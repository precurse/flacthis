__author__ = 'precurse'

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flacthis import ConverterConfig, LosslessToLossyConverter
import audio_codecs
import multiprocessing
import tempfile
from distutils import spawn

class TestConverterConfig(object):
    # Source dir tests
    def test_source_dir_missing(self, converter_config):
        t_dir = tempfile.gettempdir()
        with pytest.raises(OSError, match='Source directory not a directory'):
            converter_config.source_dir = os.path.join(t_dir, 'path/does/not/exist')

    def test_source_dir_is_file(self, converter_config):
        with pytest.raises(OSError, match='Source directory not a directory'):
            converter_config.source_dir = '/dev/null'

    def test_source_dir_not_readable(self, converter_config):
        with pytest.raises(OSError, match='Source directory not readable'):
            converter_config.source_dir = '/root/'

    def test_source_dir_readable(self, converter_config):
        converter_config.source_dir = '/tmp/'

    # Destination dir tests
    def test_dest_dir_is_nonexistent_and_parent_not_writable(self, converter_config):
        with pytest.raises(OSError, match='Destination directory parent not writable'):
            converter_config.dest_dir = '/this_path_is_not_writable'

    def test_dest_dir_exists_and_not_writable(self, converter_config):
        with pytest.raises(OSError, match='Destination directory not writable'):
            converter_config.dest_dir = '/'

    def test_dest_dir_exists_and_is_a_file(self, converter_config):
        with pytest.raises(OSError, match='Destination directory is a file'):
            converter_config.dest_dir = '/dev/null'

    def test_dest_dir_parent_writable(self, converter_config):
        t_dir = tempfile.gettempdir()
        dir = os.path.join(t_dir,'path_does_not_exist')
        converter_config.dest_dir = dir
        assert converter_config._dest_dir == dir

    def test_dest_dir_writable(self, converter_config):
        t_dir = tempfile.gettempdir()
        converter_config.dest_dir = t_dir
        assert converter_config._dest_dir == t_dir

    def test_auto_thread_detection(self, converter_config):
        converter_config.threads = 0
        cpu_count = multiprocessing.cpu_count()

        assert converter_config._threads == cpu_count

    def test_invalid_thread_count(self, converter_config):
        with pytest.raises(OSError, match='Cannot set thread count to less than 0'):
            converter_config.threads = -1

class TestCodecManager(object):
    def test_convert_invalid_encoder(self, codec_manager):
        with pytest.raises(audio_codecs.SelectedCodecNotValid):
            codec_manager.get_encoder('foo-bar-codec')

    def test_convert_invalid_decoder(self, codec_manager):
        with pytest.raises(audio_codecs.SelectedCodecNotValid):
            codec_manager.get_decoder('foo-bar-codec')

    def test_codec_manager_select_decoder_without_discover(self):
        with pytest.raises(audio_codecs.SelectedCodecNotValid):
            m = audio_codecs.CodecManager()
            m.get_decoder('flac')

    def test_codec_manager_select_encoder_without_discover(self):
        with pytest.raises(audio_codecs.SelectedCodecNotValid):
            m = audio_codecs.CodecManager()
            m.get_encoder('flac')

    def test_decoder_list_length_after_discovery(self):
        m = audio_codecs.CodecManager()
        m.discover_codecs()
        l = len(m._avail_decoders)
        m.discover_codecs()
        l2 = len(m._avail_decoders)
        assert l == l2

    def test_encoder_list_length_after_discovery(self):
        m = audio_codecs.CodecManager()
        m.discover_codecs()
        l = len(m._avail_encoders)
        m.discover_codecs()
        l2 = len(m._avail_encoders)
        assert l == l2

class TestConverter(object):
    def test_convert_flac_to_mp3(self, flac_converter, codec_manager):
        flac_converter.Encoder = codec_manager.get_encoder('mp3')
        flac_converter.start()

    def test_convert_wav_to_mp3(self, wav_converter, codec_manager):
        wav_converter.Encoder = codec_manager.get_encoder('mp3')
        wav_converter.start()

    def test_convert_flac_to_faac(self, flac_converter, codec_manager):
        flac_converter.Encoder = codec_manager.get_encoder('aac')
        flac_converter.start()

    def test_convert_wav_to_faac(self, wav_converter, codec_manager):
        wav_converter.Encoder = codec_manager.get_encoder('aac')
        wav_converter.start()

    @pytest.mark.skipif(not spawn.find_executable('fdkaac'),
                        reason="fdkaac not found")
    def test_convert_flac_to_fdkaac(self, flac_converter, codec_manager):
        flac_converter.Encoder = codec_manager.get_encoder('fdkaac')
        flac_converter.start()

    @pytest.mark.skipif(not spawn.find_executable('fdkaac'),
                        reason="fdkaac not found")
    def test_convert_wav_to_fdkaac(self, wav_converter, codec_manager):
        wav_converter.Encoder = codec_manager.get_encoder('fdkaac')
        wav_converter.start()

    def test_convert_flac_to_ogg(self, flac_converter, codec_manager):
        flac_converter.Encoder = codec_manager.get_encoder('ogg')
        flac_converter.start()

    def test_convert_wav_to_ogg(self, wav_converter, codec_manager):
        wav_converter.Encoder = codec_manager.get_encoder('ogg')
        wav_converter.start()

    def test_convert_invalid_source_dir(self, flac_converter, codec_manager):
        with pytest.raises(AssertionError):
            flac_converter.source_dir = None
            flac_converter.Encoder = codec_manager.get_encoder('mp3')
            flac_converter.start()

    def test_convert_invalid_destination_dir(self, flac_converter, codec_manager):
        with pytest.raises(AssertionError):
            flac_converter.dest_dir = None
            flac_converter.Encoder = codec_manager.get_encoder('mp3')
            flac_converter.start()
