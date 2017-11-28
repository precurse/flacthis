import pytest
from flacthis import ConverterConfig, LosslessToLossyConverter
import audio_codecs
import mutagen

@pytest.fixture
def converter_config():
    config = ConverterConfig()
    config.threads = 0
    return config

@pytest.fixture(scope='session')
def create_mock_source_dir(tmpdir_factory):
    import wave
    import subprocess
    import random
    import struct
    from shutil import copy2

    # Setup directory structure
    t_dir = tmpdir_factory.mktemp('flacthis_test_data')
    src_dir = t_dir.join('src')
    dest_dir = t_dir.join('dest')

    # Make src directory
    t_dir.mkdir('src')

    # Make mock audio wav and flac files
    sample_len = 441000 # 10 seconds of noise

    f_wav = src_dir.join('test_wav.wav')
    f_flac = src_dir.join('test_flac.flac')

    output = wave.open(str(f_wav), 'w')
    values = []

    output.setparams((2, 2, 44100, 0, 'NONE', 'not compressed'))

    for i in range(0, sample_len/10):
        value = random.randint(-32767, 32767)
        packed_value = struct.pack('h', value)

        # Duplicate some data to make it compressible
        for i in range(0,10):
            values.append(packed_value)
            values.append(packed_value)

    value_str = ''.join(values)
    output.writeframes(value_str)
    output.close()

    # Compress wav file to flac
    subprocess.call(['flac','--fast', str(f_wav), '-o', str(f_flac)])

    # Create tags on flac file
    f_tags = mutagen.File(str(f_flac), easy=True)

    f_tags['artist'] = 'fake_artist'
    f_tags['title'] = 'fake_title'
    f_tags['tracknumber'] = '1'
    f_tags['genre'] = 'fake'
    f_tags.save()

    # Create mock album folders
    mock_albums = []

    for i in range(0,3):
        album = 'album_{}'.format(i)
        src_dir.mkdir('album_{}'.format(i))
        album_dir = src_dir.join(album)
        mock_albums.append(album_dir)

        # Copy mock audio files
        copy2(str(f_wav), str(album_dir))
        copy2(str(f_flac), str(album_dir))

    # Create mock artwork
    art_exts = LosslessToLossyConverter.artwork_ext
    mock_art = []

    for ext in art_exts:
        for a in mock_albums:
          art = a.join('art.' + ext)
          open(str(art), 'a').close()
          mock_art.append(art)

    r = {
        'mock_albums': mock_albums,
        'mock_art': mock_art,
        't_dir': t_dir,
        'src_dir': src_dir,
        'dest_dir': dest_dir
    }

    return r

@pytest.fixture
def codec_manager():
    m = audio_codecs.CodecManager()
    m.discover_codecs()

    return m

@pytest.fixture
def flac_converter(converter_config, create_mock_source_dir, codec_manager):
    conf = converter_config
    conf.source_dir = str(create_mock_source_dir['src_dir'])
    conf.dest_dir = str(create_mock_source_dir['dest_dir'])
    conf.decoder = codec_manager.get_decoder('flac')
    conv = LosslessToLossyConverter(conf)

    return conv

@pytest.fixture
def wav_converter(converter_config, create_mock_source_dir, codec_manager):
    conf = converter_config
    conf.source_dir = str(create_mock_source_dir['src_dir'])
    conf.dest_dir = str(create_mock_source_dir['dest_dir'])
    conf.decoder = codec_manager.get_decoder('wav')
    conv = LosslessToLossyConverter(conf)

    return conv
