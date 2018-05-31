flacthis
========

[![Build Status](https://travis-ci.org/precurse/flacthis.svg?branch=master)](https://travis-ci.org/precurse/flacthis)


A multithreaded and multi-platform, BSD-licensed, Python-based command line utility that converts
lossless FLAC or WAV audio files to MP3s, AAC, or Ogg and preserves the directory structure.

I created this when I didn't want to use the Mono libraries needed to use
 other alternatives and wanted something easy to run in a cronjob.

This has been designed to be as modular as possible. Any type of codec that supports
 writing to/from stdin/out can be added with minimal effort. I've supported the majority
 of mainstream codecs, but if there are others you want added, please email me!

NOTE: No files or directories will ever be deleted. Only new directories and
 files are created. The purpose of this utility is to be able to run it on a regular
 basis and only needing to encode new content.

Installation
------
Install `flacthis` from [Github](http://www.github.com) using git:

    git clone https://github.com/precurse/flacthis.git

Install module requirements using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

    pip install -r requirements.txt

    or

    pipenv install

Need pip? Try installing it by running the following from the command
line:

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python


Command Line Usage
------

    usage: flacthis.py [-h] [-i {flac,wav,winwav}]
                       [-o {mp3,ogg,aac,fdkaac,avconv-fdkaac,ffmpeg-fdkaac}]
                       [-t THREADS] [--noid3] [--noartwork] [--noop] [--debug]
                       source_dir dest_dir

    positional arguments:
      source_dir            Input (lossless) directory
      dest_dir              Output (lossy) directory

    optional arguments:
      -h, --help            show this help message and exit
      -i {flac,wav,winwav}, --input_codec {flac,wav,winwav}
                            Input (lossless) codec (default: flac)
      -o {mp3,ogg,aac,fdkaac,avconv-fdkaac,ffmpeg-fdkaac}, --output_codec {mp3,ogg,aac,fdkaac,avconv-fdkaac,ffmpeg-fdkaac}
                            Output (lossy) codec (default: mp3)
      -t THREADS, --threads THREADS
                            Force specific number of threads (default: auto)
      --noid3               Disable ID3 file tagging (remove requirement for
                            Mutagen)
      --noartwork           Disable copy of artwork (default: copy artwork)
      --noop                Don't write files. Only show files that will be
                            (default: write files)
      --debug               Enable debugging


Module Import Usage
------
When importing `flacthis` as a module into your existing codebase the module requires, at minimum, the
source and destination directories.  You can pass these directly to the constructor (see the code below).

```python
import flacthis

ft = flacthis.main(['source_dir', 'dest_dir'])
```

If you wish to use optional arguments like `--input-codec`, you must maintain the positional directory arguments as
shown below:

```python
import flacthis

ft = flacthis.main(['i', 'flac', 'o', 'mp3', '--debug', 'source_dir', 'dest_dir'])
```

Supported Codecs
--------------

  Codec:  (Command used)
* FLAC decoder: (flac)

* WAV decoder: ('cat' in *nix and 'type' in Windows)

* MP3 encoder: (lame)

* AAC encoder: (faac)

* FDKAAC encoder: (fdkaac)

* ffmpeg or libav encoder for Fraunhofer AAC support: (ffmpeg or avconv)
    + Fraunhofer codec: http://sourceforge.net/projects/opencore-amr/files/fdk-aac/
    + Both must be compiled with "--enable-libfdk-aac".

* Ogg encoder: (oggenc)

Most of these can be downloaded easily from rarewares.org on Windows, or installed from
 your friendly neighbourhood package manager (Linux, BSD).

Requirements
-------------

* Python (automated tests run on 2.6, 2.7, 3.5, and 3.6)

* A supported decoder from above list

* A supported encoder from above list

* Mutagen Python Library (Optional, but highly recommended)
    + Used for ID3 tagging, but requirement can be disabled with --noid3 flag
    + https://bitbucket.org/lazka/mutagen

Running Tests
-------------

Ensure you have flac, lame, fdkaac, and oggenc installed before running tests:

```sh
pip install -r dev_requirements.txt

make test

or

make test3 # python3

or

py.test tests/test_flacthis.py
```

Benchmarks
-----------

    System: Intel i5-750 w/ Intel 520 120GB SSD
    Command: Using Linux time command and flacthis -t 1,2,3,4, or 5 (lame encoder with -V 0 flags):

    3 albums (39 songs)
    Input: 1.7GB
    Output: 471.5MB

    1 Thread:
        real    7m33.512s
        user    7m20.371s
        sys    0m8.363s

    2 Threads:
        real    4m5.559s
        user    7m37.347s
        sys    0m7.729s

    3 Threads:
        real    2m59.474s
        user    8m2.432s
        sys    0m7.150s

    4 Threads:
        real    2m9.415s
        user    8m3.955s
        sys    0m6.166s

    5 Threads:
        real    2m5.893s
        user    8m3.455s
        sys    0m6.090s


Run, and enjoy. If any issues are encountered, please contact me at andrewklaus@gmail.com.
