from pippi import dsp, tune
from hcj import snds, keys

key = 'g'

rhodes = snds.load('hcj/rhodes1.wav')
rhodes = dsp.transpose(rhodes, 16.0/15.0)

def chord(length, freqs, amp):
    layers = [ keys.rhodes(length, freq, amp * dsp.rand(0.25, 0.5)) for freq in freqs ]
    layers = [ dsp.pan(layer, dsp.rand()) for layer in layers ]

    return dsp.mix(layers)

def makeStab(length, i):
    freqs = tune.fromdegrees([ dsp.randchoose([1,2,3,4,5,6,8]) for _ in range(dsp.randint(2,4)) ], octave=3, root=key)
    stab = chord(length, freqs, dsp.rand(0.25, 0.75))
    stab = dsp.taper(stab, 40)
    stab = dsp.fill(stab, length, silence=True)

    return stab

def makePulse(length, i):
    freqs = tune.fromdegrees([ dsp.randchoose([1,2,3,4,5,6,8]) for _ in range(dsp.randint(2,4)) ], octave=2, root=key)
    pulse = chord(length, freqs, dsp.rand(0.5, 0.75)) 
    pulse = dsp.taper(pulse, 40)
    pulse = dsp.amp(pulse, dsp.rand(0.5, 1))
    pulse = dsp.fill(pulse, length, silence=True)

    return pulse

def makeLongChord(seg):
    degrees = [ dsp.randint(1, 9) for _ in range(dsp.randint(2,4)) ]
    long_chord = chord(sum(seg), [ freq * 2**dsp.randint(0, 5) for freq in tune.fromdegrees(degrees, octave=1, root=key) ], dsp.rand(0.15, 0.35))
    long_chord = dsp.fill(long_chord, sum(seg))

    return long_chord

def makeGlitch(length, i):
    g = dsp.cut(long_chord, dsp.randint(0, dsp.flen(long_chord) - length), length)
    g = dsp.alias(g)
    g = dsp.fill(g, length)

    return g


