#!/usr/bin/env python
"""
Copyright (c) 2017, Andrew Klaus <andrewklaus@gmail.com>
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


"""

__version__ = '1.4-head'
__author__ = 'Andrew Klaus'
__author_email__ = 'andrewklaus@gmail.com'
__copyright__ = '2017'

import os
import time
import shutil
import shlex
import sys
import subprocess
import threading
import multiprocessing  # for cpu count
import argparse

try:
    import mutagen  # ID3 Tags, Imported if selected from command line
except ImportError:
    pass
import audio_codecs
import logging

class ConverterConfig(object):
    def __init__(self):
        self.logger = logging.getLogger("config")
        self._dest_dir = None
        self._source_dir = None
        self.encoder = None
        self.decoder = None
        self._threads = None
        self.no_artwork = False
        self.disable_id3 = False
        self.debug = False

    @property
    def dest_dir(self):
        return self._dest_dir

    @dest_dir.setter
    def dest_dir(self, dir):
        # Remove trailing slashes from path
        self._dest_dir = dir.rstrip('/')

    @property
    def source_dir(self):
        return self._source_dir

    @source_dir.setter
    def source_dir(self, dir):
        # Remove trailing slashes from path
        d = dir.rstrip('/')
        # Verify source directory exists and readable
        if not os.path.isdir(d):
            raise IOError('Source directory not found')
        if not os.access(d, os.R_OK):
            raise OSError('Source directory not readable')

        self._source_dir = d

    @property
    def threads(self):
        return self._threads

    @threads.setter
    def threads(self, t):
        if t == 0:
            cpu = multiprocessing.cpu_count()
            self.logger.debug("Setting cpu count to {}".format(cpu))
            self._threads = cpu
        else:
            self.logger.debug("Setting CPU count to {}".format(t))
            self._threads = t

    def __str__(self):
        return """Source Directory: {}
                    Dest Directory: {}
                    Decoder: {}
                    Encoder: {}
                    Threads: {}
                    Skip artwork: {}
                    Disable ID3 tags: {}
                """.format(self.source_dir,
                           self.dest_dir,
                           str(self.decoder),
                           str(self.encoder),
                           self.threads,
                           self.no_artwork,
                           self.disable_id3)

class LosslessToLossyConverter(object):
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("audio_converter")

        assert (config.decoder.found_exe)
        assert (config.encoder.found_exe)

        self.source_dir = config.source_dir
        self.dest_dir = config.dest_dir


        self.Decoder = config.decoder
        self.Encoder = config.encoder
        self.threads = config.threads

        self.to_convert = []    # Music to convert
        self.to_copy = []       # Artwork to copy

        self.success = 0        # Successful conversions
        self.error_conv = []    # List of error conversions
        self.error_id3 = []     # List of error id3 tags

        self.disable_id3 = config.disable_id3
        self.no_artwork = config.no_artwork
        self.artwork_ext = ['jpg','JPG','jpeg','JPEG','bmp','BMP']
        self.debug = config.debug

    def get_convert_list(self):
        """Populates list with files needing conversion."""

        self.logger.debug('Get convert list starting')
        try:
            for dirpath, dirnames, filenames in os.walk(self.source_dir):
                # Flag to create directory after all files checked
                found_file = False

                for filename in filenames:

                    # Find artwork
                    if not self.no_artwork and \
                      os.path.splitext(filename)[1][1:] in self.artwork_ext:
                        self.logger.debug("Found artwork file: {}".format(\
                                                      os.path.join(dirpath, filename)))
                        f_path_src = os.path.join(dirpath, filename)

                        f_path_dest = os.path.normpath(self.dest_dir + \
                                              f_path_src[len(self.source_dir):])

                        # Check if file already exists on dest
                        try:
                            f_exists = os.path.isfile(f_path_dest)
                        except OSError as e:
                            self.logger.exception(e)

                        if not f_exists:
                            self.logger.debug("Artwork file {} doesn't exist at dest".format(f_path_src))
                            found_file = True
                            self.to_copy.append(f_path_src)

                    # Find files to convert
                    if os.path.splitext(filename)[1] in self.Decoder.ext \
                            and os.path.splitext(filename)[1] != '':
                        # self.logger.debug('filename extension: ' + os.path.splitext(filename)[1])
                        # self.logger.debug('comparing extension: ' + self.source_ext)
                        if not self.does_lossy_file_exist(os.path.join(dirpath, filename)):
                            self.logger.debug('***Adding to_convert: ' + os.path.join(dirpath, filename))
                            # Lossy song does not exist
                            self.to_convert.append(os.path.join(dirpath, filename))

                            found_file = True

                if found_file:
                    # Create destination directory
                    d = os.path.normpath(self.dest_dir + dirpath[len(self.source_dir):])
                    self.logger.debug("Creating directory {}".format(d))
                    try:
                        os.makedirs(d)
                    except OSError as e:
                        if e.errno == os.errno.EEXIST:
                            # Ignore file already exists exception
                            pass

        except Exception as ex:
            self.logger.exception('Something happened in get_convert_list')
            raise SystemExit

    def copy_artwork(self):
        """ Copy artwork to destination directory """
        assert(not self.no_artwork)
        for c in self.to_copy:
            d = os.path.normpath(self.dest_dir + c[len(self.source_dir):])
            self.logger.debug("Copying {} to {}".format(c, d))
            shutil.copy2(c, d)

    def translate_src_to_dest(self, lossless_file_path):
        """Provides translation between the source file and destination file"""

        # Remove "src_path" from path
        self.logger.debug('translate got: ' + lossless_file_path)
        self.logger.debug("Dest_dir: {}".format(self.dest_dir))
        self.logger.debug("{}".format(lossless_file_path[len(self.source_dir):]))
        dest = os.path.normpath(self.dest_dir + lossless_file_path[len(self.source_dir):])

        # Add extension
        dest = os.path.splitext(dest)[0] + self.Encoder.ext
        self.logger.debug('translate changed dest to: ' + dest)

        return dest

    def does_lossy_file_exist(self, source_file_path):
        """ Checks if .lossless -> .lossy file already exists """
        # self.logger.debug('does_lossy_file_exist received: '+ source_file_path)
        dest = self.translate_src_to_dest(source_file_path)

        # Remove ext and add .mp3 extension
        dest = os.path.splitext(dest)[0] + self.Encoder.ext

        # self.logger.debug('does_lossy_file_exist dest: '+ dest)
        return os.path.exists(dest)

    def get_running_thread_count(self):
        """Returns number of non-main Python threads"""

        main_thread = threading.currentThread()

        count = 0

        # Count all threads except the main thread
        for t in threading.enumerate():
            if t is main_thread:
                continue
            count += 1

        return count

    def encode_and_tagging(self, lossless_file, lossy_file):
        self.logger.debug('Starting encode_and_tagging. Received: ' + ' ' + lossless_file + ' ' + lossy_file)

        conv_result = self.convert_to_lossy(lossless_file, lossy_file)

        # Only ID3 tag if conversion successful and if not disabled
        if conv_result == 0 and not self.disable_id3:
            self.update_lossy_tags(lossless_file, lossy_file)

    def convert_to_lossy(self, lossless_file, lossy_file):

        try:
            # avconv complains when .m4a.tmp files are used as output.
            # Therefore we need to make extension: .tmp.m4a
            # lossy_file_tmp = lossy_file + '.tmp'
            lossy_file_tmp = os.path.splitext(lossy_file)[0] + '.tmp' + self.Encoder.ext

            exe = self.Decoder.found_exe
            input_file = lossless_file
            flags = self.Decoder.flags

            source_cmd = self.Decoder.cmd_seq.format(
                exe=exe,
                input_file=input_file,
                flags=flags)

            self.logger.debug('INPUT command: ' + source_cmd)

            exe = self.Encoder.found_exe
            output_file = lossy_file_tmp
            flags = self.Encoder.flags

            dest_cmd = self.Encoder.cmd_seq.format(
                exe=exe,
                output_file=output_file,
                flags=flags)

            self.logger.debug('OUTPUT command: ' + dest_cmd)

            src_args = shlex.split(source_cmd)
            dest_args = shlex.split(dest_cmd)

            p1 = subprocess.Popen(src_args, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(dest_args, stdin=p1.stdout)

            output = p2.communicate()[0]

            self.logger.debug('Encode output: ' + str(output))

            # Move .tmp after conversion
            shutil.move(lossy_file_tmp, lossy_file)

        except Exception as ex:
            self.logger.exception('Could not encode')
            self.error_conv.append(lossless_file)

            return 1

        else:

            self.success += 1

            return 0

    def update_lossy_tags(self, lossless_file, lossy_file):
        """ Copies ID3 tags from lossless file to lossy file. """
        try:
            lossless_tags = mutagen.File(lossless_file, easy=True)
            lossy_tags = mutagen.File(lossy_file, easy=True)

            for k in lossless_tags:
                if k in ('album', 'artist', 'title', 'performer', 'tracknumber', 'date', 'genre',):
                    lossy_tags[k] = lossless_tags[k]

            lossy_tags.save()
        except Exception as e:
            self.logger.exception(e)
            self.error_id3.append(lossy_file)

    def print_results(self):
        """ Print a final summary of successful and/or failed conversions"""
        output = ''

        count_failed_conv = len(self.error_conv)
        count_failed_id3 = len(self.error_id3)

        if count_failed_conv > 0:
            output += '{} song(s) failed to convert:\n'.format(count_failed_conv)

            for s in self.error_conv:
                output += '{}\n'.format(s)
        else:
            output += '0 conversion errors\n'

        if count_failed_id3 > 0:
            output += '{} ID3 tag(s) failed to write\n'.format(count_failed_id3)

            for s in self.error_id3:
                output += '{}\n'.format(s)
        else:
            output += '0 ID3 tag errors\n'

        if self.success > 0:
            output += '{} song(s) successfully converted'.format(self.success)
        else:
            output += '0 songs converted'

        print(output)

    def start(self):
        """
            Start the full conversion process
        """

        self.logger.debug('Starting Conversion')

        self.get_convert_list()

        self.logger.debug('Number of items in convert list: ' + str(len(self.to_convert)))

        if not self.no_artwork:
            self.logger.debug('Copying artwork')
            self.copy_artwork()

        # Start Threaded Converting
        while len(self.to_convert) > 0:

            # Get file from list and remove
            lossless_file = self.to_convert.pop()
            lossy_file = self.translate_src_to_dest(lossless_file)

            t = threading.Thread(target=self.encode_and_tagging, args=(lossless_file, lossy_file))

            t.start()

            # Don't allow more than max_cpu threads to run
            while self.get_running_thread_count() >= self.threads:
                # Check every second if more threads are needed
                time.sleep(1)
                # Wait for threads to complete
        main_thread = threading.current_thread()

        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()


def setup_parsing(decoders, encoders):
    parser = argparse.ArgumentParser()
    parser.add_argument('source_dir',
                        help='Input (lossless) directory')
    parser.add_argument('dest_dir',
                        help='Output (lossy) directory')
    parser.add_argument('-i',
                        '--input_codec',
                        default='flac',
                        choices=decoders,
                        help='Input (lossless) codec (default: flac)')
    parser.add_argument('-o',
                        '--output_codec',
                        default='mp3',
                        choices=encoders,
                        help='Output (lossy) codec (default: mp3)')
    parser.add_argument('-t',
                        '--threads',
                        type=int,
                        default=0,
                        help='Force specific number of threads (default: auto)')
    parser.add_argument('--noid3',
                        action='store_true',
                        default=False,
                        help='Disable ID3 file tagging (remove requirement for Mutagen)')
    parser.add_argument('--noartwork',
                        action='store_true',
                        help='Disable copy of artwork (default: false)')
    parser.add_argument('--debug',
                        help='Enable debugging',
                        action='store_true')

    return parser


def setup_logging(debug=False):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("main")

    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger.setLevel(level)
    logging.getLogger("audio_codecs").setLevel(level)
    logging.getLogger("audio_converter").setLevel(level)
    logging.getLogger("config").setLevel(level)

    return logger


def main(import_args):
    print("flacthis {version} Copyright (c) {copyright} {author} ({email})\n"
          .format(version=__version__, copyright=__copyright__, author=__author__, email=__author_email__))

    try:
        CodecMgr = audio_codecs.CodecManager()
    except Exception as ex:
        sys.exit('An unknown error has occurred: {}'.format(str(ex)))

    config = ConverterConfig()

    decoders = CodecMgr.list_all_decoders()
    encoders = CodecMgr.list_all_encoders()

    if __name__ == "__main__":  # test if user using from CLI
        args = setup_parsing(decoders, encoders).parse_args()
    else:  # user imported module, use given args
        args = setup_parsing(decoders, encoders).parse_args(import_args)

    logger = setup_logging(args.debug)
    logger.debug('Arguments: ' + str(args))

    config.source_dir = args.source_dir
    config.dest_dir = args.dest_dir
    config.threads = args.threads
    config.no_artwork = args.noartwork

    try:
        CodecMgr.discover_codecs()
    except audio_codecs.NoSystemDecodersFound:
        sys.exit("Please install a valid decoder before running")
    except audio_codecs.NoSystemEncodersFound:
        sys.exit("Please install a valid encoder before running")

    # Setup codecs
    try:
        config.decoder = CodecMgr.get_decoder(args.input_codec)
        print("Using Decoder version: {}".format(config.decoder.version))
    except audio_codecs.SelectedCodecNotValid as e:
        # This should never trigger as parser will force a valid codec
        raise audio_codecs.SelectedCodecNotValid('{} decoder not available'.format(args.input_codec))

    try:
        config.encoder = CodecMgr.get_encoder(args.output_codec)
        print("Using Encoder version: {}".format(config.encoder.version))
    except audio_codecs.SelectedCodecNotValid as e:
        # This should never trigger as parser will force a valid codec
        raise audio_codecs.SelectedCodecNotValid('{} encoder not available'.format(args.output_codec))

    config.disable_id3 = args.noid3
    if not config.disable_id3:
        try:
            import mutagen
        except ImportError:
            sys.exit("""You require the Mutagen Python module
                    install it from http://code.google.com/p/mutagen/""")

    logger.debug(config)
    converter = LosslessToLossyConverter(config)
    converter.start()
    converter.print_results()

    return 0


if __name__ == "__main__":
    sys.exit(main(0))

