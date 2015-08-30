from pippi import dsp
from hcj import snds

hat = snds.load('mc303/hat2.wav')

def make(length, i):
    #h = dsp.bln(length / 4, dsp.rand(6000, 8000), dsp.rand(9000, 16000))
    #h = dsp.amp(h, dsp.rand(0.5, 1))
    #h = dsp.env(h, 'phasor')
    h = hat
    h = dsp.fill(h, length, silence=True)

    return h


