from pippi import dsp, tune
from hcj import fx, keys
import ctl

tlength = dsp.stf(60 * 3)

out = ''
elapsed = 0
count = 0

dloop = dsp.read('samples/jess/loop2.wav').data
kicksoft = dsp.read('samples/jess/kickshuffle.wav').data
kickhard = dsp.read('samples/jess/kickcym.wav').data
snare = dsp.read('samples/jess/snare.wav').data
flam = dsp.read('samples/jess/snareflam.wav').data
smash = dsp.read('samples/jess/smash.wav').data
skitter = dsp.read('samples/jess/skitter.wav').data

def makeSwells(cname, numswells, length, key='e', octave=1):
    swells = []

    for _ in range(numswells):
        slength = dsp.randint((length / numswells) * 0.85, length / numswells)
        swell = keys.pulsars(cname, slength, drift=dsp.rand(0.001, 0.01), speed=dsp.rand(0.1, 0.5), amp=dsp.rand(0.2, 0.5), key=key, octave=octave)
        swell = dsp.env(swell, 'hann')
        swell = dsp.taper(swell, 30)

        swells += [ swell ]

    swells = [ dsp.fill(swell, length / numswells, silence=True) for swell in swells ]

    return ''.join(swells)

def makeSnare(length, i):
    return dsp.fill(snare, length, silence=True)

def makeKick(length, i):
    k = dsp.randchoose([ kickhard, kicksoft ])
    return dsp.fill(k, length, silence=True)

while elapsed < tlength:
    print 'Rendering section %s...' % count

    bar = ''

    bar += dsp.mix([ dloop, kickhard ])
    bar += dsp.mix([ dloop, kicksoft ])
    bar += dsp.mix([ dloop, kicksoft ])

    beat = dsp.flen(bar) / 16
    bar = dsp.split(bar, beat)
    bar = dsp.randshuffle(bar)
    for i, b in enumerate(bar):
        if dsp.rand() > 0.5:
            bar[i] = dsp.pad('', 0, dsp.flen(b))

    bar = ''.join(bar)

    snarep = '..x.'
    pattern = ctl.parseBeat(snarep)
    snares = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeSnare)

    kickp = 'x.......'
    pattern = ctl.parseBeat(kickp)
    kicks = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeKick)

    sm = dsp.fill(smash, dsp.flen(bar))
    sm = dsp.mix([ dsp.alias(sm), fx.penv(sm) ])
    sm = dsp.amp(sm, dsp.rand(0.5, 1))
    sk = dsp.fill(skitter, dsp.flen(bar))
    sk = fx.penv(sk)

    if count % 4 == 0:
        bar = dsp.mix([ bar, dsp.pad(flam, dsp.flen(bar) - dsp.flen(flam), 0) ])

    # Look ma, harmonic motion!
    progression = 'i i v IV IV6'.split(' ')
    cname = progression[ count % len(progression) ]
    swells = dsp.mix([ makeSwells(cname, nswell, dsp.flen(bar)) for nswell in [8,4] ])

    bar = dsp.mix([ bar, sm, sk, snares, kicks, swells ])

    out += bar

    elapsed += dsp.flen(bar)
    count += 1

dsp.write(out, '03-study.ix')
