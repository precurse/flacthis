__author__ = 'beallio'

'''

Test machine doesn't have ffmpeg compiled with ffmpeg-fdkaac, ogg, nor winwav

'''
import flacthis
import audio_codecs
import nose.tools


def test_output_plugin_mp3():
    output_plugin = 'mp3'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/', '/']
    ft.main(args)


def test_output_plugin_aac():
    output_plugin = 'aac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/', '/']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_output_plugin_ogg():
    output_plugin = 'ogg'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/', '/']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_output_plugin_ffmpeg_fdkaac():
    output_plugin = 'ffmpeg-fdkaac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/', '/']
    ft.main(args)


def test_output_plugin_avconv_fdkaac():
    output_plugin = 'avconv-fdkaac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/', '/']
    ft.main(args)


def test_input_plugin_flac():
    input_plugin = 'flac'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/', '/']
    ft.main(args)


def test_input_plugin_wav():
    input_plugin = 'wav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/', '/']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_input_plugin_winwav():
    input_plugin = 'winwav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/', '/']
    ft.main(args)


def test_missing_argument():
    with nose.tools.assert_raises(SystemExit) as e:
        input_plugin = 'flac'
        ft = flacthis
        args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/']
        ft.main(args)
    ex = e.exception
    nose.tools.assert_equal(ex.code, 2)


@nose.tools.raises(IOError)
def test_missing_source_dir():
    input_plugin = 'wav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/test', '/output']
    ft.main(args)


@nose.tools.raises(OSError)
def test_unreadable_source_dir():
    input_plugin = 'wav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/unreadable', '/output']
    ft.main(args)
