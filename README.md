flacthis
========

A multithreaded Python-based command line utility that converts lossless FLAC 
or WAV audio files to MP3s, AAC, or Ogg and preserves the directory structure.

I created this when I didn't want to use the Mono libraries needed to use
 FlacSquisher and wanted something easy to run in a cronjob.

NOTE: No files or directories will ever be deleted. Only new directories and
 files are created. The purpose of this utility is to be able to run it over
 and over again and only needing to encode new content.


Prerequisites
--------------

* MP3 encoder for MP3 support: (lame)
	+ http://sourceforge.net/projects/lame/files/lame/3.99/
	+ Windows binary: http://www.rarewares.org/files/mp3/lame3.99.5.zip

* AAC encoder for AAC support: (faac)
	+ http://sourceforge.net/projects/faac/
	+ Windows binary: http://www.rarewares.org/files/aac/faac-1.28-mod.zip

* Libav encoder for Fraunhofer AAC support: (avconv)
	+ Fraunhofer codec: http://sourceforge.net/projects/opencore-amr/files/fdk-aac/
	+ http://libav.org/download.html
		-  Libav must be compiled with "--enable-libfdk-aac" 

* Ogg encoder for Ogg support: (oggenc)
	+ http://www.vorbis.com/
	+ Windows binary: http://www.rarewares.org/files/ogg/oggenc2.87-1.3.3-generic.zip

* FLAC decoder: (flac) 
	+ http://flac.sourceforge.net/download.html
	+ Windows binary: http://www.rarewares.org/files/lossless/flac-1.2.1b.zip

* Mutagen Python library (used for tagging, but requirement can be disabled with --noid3 flag)
	+ http://code.google.com/p/mutagen/

* Python2
	+ http://www.python.org/download/

Usage
------

	usage: flacthis.py [-h] [-i {wav,flac}] [-o {fdkaac,ogg,mp3,aac}] [-t THREADS]
		           [--noid3] [--debug]
		           source_dir dest_dir

	positional arguments:
	  source_dir            Input (lossless) directory
	  dest_dir              Output (lossy) directory

	optional arguments:
	  -h, --help            show this help message and exit
	  -i {wav,flac}, --input_codec {wav,flac}
		                Input (lossless) codec (default: flac)
	  -o {fdkaac,ogg,mp3,aac}, --output_codec {fdkaac,ogg,mp3,aac}
		                Output (lossy) codec (default: mp3)
	  -t THREADS, --threads THREADS
		                Force specific number of threads (default: auto)
	  --noid3               Disable ID3 file tagging (does not require Mutagen)
	  --debug               Enable debugging




Benchmarks
-----------

	System: Intel i5-750 w/ Intel 520 120GB SSD 
	Command: Using Linux time command and flacthis -t 1,2,3,4, or 5 (lame encoder with -V 0 flags):

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
		real	2m9.415s
		user	8m3.955s
		sys	0m6.166s

	5 Threads:
		real	2m5.893s
		user	8m3.455s
		sys	0m6.090s


Run, and enjoy. If any issues are encountered, feel free to contact me (andrewklaus@gmail.com).
