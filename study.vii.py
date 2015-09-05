from pippi import dsp

import orc.hat
import orc.kick
import orc.snare
import orc.suiteguitar
import orc.rhodes
import orc.guitar
import ctl

key = 'g'

out = ''
nsegs = 60

segs = ctl.tempoPath(nsegs)

kickprob = [ 0 for _ in range(20) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 30) + [ 0 for _ in range(10) ]
snareprob = [ 0 for _ in range(20) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 30) + [ 0 for _ in range(10) ]
hatprob = [ 0 for _ in range(10) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 20) + [ 0 for _ in range(10) ]
suiteguitarprob = dsp.breakpoint([ dsp.rand() for _ in range(8) ], 15) + [ 0 for _ in range(nsegs - 30) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], 15)
stabprob = [ 0 for _ in range(3) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 6) + [ 0 for _ in range(3) ]
pulseprob = [ 0 for _ in range(3) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 6) + [ 0 for _ in range(3) ]
longchordprob = [ 1 for _ in range(3) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 6) + [ 1 for _ in range(3) ]
guitarprob = [ 1 for _ in range(nsegs) ]
glitchprob = [ 1 for _ in range(3) ] + dsp.breakpoint([ dsp.rand() for _ in range(8) ], nsegs - 6) + [ 1 for _ in range(3) ]

for segi, seg in enumerate(segs): 
    print 'Rendering section %s' % (segi + 1)

    layers = []

    if dsp.rand() < kickprob[segi]:
        kickp =  'x...-.....x..x...'
        pattern = ctl.parseBeat(kickp)
        kicks = ctl.makeBeat(pattern, seg, orc.kick.make)

        layers += [ kicks ]

    if dsp.rand() < snareprob[segi]:
        snarep = '..x...x...'
        pattern = ctl.parseBeat(snarep)
        subseg = ctl.splitSeg(seg, 2)
        snares = ctl.makeBeat(pattern, subseg, orc.snare.make)

        layers += [ snares ]

    if dsp.rand() < hatprob[segi]:
        hatp =   'xxxx'
        pattern = ctl.parseBeat(hatp)
        subseg = ctl.splitSeg(seg, 4)
        hats = ctl.makeBeat(pattern, subseg, orc.hat.make)

        layers += [ hats ]

    if dsp.rand() < suiteguitarprob[segi]:
        pattern = ctl.parseBeat('x  x')
        orc.suiteguitar.scale = orc.suiteguitar.makeScale()
        guitars = ctl.makeBeat(pattern, seg, orc.suiteguitar.make)

        layers += [ guitars ]

    if dsp.rand() < stabprob[segi]:
        bar_length = dsp.randint(4, 13)
        num_pulses = dsp.randint(1, bar_length)
        orc.rhodes.key = key
        pattern = dsp.eu(bar_length, num_pulses)
        pattern = dsp.rotate(pattern, vary=True)
        subseg = ctl.splitSeg(seg, 3)
        stabs = ctl.makeBeat(pattern, subseg, orc.rhodes.makeStab)

        layers += [ stabs ]
    
    if dsp.rand() < pulseprob[segi]:
        orc.rhodes.key = key
        pulsep = 'x..'
        pattern = ctl.parseBeat(pulsep)
        pulses = ctl.makeBeat(pattern, seg, orc.rhodes.makePulse)

        layers += [ pulses ]

    orc.rhodes.key = key
    long_chord = orc.rhodes.makeLongChord(seg)
    if dsp.rand() < longchordprob[segi]:
        layers += [ long_chord ]

    if dsp.rand() < guitarprob[segi]:
        long_guitar = orc.guitar.makeLong(seg)
        layers += [ long_guitar ]

    if dsp.rand() < glitchprob[segi]:
        subseg = ctl.splitSeg(seg, 2)
        orc.rhodes.long_chord = long_chord
        glitches = ctl.makeBeat([1,1], subseg, orc.rhodes.makeGlitch)

        layers += [ glitches ]

    if len(layers) > 0:
        section = dsp.mix(layers)
        out += section

out += dsp.env(dsp.mix([ orc.guitar.makeLong([dsp.stf(dsp.rand(4, 8))]) for _ in range(2) ]), 'phasor')
out += dsp.env(dsp.mix([ orc.guitar.makeLong([dsp.stf(dsp.rand(4, 10))]) for _ in range(2) ]), 'phasor')
out += dsp.env(dsp.mix([ orc.guitar.makeLong([dsp.stf(dsp.rand(6, 12))]) for _ in range(3) ]), 'phasor')

dsp.write(out, '02-study.vii')
