from pippi import dsp, tune

import orc.hat
import orc.kick
import orc.snare
import orc.suiteguitar
import orc.rhodes
import orc.guitar
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

    long_chord = orc.rhodes.makeLongChord(seg)
    long_guitar = orc.guitar.makeLong(seg)

    subseg = ctl.splitSeg(seg, 2)
    orc.rhodes.long_chord = long_chord
    glitches = ctl.makeBeat([1,1], subseg, orc.rhodes.makeGlitch)

    changeindex = changeindex + 1

    section = dsp.mix([ section, long_chord, long_guitar, glitches ])

    out += section


dsp.write(out, 'study.vii')
