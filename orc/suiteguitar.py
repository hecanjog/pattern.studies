from pippi import dsp, tune
from hcj import snds

guitar = snds.load('hcj/guitar1.wav')
guitar = dsp.transpose(guitar, 0.711) # transpose from Db to G

def makeScale():
    scale = dsp.rotate([1,2,3,4,5,6,7,8,9,10], vary=True)
    if dsp.rand() > 0.5:
        scale.reverse()

    for _ in range(4, 8):
        scale.pop(dsp.randint(0, len(scale)-1))

    return scale

def getRatio(degree, ratios=tune.terry, scale=tune.major):
    ratio = ratios[scale[(degree - 1) % len(scale)]]
    return ratio[0] / ratio[1]

def make(length, i):
    r = dsp.transpose(guitar, getRatio(scale[ i % len(scale)]))
    r = dsp.mix([ dsp.pan(r, dsp.rand()), dsp.drift(dsp.pan(r, dsp.rand()), dsp.rand(0.001, 0.02)) ])

    if dsp.rand() > 0.5:
        r = dsp.alias(r)

    if dsp.rand() > 0.5:
        r = dsp.split(r, dsp.flen(r) / dsp.randint(2,5))
        r = dsp.randshuffle(r)
        r = ''.join(r)

    r = dsp.amp(r, dsp.rand(0.1, 0.75))

    g = dsp.fill(r, length, silence=True)

    return g


