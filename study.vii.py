from pippi import dsp, tune

import orc.hat
import orc.kick
import orc.snare
import orc.suiteguitar
import orc.rhodes

key = 'g'

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


    # kicks
    kickp =  'x...-.....x..x...'
    pattern = parseBeat(kickp)
    kicks = makeBeat(pattern, seg, orc.kick.make)

    # snares
    snarep = '..x...x...'
    pattern = parseBeat(snarep)
    subseg = splitSeg(seg, 2)
    snares = makeBeat(pattern, subseg, orc.snare.make)

    # hats
    hatp =   'xxxx'
    pattern = parseBeat(hatp)
    subseg = splitSeg(seg, 4)
    hats = makeBeat(pattern, subseg, orc.hat.make)

    # guitar 
    pattern = parseBeat('x  x')
    orc.suiteguitar.scale = orc.suiteguitar.makeScale()
    guitars = makeBeat(pattern, seg, orc.suiteguitar.make)

    # stabs
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length)
    orc.rhodes.key = key
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, vary=True)
    subseg = splitSeg(seg, 3)
    stabs = makeBeat(pattern, subseg, orc.rhodes.makeStab)
    
    # pulses
    pulsep = 'x..'
    pattern = parseBeat(pulsep)
    pulses = makeBeat(pattern, seg, orc.rhodes.makePulse)

    instLayers = [ kicks, snares, stabs, hats, pulses ]

    if segi <= 40:
        for _ in range(0, 4):
            instLayers.pop(dsp.randint(0, len(instLayers)-1))

    section = dsp.mix(instLayers)

    chord = [ dsp.randint(1, 9) for _ in range(dsp.randint(2,4)) ]
    long_chord = orc.rhodes.chord(sum(seg), tune.fromdegrees(chord, octave=dsp.randint(2,4), root=key), dsp.rand(0.6, 0.75))
    long_chord = dsp.fill(long_chord, sum(seg))

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
