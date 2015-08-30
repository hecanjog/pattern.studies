from pippi import dsp, tune
from hcj import keys, fx, drums, snds

#kick = dsp.read('snds/kick.wav').data
kick = snds.load('mc303/kick1.wav')
hat = snds.load('mc303/hat2.wav')
bigkick = snds.load('mc303/kick2.wav')
guitar = snds.load('hcj/guitar1.wav')
rhodes = snds.load('hcj/rhodes1.wav')
rhodes = dsp.transpose(rhodes, 16.0/15.0)
#bigkick = dsp.read('snds/kick606.wav').data
#snare = dsp.read('snds/snare.wav').data
#snare = dsp.env(snare, 'phasor')
snare = snds.load('mc303/snare1.wav')
snare = dsp.amp(snare, 3)

snarex = dsp.split(snare, 0, 1)

key = 'c#'

def getRatio(degree, ratios=tune.terry, scale=tune.major):
    ratio = ratios[scale[(degree - 1) % len(scale)]]
    return ratio[0] / ratio[1]

# tempo path
def tempoPath(nsegs):
    #maxms = dsp.rand(300, 500)
    #minms = dsp.rand(1, 100)
    minms = 1
    maxms = 500
    wavetypes = ['hann', 'sine', 'vary']

    out = []

    for _ in range(nsegs):
        seglen = dsp.randint(20, 100)
        seg = dsp.wavetable(dsp.randchoose(wavetypes), seglen)

        # pull out a randomly selected subsegment of the curve
        sublen = seglen / dsp.randint(2, 5)
        segstart = dsp.randint(0, seglen - sublen)
        segend = segstart + sublen
        seg = seg[segstart:segend]

        out += [ [ dsp.mstf(abs(s) * (maxms - minms) + minms) for s in seg ] ]

    return out

def rhodesChord(length, chord, amp):
    layers = [ keys.rhodes(length, freq, amp * dsp.rand(0.25, 0.5)) for freq in chord ]
    layers = [ dsp.pan(layer, dsp.rand()) for layer in layers ]

    return dsp.mix(layers)

def parseBeat(pattern):
    out = []
    for tick in pattern:
        if tick == 'x':
            out += [ 1 ]
        else:
            out += [ 0 ]

    return out

def makeBeat(pattern, lengths, callback):
    out = ''

    for i, length in enumerate(lengths):
        # Silence or beat?
        amp = pattern[i % len(pattern)]

        if amp > 0:
            out += callback(length, i)
        else:
            out += dsp.pad('', 0, length)

    try:
        assert dsp.flen(out) == sum(lengths)
    except AssertionError:
        print 'doh', dsp.flen(out), sum(lengths), pattern

    return out

gmelody = [1,3,4,6,9]

def makeGuitar(length, i):
    #g = dsp.transpose(guitar, getRatio(gmelody[i % len(gmelody)]))
    #g = dsp.transpose(guitar, getRatio(scale[ i % len(scale)]))
    r = dsp.transpose(guitar, getRatio(scale[ i % len(scale)]))
    r = dsp.amp(r, dsp.rand(0.1, 0.5))

    #g = dsp.mix([g,r])
    g = dsp.fill(r, length, silence=True)


    return g

def makeHat(length, i):
    #h = dsp.bln(length / 4, dsp.rand(6000, 8000), dsp.rand(9000, 16000))
    #h = dsp.amp(h, dsp.rand(0.5, 1))
    #h = dsp.env(h, 'phasor')
    h = hat
    h = dsp.fill(h, length, silence=True)

    return h

def makeKick(length, i):
    return dsp.taper(dsp.fill(dsp.mix([ bigkick, kick ]), length, silence=True), 40)

def makeSnare(length, i):
    #burst = dsp.bln(length, dsp.rand(400, 800), dsp.rand(8000, 10000))
    #burst = dsp.env(burst, 'phasor')
    #s = dsp.mix([snare, burst])
    s = snare
    s = dsp.transpose(s, dsp.rand(0.9, 1.1))

    s = dsp.fill(s, length, silence=True)

    return dsp.taper(s, 40)

def makeStab(length, i):
    chord = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=3, root=key)
    stab = rhodesChord(length, chord, dsp.rand(0.5, 0.75))
    stab = dsp.taper(stab, 40)
    stab = dsp.fill(stab, length, silence=True)

    return stab

def makePulse(length, i):
    chord = tune.fromdegrees([ dsp.randchoose([1,4,5,8]) for _ in range(dsp.randint(2,4)) ], octave=2, root=key)
    pulse = rhodesChord(length, chord, dsp.rand(0.5, 0.75)) 
    #pulse = dsp.mix([ pulse, kick ])
    pulse = dsp.taper(pulse, 40)
    pulse = dsp.amp(pulse, dsp.rand(0.9, 1.5))
    pulse = dsp.fill(pulse, length, silence=True)

    return pulse


def splitSeg(seg, size=2, vary=False):
    def split(s, size):
        hs = s / size
        rs = s - hs
        return [ hs, rs ]

    subseg = []
    for s in seg:
        if vary:
            if dsp.rand() > 0.5:
                subseg += split(s, size)
            else:
                subseg += [ s ]
        else:
            subseg += split(s, size)

    assert sum(subseg) == sum(seg)

    return subseg

out = ''
changeindex = 0
segs = tempoPath(50)

for segi, seg in enumerate(segs): 
    print 'Rendering section %s' % (segi + 1)

    scale = dsp.rotate([1,2,3,4,5,6,7,8,9,10], vary=True)
    if dsp.rand() > 0.5:
        scale.reverse()

    for _ in range(4, 8):
        scale.pop(dsp.randint(0, len(scale)-1))


    # kicks
    kickp =  'x...-.....x..x...'
    pattern = parseBeat(kickp)
    kicks = makeBeat(pattern, seg, makeKick)

    # snares
    snarep = '..x...x...'
    pattern = parseBeat(snarep)
    subseg = splitSeg(seg, 2)
    snares = makeBeat(pattern, subseg, makeSnare)

    # hats
    hatp =   'xxxx'
    pattern = parseBeat(hatp)
    subseg = splitSeg(seg, 4)
    hats = makeBeat(pattern, subseg, makeHat)

    # guitar 
    pattern = parseBeat('x  x')
    guitars = makeBeat(pattern, seg, makeGuitar)

    # stabs
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length)
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, vary=True)
    subseg = splitSeg(seg, 3)

    stabs = makeBeat(pattern, subseg, makeStab)
    
    # pulses
    pulsep = 'x..'
    pattern = parseBeat(pulsep)
    pulses = makeBeat(pattern, seg, makePulse)

    instLayers = [ kicks, snares, stabs, hats, pulses, guitars ]

    if segi <= 40:
        for _ in range(0, 4):
            instLayers.pop(dsp.randint(0, len(instLayers)-1))

    section = dsp.mix(instLayers)

    chord = [ dsp.randint(1, 9) for _ in range(dsp.randint(2,4)) ]
    long_chord = rhodesChord(sum(seg), tune.fromdegrees(chord, octave=dsp.randint(2,4), root=key), dsp.rand(0.6, 0.75))
    long_chord = dsp.fill(long_chord, sum(seg))
    long_chord = dsp.mix([ long_chord, dsp.fill(guitar, sum(seg), silence=True) ])

    def makeGlitch(length, i):
        g = dsp.cut(long_chord, dsp.randint(0, dsp.flen(long_chord) - length), length)
        g = dsp.alias(g)
        g = dsp.fill(g, length)

        return g

    subseg = splitSeg(seg, 2)
    glitches = makeBeat([1,1], subseg, makeGlitch)

    changeindex = changeindex + 1

    section = dsp.mix([ section, long_chord, glitches ])

    out += section


dsp.write(out, 'study.vii')
