from pippi import dsp
from hcj import snds

snare = snds.load('mc303/snare1.wav')
snare = dsp.amp(snare, 3)
#snare = dsp.read('snds/snare.wav').data
#snare = dsp.env(snare, 'phasor')
snarex = dsp.split(snare, 0, 1)

def make(length, i):
    #burst = dsp.bln(length, dsp.rand(400, 800), dsp.rand(8000, 10000))
    #burst = dsp.env(burst, 'phasor')
    #s = dsp.mix([snare, burst])
    s = snare
    s = dsp.transpose(s, dsp.rand(0.9, 1.1))

    s = dsp.fill(s, length, silence=True)

    return dsp.taper(s, 40)


