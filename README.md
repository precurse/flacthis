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

Usage:

	usage: flacthis.py [-h] [-o {fdkaac,ogg,mp3,aac}] [-t THREADS] [--debug]
		           source_dir dest_dir

	positional arguments:
	  source_dir            Input (lossless) directory
	  dest_dir              Destination (lossy) directory

	optional arguments:
	  -h, --help            show this help message and exit
	  -o {fdkaac,ogg,mp3,aac}, --output_codec {fdkaac,ogg,mp3,aac}
		                Output (lossy) codec (default: mp3)
	  -t THREADS, --threads THREADS
		                Force specific number of threads (default: auto)
	  --debug               Enable debugging


Benchmarks:

	System: Intel i5-750 w/ Intel 520 120GB SSD 
	Command: Using Linux time command and flacthis -t 1,2,3,4 (lame encoder with -V 0 flags):

	3 albums (39 songs)
	Input: 1.7GB
	Output: 471.5MB

	1 Thread: 
		real	7m33.512s
		user	7m20.371s
		sys	0m8.363s

	2 Threads:
		real	4m5.559s
		user	7m37.347s
		sys	0m7.729s

	3 Threads:
		real	2m59.474s
		user	8m2.432s
		sys	0m7.150s

	4 Threads:
		real	2m20.317s
		user	8m4.628s
		sys	0m6.426s


Run, and enjoy. If any issues are encountered, feel free to contact me (andrewklaus@gmail.com).
