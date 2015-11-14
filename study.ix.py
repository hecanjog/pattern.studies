from pippi import dsp, tune
from hcj import fx, keys, snds, drums, Sampler
import ctl

tlength = dsp.stf(60 * 5)

out = ''
elapsed = 0
count = 1 

dloop2 = dsp.read('samples/jess/loop2.wav').data

dloop1 = dsp.read('samples/jess/loop1.wav').data
dloop1 = dsp.fill(dloop1, dsp.flen(dloop2))

kicksoft = dsp.read('samples/jess/kickshuffle.wav').data
kickhard = dsp.read('samples/jess/kickcym.wav').data
rimshot = dsp.read('samples/jess/rimshot.wav').data
rimshot = dsp.amp(rimshot, 4)
snare = dsp.read('samples/jess/snare.wav').data
snare = dsp.amp(snare, 3)
flam = dsp.read('samples/jess/snareflam.wav').data
flam = dsp.amp(flam, 3)
smash = dsp.read('samples/jess/smash.wav').data
skitter = dsp.read('samples/jess/skitter.wav').data
paper = snds.load('hits/papersnap.wav')

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

def makeArps(length, beat, cname):
    freqs = tune.chord(cname, key, dsp.randint(1,4))
    tone = Sampler(snds.load('tones/nick.wav'), direction='fw-bw-loop', tails=False)
    freqs = dsp.randshuffle(freqs)

    beat = int((beat * 2) / dsp.randchoose([0.5, 1, 2, 3, 1.5]))

    numbeats = length / beat

    out = ''

    for i in range(numbeats):
        out += tone.play(freqs[i % len(freqs)], beat) 

    out = dsp.fill(out, length)

    return out


def makeRhodes(length, beat, freqs):
    chord = [ keys.rhodes(length, freq, dsp.rand(0.4, 0.6)) for freq in freqs ]
    chord = dsp.randshuffle(chord)
    pause = 0
    for i, c in enumerate(chord):
        pause = pause + (dsp.randint(1, 4) * beat)
        c = dsp.pan(c, dsp.rand())
        chord[i] = dsp.pad(dsp.fill(c, length - pause), pause, 0)

    return dsp.mix(chord)

def makeSnare(length, i):
    return dsp.fill(snare, length, silence=True)

def makeRimshot(length, i):
    r = dsp.transpose(rimshot, dsp.rand(0.9, 1.1))
    return dsp.fill(r, length, silence=True)

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

    bloop = dsp.mix([ keys.pulsar(bf, blength, wf=wf, amp=dsp.rand(0.1, 0.5)) for bf in [ bfreq, bfreq / 2, bfreq * 2 ] ])
    bloop = dsp.env(bloop, 'phasor')

    bloop = dsp.fill(bloop, length, silence=True)

    return bloop

while elapsed < tlength:
    print 'Rendering section %s...' % count

    layers = []

    bar = ''

    key = 'e'
    octave = 1

    bar += dsp.mix([ dsp.randchoose([ dloop1, dloop2 ]), kickhard ])
    bar += dsp.mix([ dsp.randchoose([ dloop1, dloop2 ]), kicksoft ])
    bar += dsp.mix([ dsp.randchoose([ dloop1, dloop2 ]), kicksoft ])

    # Look ma, harmonic motion!
    progression = 'i i v IV IV6'.split(' ')
    progression = ('i i v IV IV6 ' * 4) + 'v9 v9 ii7 vi9 IV69 ' + ('i i v IV IV6 ' * 2) + 'v9 v9 ii7 ii7 vi9 IV69 IV69'

    progression = progression.split(' ')
    breaks = ('v9', 'ii7', 'vi9', 'IV69')
    cname = progression[ count % len(progression) ]

    if elapsed > dsp.stf(40) and cname not in breaks:
        swells = dsp.mix([ makeSwells(cname, nswell, dsp.flen(bar), key, octave) for nswell in [8,4] ])
        layers += [ swells ]


    if cname == 'IV' or cname == 'vi9' or cname == 'IV69':
        numbeats = 16 + (4 * dsp.randint(2, 4))
    else:
        numbeats = 16


    beat = dsp.flen(bar) / 16
    bar = dsp.split(bar, beat)
    bar = [ bar[i % len(bar)] for i in range(numbeats) ]
    bar = dsp.randshuffle(bar)
    for i, b in enumerate(bar):
        if dsp.rand() > 0.75:
            bar[i] = dsp.pad('', 0, dsp.flen(b))
        elif dsp.rand() > 0.75:
            bar[i] = dsp.split(b, dsp.flen(b) / 2)[0] * 2

        bar[i] = dsp.amp(bar[i], dsp.rand(0.9, 2))

    bar = ''.join(bar)

    if cname in breaks:
        rushes = [ drums.roll(dsp.randchoose([paper, smash, snare, rimshot, kickhard]), dsp.flen(bar), dsp.randint(1, 3)) for _ in range(3) ]
        layers += [ dsp.amp(dsp.mix(rushes), 0.5)]

    if elapsed > dsp.stf(20) and cname not in breaks:
        layers += [ bar ]

    if elapsed > dsp.stf(40) and cname not in breaks:
        snarep = '..x.'
        pattern = ctl.parseBeat(snarep)
        snares = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeSnare)
        snares = dsp.amp(snares, dsp.rand(2,4))
        layers += [ snares ]

    rimshotp = '....x...'
    pattern = ctl.parseBeat(rimshotp)
    rimshots = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeRimshot)
    if elapsed > dsp.stf(40) and cname not in breaks:
        if dsp.rand() > 0.75:
            rimshots = dsp.amp(drums.roll(rimshot, dsp.flen(bar), dsp.randint(2, 6)), dsp.rand(0.4, 1))

    if elapsed > dsp.stf(5) and cname not in breaks:
        layers += [ rimshots ]

    if dsp.rand() > 0.25 and cname not in breaks:
        kickp = 'x.......'
        pattern = ctl.parseBeat(kickp)
        kicks = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeKick)
        kicks = dsp.amp(kicks, dsp.rand(2,4))
        layers += [ kicks ]

    if dsp.rand() > 0.5 and elapsed > dsp.stf(90) and cname not in breaks:
        sm = dsp.fill(smash, dsp.flen(bar))
        sm = dsp.mix([ dsp.alias(sm), fx.penv(sm) ])
        sm = dsp.amp(sm, dsp.rand(0.5, 1))
        sk = dsp.fill(skitter, dsp.flen(bar))
        sk = fx.penv(sk)

        layers += [ sm, sk ]

    if count % 4 == 0:
        layers += [ dsp.pad(flam, dsp.flen(bar) - dsp.flen(flam), 0) ]

    bfreqs = tune.chord(cname, key, 2)
    bloopp = 'x.x.--------' if dsp.rand() > 0.5 else 'xxx.--------'
    bloopp = bloopp if dsp.rand() > 0.65 else 'xxx.----'
    pattern = ctl.parseBeat(bloopp)
    bloops = ctl.makeBeat(pattern, [ beat for _ in range(16) ], makeBloop, bfreqs)

    if elapsed > dsp.stf(40):
        layers += [ bloops ]

    rfreqs = tune.chord(cname, key, 2)
    rhodeses = makeRhodes(dsp.flen(bar), beat, rfreqs)
    layers += [ rhodeses ]

    if dsp.rand() > 0.5 and elapsed > dsp.stf(120) and cname in breaks:
        arpses = dsp.mix([ makeArps(dsp.flen(bar), beat, cname) for _ in range(2) ])
        layers += [ arpses ]

    layers += [ dsp.fill(dsp.amp(paper, dsp.rand(2, 4)), dsp.flen(bar), silence=True) ]

    bar = dsp.mix(layers)

    out += bar

    elapsed += dsp.flen(bar)
    count += 1

dsp.write(out, '03-study.ix')
