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
import time
#import argparse
import shutil
import sys
#import subprocess
import mutagen              # ID3 Tags
import threading
import multiprocessing      # for cpu count

lossless_formats = ('flac',)    # For future use.

lame_flags = '-V 0'


# Results

success = 0     # Successful conversions
error_conv = []  # List of error conversions
error_id3 = []  # List of error id3 tags


def main():
    source = '/FLAC' 
    dest = '/MP3'

    # Must remove trailing slashes
    source = source.rstrip('/')    
    dest = dest.rstrip('/')

    src_enc,dst_enc = findEncoders()

    #src_enc = '/usr/bin/flac'    # Source encoder (lossless) override
    #dst_enc = '/usr/bin/lame'    # Destination encoder (lossy) override

    verifyEncoders(src_enc,dst_enc)

    max_cpus = multiprocessing.cpu_count()

    createDestFolderStructure(dest, source)

    all_music_files = []    # All lossless music files
    create_music_files = []    # For files needing conversion


    getLosslessMusicList(source,all_music_files)

    getLossyMusicToConvert(dest,source,all_music_files,create_music_files)


    
    # As long as we have entries in the list to convert..
    while len(create_music_files) > 0:
        
        # Get file from list and remove
        lossless_file = create_music_files.pop()
        
        lossy_file = translateSourceToDestFileName(dest,source,lossless_file)
        
        t = threading.Thread(target=doEncodeAndTagging, \
                             args=(lossless_file,lossy_file,src_enc,dst_enc))
    
        t.start()
     
        # Ensure that there's always <= max_cpu threads running
        while getNumberOfRunningThreads() >= max_cpus: 
            time.sleep(3)
            
            

    # Wait for threads to complete
    main_thread = threading.current_thread()
    
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()

    printComplete()


def doEncodeAndTagging(lossless_file,lossy_file,src_enc,dst_enc):

    conv_result = doConvertToLossyFile(lossless_file,lossy_file,src_enc,dst_enc)

    # Only ID3 tag if conversion successful
    if conv_result == 0:
        doUpdateLossyTags(lossy_file,lossless_file)
        
        
def getNumberOfRunningThreads():
    main_thread = threading.currentThread()
    
    count = 0
    
    # Count all threads except the main thread
    for t in threading.enumerate():
        if t is main_thread:
            continue
        count += 1
        
    return count

def findEncoders():
    """ Finds all needed encoders on the system."""

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
        print(error)
        raise SystemExit

    return src_exec,dst_exec

def convertToLossyFile(lossless_file,lossy_file,src_enc,dst_enc):
    
    lossy_file_tmp = lossy_file + '.tmp'
    
    command = '{0} -c -d "{1}" | {2} - "{3}" {4}'.format \
    (src_enc,lossless_file,dst_enc,lossy_file_tmp,lame_flags)
    

    
    #print 'Starting file {0} of {1}'.format(count+1,len(create_music_files))
    
    status = os.system(command)

    if status == 2 :
        print("\n\nCancelled by user")
        raise SystemExit
    elif status > 0:
        raise NameError('FlacConversionFailed')

    # Move .tmp after conversion
    shutil.move(lossy_file_tmp, lossy_file)



def doConvertToLossyFile(lossless_file,lossy_file,src_enc,dst_enc):
    global success
    
    try:
        convertToLossyFile(lossless_file,lossy_file,src_enc,dst_enc)
    
    except:
        
        #l_error_conv.acquire()
        error_conv.append(lossless_file)
        #l_error_conv.release()
        
        return 1
    
    else:
        
        #l_success.acquire()
        success += 1
        #l_success.release()
        
        return 0
        

def findEncoderDefaultPath(exec_name):
    """ Searches the default path for a specific named encoder """

    def_paths = os.path.defpath.split(':')

    # Check if encoder in default path exists
    for path in def_paths:
        current = os.path.join(path,exec_name)

        if os.path.isfile(current):
            # Return first instance if encoder found
            return current

    # Encoder not found if reached here
    return -1

def verifyEncoders(src_enc,dst_enc):
    """ Verifies source and destination encoders exist and are executable. 
        Exits if either is not true."""

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
        print(error)
        raise SystemExit


def getLosslessMusicList(source,dest_list):
    """Gets list of ALL lossless music in source directory and
    places it in a list."""

    for dirpath, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if os.path.splitext(filename)[1][1:] in lossless_formats:
                dest_list.append(os.path.join(dirpath,filename))

def getLossyMusicToConvert(dest,source,src_list,dest_list):
    """Compares list of all lossless music to what lossy music currently exists
        and adds non-existent files to another list."""

    for file in src_list:
        if doesLossyFileExist(dest, source, file) == False:
            # Lossy song does not exist
            dest_list.append(file)


def updateLossyTags(lossy_file,lossless_file):
    """ Copies ID3 tags from lossless file to lossy file. """
    
    lossless_tags = mutagen.File(lossless_file, easy=True)
    lossy_tags = mutagen.File(lossy_file, easy=True)

    for k in lossless_tags:
        if k in ('album','artist','title','performer','tracknumber','date','genre',):
            lossy_tags[k] = lossless_tags[k]

    lossy_tags.save()


def doUpdateLossyTags(lossy_file,lossless_file):
    
    try:
        
        updateLossyTags(lossy_file,lossless_file)
        
    except:
        #l_error_id3.acquire()
        error_id3.append(lossy_file)
        #l_error_id3.release()
    

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

def printComplete():
    output = ''

    count_failed_conv = len(error_conv)
    count_failed_id3 = len(error_id3)



    if count_failed_conv > 0:
        output += '{} songs failed to convert\n'.format(count_failed_conv)

    if count_failed_id3 > 0:
        output += '{} id3 tags failed to write\n'.format(count_failed_id3)    

    if success > 0:
        output += '{} songs successfully converted'.format(success)
    else:
        output += 'No songs converted'

    print(output)

if __name__ == "__main__": 
    sys.exit(main())
