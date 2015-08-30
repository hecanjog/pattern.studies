from pippi import dsp, tune

import orc.hat
import orc.kick
import orc.snare
import orc.suiteguitar
import orc.rhodes
import ctl

key = 'g'

out = ''
changeindex = 0
segs = ctl.tempoPath(50)

for segi, seg in enumerate(segs): 
    print 'Rendering section %s' % (segi + 1)

    # kicks
    kickp =  'x...-.....x..x...'
    pattern = ctl.parseBeat(kickp)
    kicks = ctl.makeBeat(pattern, seg, orc.kick.make)

    # snares
    snarep = '..x...x...'
    pattern = ctl.parseBeat(snarep)
    subseg = ctl.splitSeg(seg, 2)
    snares = ctl.makeBeat(pattern, subseg, orc.snare.make)

    # hats
    hatp =   'xxxx'
    pattern = ctl.parseBeat(hatp)
    subseg = ctl.splitSeg(seg, 4)
    hats = ctl.makeBeat(pattern, subseg, orc.hat.make)

    # guitar 
    pattern = ctl.parseBeat('x  x')
    orc.suiteguitar.scale = orc.suiteguitar.makeScale()
    guitars = ctl.makeBeat(pattern, seg, orc.suiteguitar.make)

    # stabs
    bar_length = dsp.randint(4, 13)
    num_pulses = dsp.randint(1, bar_length)
    orc.rhodes.key = key
    pattern = dsp.eu(bar_length, num_pulses)
    pattern = dsp.rotate(pattern, vary=True)
    subseg = ctl.splitSeg(seg, 3)
    stabs = ctl.makeBeat(pattern, subseg, orc.rhodes.makeStab)
    
    # pulses
    pulsep = 'x..'
    pattern = ctl.parseBeat(pulsep)
    pulses = ctl.makeBeat(pattern, seg, orc.rhodes.makePulse)

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

    subseg = ctl.splitSeg(seg, 2)
    glitches = ctl.makeBeat([1,1], subseg, makeGlitch)

    changeindex = changeindex + 1

    section = dsp.mix([ section, long_chord, glitches ])

    out += section


dsp.write(out, 'study.vii')
