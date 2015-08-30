from pippi import dsp, tune
from hcj import snds

guitar = snds.load('hcj/guitar1.wav')

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
    #g = dsp.transpose(guitar, getRatio(gmelody[i % len(gmelody)]))
    #g = dsp.transpose(guitar, getRatio(scale[ i % len(scale)]))
    r = dsp.transpose(guitar, getRatio(scale[ i % len(scale)]))
    r = dsp.amp(r, dsp.rand(0.1, 0.5))

    #g = dsp.mix([g,r])
    g = dsp.fill(r, length, silence=True)


    return g


