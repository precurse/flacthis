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
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/test', '/test']
    ft.main(args)


def test_output_plugin_aac():
    output_plugin = 'aac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/test', '/test']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_output_plugin_ogg():
    output_plugin = 'ogg'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/test', '/test']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_output_plugin_ffmpeg_fdkaac():
    output_plugin = 'ffmpeg-fdkaac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/test', '/test']
    ft.main(args)


def test_output_plugin_avconv_fdkaac():
    output_plugin = 'avconv-fdkaac'
    ft = flacthis
    args = ['-i', 'flac', '-o', '{}'.format(output_plugin), '/test', '/test']
    ft.main(args)


def test_input_plugin_flac():
    input_plugin = 'flac'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/test', '/test']
    ft.main(args)


def test_input_plugin_wav():
    input_plugin = 'wav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/test', '/test']
    ft.main(args)


@nose.tools.raises(audio_codecs.SelectedCodecNotValid)
def test_input_plugin_winwav():
    input_plugin = 'winwav'
    ft = flacthis
    args = ['-i', '{}'.format(input_plugin), '-o', 'mp3', '/test', '/test']
    ft.main(args)