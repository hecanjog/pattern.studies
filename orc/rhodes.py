from pippi import dsp, tune
from hcj import snds, keys

key = 'g'

rhodes = snds.load('hcj/rhodes1.wav')
rhodes = dsp.transpose(rhodes, 16.0/15.0)

def chord(length, c, amp):
    layers = [ keys.rhodes(length, freq, amp * dsp.rand(0.25, 0.5)) for freq in c ]
    layers = [ dsp.pan(layer, dsp.rand()) for layer in layers ]

    return dsp.mix(layers)

def makeStab(length, i):
    c = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=3, root=key)
    stab = chord(length, c, dsp.rand(0.5, 0.75))
    stab = dsp.taper(stab, 40)
    stab = dsp.fill(stab, length, silence=True)

    return stab

def makePulse(length, i):
    c = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=2, root=key)
    pulse = chord(length, c, dsp.rand(0.5, 0.75)) 
    pulse = dsp.taper(pulse, 40)
    pulse = dsp.amp(pulse, dsp.rand(0.9, 1.5))
    pulse = dsp.fill(pulse, length, silence=True)

    return pulse


