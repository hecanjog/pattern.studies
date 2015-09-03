from pippi import dsp
from hcj import fx

guitars = [ dsp.read('samples/guitar%s.wav' % (i + 1)).data for i in range(5) ]

def makeLong(seg):
    g = dsp.randchoose(guitars)
    g = dsp.amp(g, 0.4)
    long_guitar = dsp.fill(g, sum(seg))

    fade_guitar = dsp.randchoose(guitars)
    fade_guitar = dsp.amp(fade_guitar, dsp.rand(0.1, 0.3))
    fade_guitar = fx.penv(fade_guitar)

    out = dsp.mix([ long_guitar, fade_guitar ])

    return out
