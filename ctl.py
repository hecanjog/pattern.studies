from pippi import dsp, tune

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


