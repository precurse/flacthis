flacthis
========

A multithreaded Python-based command line utility that converts lossless FLAC 
audio files to MP3s, AAC, or Ogg and preserves the directory structure.

I created this when I didn't want to use the Mono libraries needed to use
 FlacSquisher and wanted something easy to run in a cronjob.

NOTE: No files or directories will ever be deleted. Only new directories and
 files are created. The purpose of this utility is to be able to run it over
 and over again and only needing to encode new content.


Prerequisites:

	- MP3 encoder: [lame] (for MP3 support)
		- http://sourceforge.net/projects/lame/files/lame/3.99/

	- AAC encoder: [faac] (for AAC support)
		- http://sourceforge.net/projects/faac/

	- Libav encoder: [avconv] (for Fraunhofer AAC support)
		- Fraunhofer codec: http://sourceforge.net/projects/opencore-amr/files/fdk-aac/
		- http://libav.org/download.html
		- ** Libav must be compiled with "--enable-libfdk-aac" 

	- Ogg encoder: [oggenc] (for Ogg support)
		- http://www.vorbis.com/

	- FLAC decoder: [flac] 
		- http://flac.sourceforge.net/download.html

	- Mutagen Python library (used for tagging)
		- http://code.google.com/p/mutagen/

	- Python2
		- http://www.python.org/download/

USAGE:

	usage: flacthis.py [-h] [-o {fdkaac,ogg,mp3,aac}] [--debug]
		           source_dir dest_dir

	positional arguments:
	  source_dir            Input (lossless) directory
	  dest_dir              Destination (lossy) directory

	optional arguments:
	  -h, --help            show this help message and exit
	  -o {fdkaac,ogg,mp3,aac}, --output_codec {fdkaac,ogg,mp3,aac}
		                Output (lossy) codec (default: mp3)
	  --debug               Enable debugging



Run, and enjoy. If any issues are encountered, feel free to contact me (andrewklaus@gmail.com).
