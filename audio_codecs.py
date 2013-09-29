#!/usr/bin/python2
'''
Copyright (c) 2013, Andrew Klaus <andrewklaus@gmail.com>
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
import logging
import sys

class Codec(object):
    """
        Superclass for all encoders and decoders
        
        name is the name of the encoder (ex. FLAC, Wav, etc.)
        exe_file is the executable name that runs the codec 
        ext is the file extension that's used for files
        cmd_seq is the stdin/stdout command line arguments for exe_file
        flags is the desired flags to append to the cmd_seq
        
        Must run .find_exe() to initiate the locate 
    """
    def __init__(self, name, exec_file, ext, cmd_seq, flags):
        self.name = name
        self.exec_file = exec_file
        self.ext = ext
        self.cmd_seq = cmd_seq
        self.flags = flags
        
        self.found_exe = None   # Exe path + name if found


    def set_flags(self,flags):
        self.flags = flags

    def __str__(self, *args, **kwargs):
        if self.found_exe:
            r_str = "{name} : {found_exe}".format(name=self.name,found_exe=self.found_exe)
        else:
            r_str = "{name} : Not Found".format(name=self.name) 
        
        return r_str

    
    def _check_paths_for_exe(self):
        """
            Checks for the executable in the OS default path
            
            Returns string of path+exe if found.
            
        """
        logging.debug("Checking through default path for {}".format(self.exec_file))
        
        found_exe = None
        
        def_paths = []
        
        def_paths.append(os.getcwd())   # Check current directory FIRST
        
        if sys.platform == 'win32':
            logging.debug("Running win32 environment")
            def_paths.extend(os.environ["PATH"].split(';'))
        else:
            logging.debug("Running non-win32 environment")
            def_paths.extend(os.environ["PATH"].split(':'))

        if len(def_paths) == 0:
            raise NoDefaultPaths
           
        logging.debug("Checking paths: {}".format(str(def_paths)))
        
        # Check through default paths
        for path in def_paths:
            if self._is_exe_in_path(path):
                # Found 
                found_exe = os.path.join(path,self.exec_file)
                break
        
        if found_exe is not None:
            logging.debug("Found exe: {}".format(found_exe))
        else:
            logging.debug("No {} exe found".format(self.exec_file))
            
        return found_exe
            

    def _is_exe_in_path(self,path=None):
        """
            Checks if executable name is in the provided path.
            If no path provided, currect working directory is checked
             
            Returns True if it is, False if not.
        """
        found = False
        
        if path is None:
            file_path = self.exec_file
        else:
            file_path = os.path.join(path,self.exec_file)
        
        if os.path.isfile(file_path):
            found = True
        
        return found

    def _is_exe_executable(self):
        
        assert(self.found_exe)
        
        executable = os.access(self.found_exe,os.X_OK)

        return executable 
                    
    def _get_exe_version(self):
        assert(self.found_exe)
        
        version = 'Not implemented yet'
        
        return version

    def find_exe(self):
        """
            Attempts to locate executable for codec starting with the
            current directory, then looks in the default path
            
            Raises CodecNotFound if was not found
            Raises CodecNotExecutable if not executable
            
        """
        logging.debug("Finding exe {}".format(self.exec_file))
        
        self.found_exe = self._check_paths_for_exe()
        
        if not self.found_exe:
            raise CodecNotFound
        
        if not self._is_exe_executable():
            raise CodecNotExecutable


class FLACDecoder(Codec):
    def __init__(self,
                 name="flac",
                 exec_file="flac",
                 ext=".flac",
                 flags="",
                 cmd_seq = """{exe} -c -d "{input_file}" {flags}"""):

        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)
        
class WAVDecoder(Codec):
    def __init__(self,
                 name="wav",
                 exec_file="cat",
                 ext=".wav",
                 flags="",
                 cmd_seq = """{exe} "{input_file}" {flags}"""):

        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)
        
class AACEncoder(Codec):
    def __init__(self,
                 name="aac",
                 exec_file="faac",
                 ext=".m4a",
                 flags="-q 170",
                 cmd_seq = """{exe} - -w -o "{output_file}" {flags}"""):
        
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

class FDKAACEncoder(Codec):
    def __init__(self,
                 name="fdkaac",
                 exec_file="avconv",
                 ext=".m4a",
                 flags="+qscale -global_quality 5 -afterburner 1",
                 cmd_seq = """{exe} -i - -c:a libfdk_aac -flags {flags} "{output_file}" """):
        
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)

class MP3Encoder(Codec):
    def __init__(self,
                 name="mp3",
                 exec_file="lame",
                 ext=".mp3",
                 flags="-V 0",
                 cmd_seq = """{exe} - "{output_file}" {flags}"""):
        
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)
        
class OGGEncoder(Codec):
    def __init__(self,
                 name="ogg",
                 exec_file="oggenc",
                 ext=".ogg",
                 flags="-q 6",
                 cmd_seq = """{exe} - -o "{output_file}" {flags}"""):
        
        Codec.__init__(self, name, exec_file, ext, cmd_seq, flags)



class CodecManager(object):
    __decoders__ = (FLACDecoder,
                    WAVDecoder)
    
    __encoders__ = (MP3Encoder,
                    OGGEncoder,
                    AACEncoder,
                    FDKAACEncoder)
    
    def __init__(self):
        self._avail_decoders = []
        self._avail_encoders = []
        
        # Add all valid decoders and encoders to list
        self._discover_codecs()
    
    def _discover_codecs(self):
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
                logging.debug("Decoder {} not found".format(t_obj.name))
            except CodecNotExecutable:
                logging.debug("Decoder {} not executable".format(t_obj.name))
            else:
                self._avail_decoders.append(t_obj)
        
        for codec in self.__encoders__:
            t_obj = codec()
            try:
                t_obj.find_exe()
                
            except CodecNotFound:
                # Don't add to list
                logging.debug("Encoder {} not found".format(t_obj.name))
            except CodecNotExecutable:
                logging.debug("Encoder {} not executable".format(t_obj.name))
            else:
                self._avail_encoders.append(t_obj)
        
        
        if len(self._avail_decoders) < 1:
            raise NoSystemDecodersFound
        elif len(self._avail_decoders) < 1:
            raise NoSystemEncodersFound
    
    def select_decoder(self,codec_name):
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
    
        return decoder
    
    def select_encoder(self,codec_name):
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
    
        return encoder

    

    def list_supported_codecs(self):
        """
            Returns a dictionary of 'decoder' and 'encoder' names
            
        """
        d = {'decoders': [],
             'encoders': []
             }
        
        # Go through full list and get names
        for c in self.__decoders__:
            name = c().name
            d['decoders'].append(name)
            
        for c in self.__encoders__:
            name = c().name
            d['encoders'].append(name)
   
        return d 
    

    
    def available_decoders(self):

        d = {'decoders': [],
             'encoders': []
             }
        for c in self.__decoders__:
            try:
                t_obj = c()
                t_obj.find_exe()
                
            except CodecNotFound:
                # Don't add to list
                pass
            else:
                name, found_name = t_obj.name, t_obj.found_exe
                d['decoders'].append((name, found_name))
        
        for c in self.__encoders__:
            try:
                t_obj = c()
                t_obj.find_exe()
            except CodecNotFound:
                # Don't add to list
                pass
            else:
                name, found_name = t_obj.name, t_obj.found_exe
                d['encoders'].append((name, found_name))
        
        return d

    def get_available_decoders(self):
        """
            Returns a list of available decoder names
     
        """
        r_list = []
        for d in self._avail_decoders:
            r_list.append(d.name)
            
        return r_list
    
    def get_available_encoders(self):

        r_list = []

        for e in self._avail_encoders:
            r_list.append(e.name)
            
        return r_list

class SelectedCodecNotValid(Exception):
    """
        Used if a codec is selected, but not actually available
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

if __name__ == "__main__": 
    print("This module must be imported")
