flacthis
========

A multithreaded Python-based command line utility that converts lossless FLAC
 audio files to MP3s or Ogg and preserves the directory structure.

NOTE: No files or directories will ever be deleted. Only new directories and
 files are created.

I created this when I didn't want to use the Mono libraries needed to use
 FlacSquisher and wanted something easy to run in a cronjob.


Prerequisites:

	- LAME encoder(for MP3 support)

	- Oggenc encoder (for Ogg support)

	- FLAC

	- Mutagen Python library (used for tagging)

	- Python2

HOW-TO USE:
	Currently source and destination directories must be hardcoded in the Python source file.

Run, and enjoy.
