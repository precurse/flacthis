flacthis
========

A multithreaded Python-based command line utility that converts lossless FLAC 
audio files to MP3s, AAC, or Ogg and preserves the directory structure.

NOTE: No files or directories will ever be deleted. Only new directories and
 files are created. The purpose of this utility is to be able to run it over
 and over again and only needing to encode new content.

I created this when I didn't want to use the Mono libraries needed to use
 FlacSquisher and wanted something easy to run in a cronjob.


Prerequisites:

	- MP3 encoder: [lame] (for MP3 support)

	- AAC encoder: [faac] (for AAC support)

	- Libavc encoder: [avconv] (for Fraunhofer AAC support)

	- Ogg encoder: [oggenc] (for Ogg support)

	- FLAC decoder: [flac] 

	- Mutagen Python library (used for tagging)

	- Python2

HOW-TO USE:
	Currently source and destination directories must be hardcoded in the Python source file. Once arguments are
accepted, this will no longer be required. 

	(for now) To change the destination encoding, change the Converter line under main() to the following:

	MP3 (default):
	    Converter = LosslessToLossyConverter(source_dir,dest_dir, \
	                                         'flac','mp3')
	AAC:
	    Converter = LosslessToLossyConverter(source_dir,dest_dir, \
        	                                 'flac','aac')

        Fraunhofer AAC:
            Converter = LosslessToLossyConverter(source_dir,dest_dir, \
                                                 'flac','fdkaac')

	Ogg Vorbis:
	    Converter = LosslessToLossyConverter(source_dir,dest_dir, \
                	                         'flac','ogg')

Run, and enjoy.
