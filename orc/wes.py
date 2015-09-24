from glob import glob
from pippi import dsp

def fetch():
    samps = glob('samples/wes/*.wav')
    return dsp.read(dsp.randchoose(samps)).data


def make(length):
    return dsp.fill(fetch(), length)

