#!/usr/bin/python2
'''
Copyright (c) 2012, Andrew Klaus
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
import os
import argparse
import shutil
import sys
import subprocess
import mutagen		# ID3 Tags

lossless_formats = ('flac',)	# For future use.



def main():
	source = '/flac' 
	dest = '/mp3'

	# Must remove trailing slashes
        source = source.rstrip('/')	
        dest = dest.rstrip('/')

	src_enc,dst_enc = findEncoders()

	#src_enc = '/usr/bin/flac'	# Source encoder (lossless) override
	#dst_enc = '/usr/bin/lame'	# Destination encoder (lossy) override
	lame_flags = '-V 0'

	verifyEncoders(src_enc,dst_enc)

	createDestFolderStructure(dest, source)

	all_music_files = []	# All lossless music files
	create_music_files = []	# For files needing conversion


	getLosslessMusicList(source,all_music_files)

	getLossyMusicToConvert(dest,source,all_music_files,create_music_files)

	# Need for inside loop
	count = 0 	
	failed = 0	
	failed_tag = 0

	for file in create_music_files:
		lossless_file = file
		lossy_file = translateSourceToDestFileName(dest,source,file)
		lossy_file_tmp = lossy_file + '.tmp'

		command = '{0} -c -d "{1}" | {2} - "{3}" {4}'.format \
		(src_enc,lossless_file,dst_enc,lossy_file_tmp,lame_flags)


		print 'Starting file {0} of {1}'.format(count+1,len(create_music_files))

		try:

			status = os.system(command)

			if status == 2 :
				print "\n\nCancelled by user"
				raise SystemExit
			elif status > 0:
				raise NameError('FlacConversionFailed')

			# Move .tmp after conversion
			shutil.move(lossy_file_tmp, lossy_file)

		except:
			failed += 1
		else:
			count += 1
			try:
				updateLossyTags(lossy_file,lossless_file)
			except: 
				failed_tag += 1

	printComplete(count,failed,failed_tag)

def findEncoders():

	error = ''

	# Check default path for executable
	tmp = findEncoderDefaultPath('flac')
	if tmp != -1:
		src_exec = tmp
	else:
		error += "FLAC executable not found in path\n"

	tmp = findEncoderDefaultPath('lame')
	if tmp != -1:
		dst_exec = tmp
	else:
		error += "LAME executable not found in path\n"

	if error != '':
		print error
		raise SystemExit

	return src_exec,dst_exec

def findEncoderDefaultPath(exec_name):
	def_paths = os.path.defpath.split(':')

	# Check if encoder in default path exists
	for path in def_paths:
		current = os.path.join(path,exec_name)

		if os.path.isfile(current):
			return current

	# Not found if reached here
	return -1

def verifyEncoders(src_enc,dst_enc):

	error = ''

	if os.path.isfile(src_enc) is False:
		error += "FLAC executable not found\n"
	elif os.access(src_enc,os.X_OK) is False:
		error += "FLAC executable not executable\n"

	if os.path.isfile(dst_enc) is False:
		error += "LAME executable not found\n"
	elif os.access(dst_enc,os.X_OK) is False:
		error += "LAME executable not executable\n"

	if error != '':
		print error
		raise SystemExit


def getLosslessMusicList(source,dest_list):
	for dirpath, dirnames, filenames in os.walk(source):
		for filename in filenames:
			if os.path.splitext(filename)[1][1:] in lossless_formats:
				dest_list.append(os.path.join(dirpath,filename))

def getLossyMusicToConvert(dest,source,src_list,dest_list):
	for file in src_list:
		if doesLossyFileExist(dest, source, file) == False:
			# Lossy song does not exist
			dest_list.append(file)


def updateLossyTags(lossy_file,lossless_file):

	lossless_tags = mutagen.File(lossless_file, easy=True)
	lossy_tags = mutagen.File(lossy_file, easy=True)

	for k in lossless_tags:
		if k in ('album','artist','title','performer','tracknumber','date','genre',):
			lossy_tags[k] = lossless_tags[k]

	lossy_tags.save()


def createDestFolderStructure(dest_dir, source_dir):
	# Try to create every folder needed and catch any exceptions (directory already created)
	# This avoids any directory creation race conditions

	for dirpath, dirnames, filenames  in os.walk(source_dir):
		try:
			os.makedirs(os.path.join(dest_dir,dirpath[1+len(source_dir):]))
		except:
			pass	



def doesLossyFileExist(dest_dir, source_dir, source_file_path):
	# Dest with .lossless extension
	#dest = os.path.join(dest_dir, source_file_path[1+len(source):])
	dest = translateSourceToDestFileName(dest_dir, source_dir, source_file_path)
	# Remove ext and add .mp3 extension
	dest = os.path.splitext(dest)[0] + '.mp3'

	return  os.path.exists(dest)

def translateSourceToDestFileName(dest_dir, source_dir, source_file_path):
	# Remove "src_path" from path
	dest = os.path.join(dest_dir, source_file_path[1+len(source_dir):])

	# Add mp3 extension
	dest = os.path.splitext(dest)[0] + '.mp3'

	return dest

def printComplete(count,failed,failed_id3):
	output = ''

	if failed > 0:
		output += '{} songs failed to convert\n'.format(failed)

	if failed_id3 > 0:
		output += '{} id3 tags failed to write\n'.format(failed_id3)	

	if count > 0:
		output += '{} songs successfully converted'.format(count)
	else:
		output += 'No songs converted'

	print output

if __name__ == "__main__": 
	sys.exit(main())

