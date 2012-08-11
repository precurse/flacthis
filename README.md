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

USAGE:

	usage: flacthis.py [-h] [-d {fdkaac,ogg,mp3,aac}] [--debug]
		           source_dir dest_dir

	positional arguments:
	  source_dir            Source (lossless) directory
	  dest_dir              Destination (lossy) directory

	optional arguments:
	  -h, --help            show this help message and exit
	  -d {fdkaac,ogg,mp3,aac}, --dest_codec {fdkaac,ogg,mp3,aac}
		                Destination (lossy) codec
	  --debug               Enable debugging


Run, and enjoy.
