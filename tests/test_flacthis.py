__author__ = 'precurse'

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flacthis import ConverterConfig, LosslessToLossyConverter
import audio_codecs
import multiprocessing

class TestConverterConfig(object):

    # Source dir tests
    def test_source_dir_missing(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Source directory not a directory'):
            config.source_dir = '/this/path_should/never/exist/9999999'

    def test_source_dir_is_file(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Source directory not a directory'):
            config.source_dir = '/dev/null'

    def test_source_dir_not_readable(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Source directory not readable'):
            config.source_dir = '/root/'

    def test_source_dir_readable(self):
        config = ConverterConfig()
        config.source_dir = '/tmp/'

    # Destination dir tests
    def test_dest_dir_is_nonexistent_and_parent_not_writable(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Destination directory parent not writable'):
            config.dest_dir = '/this/path_should_not/exist_1234567890'

    def test_dest_dir_exists_and_not_writable(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Destination directory not writable'):
            config.dest_dir = '/'

    def test_dest_dir_exists_and_is_a_file(self):
        config = ConverterConfig()
        with pytest.raises(OSError, match='Destination directory is a file'):
            config.dest_dir = '/dev/null'

    def test_dest_dir_parent_writable(self):
        config = ConverterConfig()
        config.dest_dir = '/tmp/path_should/not_exist/999999'

    def test_dest_dir_writable(self):
        config = ConverterConfig()
        config.dest_dir = '/tmp/'

    def test_auto_thread_detection(self):
        config = ConverterConfig()
        config.threads = 0
        cpu_count = multiprocessing.cpu_count()

        assert config._threads == cpu_count




# class TestConverter(unittest.TestCase):
#     def setUp(self):
#         self.config = ConverterConfig()
#         self.config.source_dir = 'src'
#         self.config.dest_dir = 'dest'
#         self.converter = LosslessToLossyConverter(self.config)

#     def test_translate_src_to_dest(self):
#         self.converter.translate_src_to_dest('src/test_file.flac')

# if __name__ == '__main__':
#     unittest.main()
