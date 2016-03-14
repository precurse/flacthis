"""
Copyright (c) 2016, Andrew Klaus <andrewklaus@gmail.com>
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
import os
import logging
import sys
import subprocess


logger = logging.getLogger(__name__)


class Codec(object):
    """
        Superclass for all encoders and decoders
        
        name is the name of the encoder (ex. FLAC, Wav, etc.)
        exe_file is the executable name that runs the codec (ex flac) 
        ext is the file extension that's used for files  (ex .flac)
        cmd_seq is the stdin/stdout command line arguments for exe_file:
            in the format like : "{exe} -c -d "{input_file}" {flags}"
        flags is the desired flags to append to the cmd_seq
        
        Must run .find_exe() to initiate the locate 
    """

    def __init__(self, name, exec_file, ext, cmd_seq, flags):
        self.name = name
        self.exec_file = exec_file
        self.ext = ext
        self.cmd_seq = cmd_seq
        self.flags = flags
        self.version = None

        self.found_exe = None

        # Append .exe if running windows
        if self._is_windows_os() \
                and self.exec_file[-4:] != ".exe":
            self.exec_file += ".exe"

    def __str__(self, *args, **kwargs):
        if self.found_exe:
            r_str = "{name} : {found_exe}".format(name=self.name, found_exe=self.found_exe)
        else:
            r_str = "{name} : Not Found".format(name=self.name)

        return r_str

    def _check_paths_for_exe(self):
        """
            Checks for the executable in the OS default path
            
            Returns string of path+exe if found.
            
        """
        logger.debug("Checking through default path for {}".format(self.exec_file))

        found_exe = None

        def_paths = [os.getcwd()]  # Check current directory FIRST

        if self._is_windows_os():
            logger.debug("Running win32 environment")
            def_paths.extend(os.environ["PATH"].split(';'))
        else:
            logger.debug("Running non-win32 environment")
            def_paths.extend(os.environ["PATH"].split(':'))

        if len(def_paths) == 0:
            raise NoDefaultPaths

        logger.debug("Checking paths: {}".format(str(def_paths)))

        # Check through default paths
        for path in def_paths:
            if self._is_exe_in_path(path):
                # Found 
                found_exe = os.path.join(path, self.exec_file)
                break

        if found_exe is not None:
            logger.debug("Found executable: {}".format(found_exe))
        else:
            logger.debug("No {} executable found".format(self.exec_file))

        return found_exe

    def _is_exe_in_path(self, path=None):
        """
            Checks if executable name is in the provided path.
            If no path provided, current working directory is checked
             
            Returns True if it is, False if not.
        """
        found = False

        if path is None:
            file_path = self.exec_file
        else:
            file_path = os.path.join(path, self.exec_file)

        if os.path.isfile(file_path):
            found = True

        return found

    def _is_exe_executable(self):

        assert self.found_exe

        executable = os.access(self.found_exe, os.X_OK)

        return executable

    @staticmethod
    def _is_windows_os():
        return sys.platform in ("win32", "cygwin")

    def _find_exe_version(self):
        """
            Must be implemented at the subclass level
        """
        pass

    def _check_exe_codec_support(self):
        """
            Must be implemented at the subclass level.
            
            Some projects don't implement certain codecs by default.
            (i.e.  ffmpeg doesn't compile libfdk-aac in by default)
            
            We need a method that will check the exe for this support
        """
        pass

    def find_exe(self):
        """
            Attempts to locate executable for codec starting with the
            current directory, then looks in the default path
            
            Raises CodecNotFound if file was not found
            Raises CodecNotExecutable if file not executable
            
        """
        logger.debug("Finding executable {}".format(self.exec_file))

        self.found_exe = self._check_paths_for_exe()

        if not self.found_exe:
            raise CodecNotFound

        if not self._is_exe_executable():
            raise CodecNotExecutable

        # Won't do anything unless subclass creates a function for it        
        self._check_exe_codec_support()
        self._find_exe_version()

    def override_codec_flags(self, flags):
        self.flags = flags


#### DECODERS ####

class FLACDecoder(Codec):
    def __init__(self,
                 name="flac",
                 exec_file="flac",
                 ext=".flac",
                 flags="",
                 cmd_seq="""{exe} -s -c -d "{input_file}" {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

    def _find_exe_version(self):
        version = subprocess.check_output([self.found_exe, "-v"])

        if len(version) > 0:
            self.version = version.strip()


class WAVDecoder(Codec):
    def __init__(self,
                 name="wav",
                 exec_file="cat",
                 ext=".wav",
                 flags="",
                 cmd_seq="""{exe} "{input_file}" {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)


# Wave file support for windows (UNTESTED)
class WINWAVDecoder(Codec):
    def __init__(self,
                 name="winwav",
                 exec_file="type.exe",
                 ext=".wav",
                 flags="",
                 cmd_seq="""{exe} "{input_file}" {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)


#### ENCODERS ####

class AACEncoder(Codec):
    def __init__(self,
                 name="aac",
                 exec_file="faac",
                 ext=".m4a",
                 flags="-q 170",
                 cmd_seq="""{exe} - -w -o "{output_file}" {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)


class AVConvLibFdkAACEncoder(Codec):
    def __init__(self,
                 name="avconv-fdkaac",
                 exec_file="avconv",
                 ext=".m4a",
                 flags="+qscale -global_quality 5 -afterburner 1",
                 cmd_seq='{exe} -i - -c:a libfdk_aac -flags {flags} "{output_file}" '):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)


class FfmpegLibFdkEncoder(Codec):
    def __init__(self,
                 name="ffmpeg-fdkaac",
                 exec_file="ffmpeg",
                 ext=".m4a",
                 flags="-vbr 3",
                 cmd_seq='{exe} -v 0 -i - -c:a libfdk_aac {flags} "{output_file}" '):
        #libfdk_aac
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

    def _check_exe_codec_support(self):
        # the -v 0 suppresses verbose output
        try:
            subprocess.check_output([self.found_exe, "-v", "0", "-encoders"])
        except subprocess.CalledProcessError:
            raise NotCompiledWithCodecSupport

    def _find_exe_version(self):
        version = subprocess.check_output([self.found_exe, "-v", "0", "-version"])

        # Lame has a lot of output.. we only want the first line
        version = version.split("\n")[0]

        if len(version) > 0:
            self.version = version.strip()


class MP3Encoder(Codec):
    def __init__(self,
                 name="mp3",
                 exec_file="lame",
                 ext=".mp3",
                 flags="-V 0",
                 cmd_seq="""{exe} - "{output_file}" --silent {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

    def _find_exe_version(self):
        version = subprocess.check_output([self.found_exe, "--version"])

        # Lame has a lot of output.. we only want the first line
        version = version.split("\n")[0]

        if len(version) > 0:
            self.version = version.strip()


class OGGEncoder(Codec):
    def __init__(self,
                 name="ogg",
                 exec_file="oggenc",
                 ext=".ogg",
                 flags="-q 6",
                 cmd_seq="""{exe} - -o "{output_file}" {flags}"""):
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

    def _find_exe_version(self):
        version = subprocess.check_output([self.found_exe, "--version"])

        if len(version) > 0:
            self.version = version.strip()


class CodecManager(object):
    """
        Manager for all supported codecs.
        
        discover_codecs() must be run before trying to select a codec
         
    """
    __decoders__ = (FLACDecoder,
                    WAVDecoder,
                    WINWAVDecoder)

    __encoders__ = (MP3Encoder,
                    OGGEncoder,
                    AACEncoder,
                    AVConvLibFdkAACEncoder,
                    FfmpegLibFdkEncoder,)

    def __init__(self):
        self._avail_decoders = []
        self._avail_encoders = []

    def discover_codecs(self):
        """
            Looks through all codecs at which are available
             to the system
        """
        for codec in self.__decoders__:
            t_obj = codec()
            try:
                t_obj.find_exe()

            except CodecNotFound:
                # Don't add to list
                logger.debug("Decoder {} not found".format(t_obj.name))
            except CodecNotExecutable:
                logger.debug("Decoder {} not executable".format(t_obj.name))
            except NotCompiledWithCodecSupport:
                logger.debug("Decoder {} not compiled with codec support".format(t_obj.name))
            else:
                self._avail_decoders.append(t_obj)

        for codec in self.__encoders__:
            t_obj = codec()
            try:
                t_obj.find_exe()

            except CodecNotFound:
                # Don't add to list
                logger.debug("Encoder {} not found".format(t_obj.name))
            except CodecNotExecutable:
                logger.debug("Encoder {} not executable".format(t_obj.name))
            except NotCompiledWithCodecSupport:
                logger.debug("Encoder {} not compiled with codec support".format(t_obj.name))
            else:
                self._avail_encoders.append(t_obj)

        if len(self._avail_decoders) < 1:
            raise NoSystemDecodersFound
        elif len(self._avail_decoders) < 1:
            raise NoSystemEncodersFound

    def get_decoder(self, codec_name):
        """
            Accepts a name of a codec, and returns codec object
        """
        decoder = None
        # Loop through list finding the name
        for d in self._avail_decoders:
            if codec_name in d.name:
                decoder = d
                break

        if decoder is None:
            raise SelectedCodecNotValid

        logger.debug("Returning {}".format(str(decoder)))
        return decoder

    def get_encoder(self, codec_name):
        """
            Accepts a name of a codec, and returns codec object
        """
        encoder = None
        # Loop through list finding the name
        for e in self._avail_encoders:
            if codec_name in e.name:
                encoder = e
                break

        if encoder is None:
            raise SelectedCodecNotValid

        logger.debug("Returning {}".format(str(encoder)))
        return encoder

    def list_all_decoders(self):
        """
            Returns list of all decoder names
            that are supported
        """
        d = []

        # Go through full list and get names
        for c in self.__decoders__:
            d.append(c().name)

        return d

    def list_all_encoders(self):
        """
            Returns list of all encoder names
            that are supported
        """
        d = []

        for c in self.__encoders__:
            d.append(c().name)

        return d

    def get_avail_decoders(self):
        """
            Returns a list of decoders available 
            to the script
        """
        r_list = []
        for d in self._avail_decoders:
            r_list.append(d.name)

        return r_list

    def get_avail_encoders(self):
        """
            Returns a list of encoders available 
            to the script
        """
        r_list = []

        for e in self._avail_encoders:
            r_list.append(e.name)

        return r_list


class SelectedCodecNotValid(Exception):
    """
        Used if a codec is selected by the user, but not available
        to the system
    """
    pass


class NoSystemDecodersFound(Exception):
    pass


class NoSystemEncodersFound(Exception):
    pass


class NoDefaultPaths(Exception):
    pass


class CodecNotFound(Exception):
    pass


class CodecNotExecutable(Exception):
    pass


class NotCompiledWithCodecSupport(Exception):
    pass


if __name__ == "__main__":
    print("This module must be imported")
