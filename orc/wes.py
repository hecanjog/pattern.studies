from glob import glob
from pippi import dsp

def make(length):
    samps = glob('samples/wes/*.wav')

    voice = dsp.read(dsp.randchoose(samps)).data
    voice = dsp.fill(voice, length)

    return voice
