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

    freqs = tune.chord(cname, key, octave)

    root = tune.ntf(key, octave)

    # Naive pitch wrapping
    for i, freq in enumerate(freqs):
        if freq > root * 2.5:
            freqs[i] = freq * 0.5

    for _ in range(numswells):
        slength = dsp.randint((length / numswells) * 0.85, length / numswells)
        swell = [ keys.pulsar(freq, slength, drift=dsp.rand(0.001, 0.01), speed=dsp.rand(0.1, 0.5), amp=dsp.rand(0.2, 0.5)) for freq in freqs ]
        swell = dsp.mix(swell)
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

def makeBloop(length, i, bfreqs):
    bfreq = dsp.randchoose(bfreqs)

    if dsp.rand() > 0.5:
        blength = length if length <= dsp.mstf(80) else dsp.mstf(dsp.rand(40, 80))
    else:
        blength = length

    wf = dsp.breakpoint([0] + [ dsp.rand(-1,1) for _ in range(dsp.randint(8, 20)) ] + [0], 512)

    bloop = dsp.mix([ keys.pulsar(bf, blength, wf=wf, amp=dsp.rand(0.1, 0.25)) for bf in [ bfreq, bfreq / 2, bfreq * 2 ] ])
    bloop = dsp.env(bloop, 'phasor')

    bloop = dsp.fill(bloop, length, silence=True)

    return bloop

while elapsed < tlength:
    print 'Rendering section %s...' % count

    layers = []

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

    layers += [ bar ]

    snarep = '..x.'
    pattern = ctl.parseBeat(snarep)
    snares = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeSnare)
    layers += [ snares ]

    kickp = 'x.......'
    pattern = ctl.parseBeat(kickp)
    kicks = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeKick)
    layers += [ kicks ]

    sm = dsp.fill(smash, dsp.flen(bar))
    sm = dsp.mix([ dsp.alias(sm), fx.penv(sm) ])
    sm = dsp.amp(sm, dsp.rand(0.5, 1))
    sk = dsp.fill(skitter, dsp.flen(bar))
    sk = fx.penv(sk)

    if count > 8:
        layers += [ sm, sk ]

    if count % 4 == 0:
        layers += [ dsp.pad(flam, dsp.flen(bar) - dsp.flen(flam), 0) ]

    key = 'e'
    octave = 1

    # Look ma, harmonic motion!
    progression = 'i i v IV IV6'.split(' ')
    cname = progression[ count % len(progression) ]
    swells = dsp.mix([ makeSwells(cname, nswell, dsp.flen(bar), key, octave) for nswell in [8,4] ])
    layers += [ swells ]

    bfreqs = tune.chord(cname, key, 2)
    bloopp = 'x.x.--------' if dsp.rand() > 0.5 else 'xxx.--------'
    bloopp = bloopp if dsp.rand() > 0.65 else 'xxx.----'
    pattern = ctl.parseBeat(bloopp)
    bloops = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeBloop, bfreqs)
    
    if count > 4:
        layers += [ bloops ]

    bar = dsp.mix(layers)

    out += bar

    elapsed += dsp.flen(bar)
    count += 1

dsp.write(out, '03-study.ix')
