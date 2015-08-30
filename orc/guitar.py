from pippi import dsp

guitars = [ dsp.read('samples/guitar%s.wav' % (i + 1)).data for i in range(5) ]

def makeLong(seg):
    g = dsp.randchoose(guitars)
    g = dsp.amp(g, 0.5)
    long_guitar = dsp.fill(g, sum(seg))

    return long_guitar
