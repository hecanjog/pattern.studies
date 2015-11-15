from pippi import dsp, tune
from hcj import fx, keys, snds, drums, Sampler
import ctl

dloop2 = dsp.read('samples/jess/loop2.wav').data

dloop1 = dsp.read('samples/jess/loop1.wav').data
dloop1 = dsp.fill(dloop1, dsp.flen(dloop2))

kicksoft = dsp.read('samples/jess/kickshuffle.wav').data
kickhard = dsp.read('samples/jess/kickcym.wav').data
rimshot = dsp.read('samples/jess/rimshot.wav').data
rimshot = dsp.amp(rimshot, 4)

snare = dsp.read('samples/jess/snare.wav').data
snare = dsp.amp(snare, 3)
snare2 = snds.load('hits/hisnarespa.wav')
snare2 = dsp.amp(snare2, 0.25)

clap = snds.load('hits/tapeclap.wav')
clap = dsp.amp(clap, 0.25)

flam = dsp.read('samples/jess/snareflam.wav').data
flam = dsp.amp(flam, 3)
smash = dsp.read('samples/jess/smash.wav').data
skitter = dsp.read('samples/jess/skitter.wav').data
paper = snds.load('hits/papersnap.wav')
#sock = snds.load('hits/sockbass.wav')
sock = snds.load('hits/detroitkick1.wav')
hat = snds.load('hits/keyshihat.wav')

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
    out = fx.penv(out)

    return out


def makeRhodes(length, beat, freqs, maxbend=0.05):
    backup = Sampler(snds.load('tones/nycrhodes01.wav'), tune.ntf('c'), direction='fw-bw-loop', tails=False)
    chord = [ keys.rhodes(length, freq, dsp.rand(0.4, 0.7)) for freq in freqs ]
    chord = dsp.randshuffle(chord)
    chord = [ dsp.mix([ dsp.env(fx.penv(backup.play(freq * 2**dsp.randint(0,2), length, dsp.rand(0.4, 0.6))), 'line'), c ]) for freq, c in zip(freqs, chord) ]
    pause = 0
    for i, c in enumerate(chord):
        pause = pause + (dsp.randint(1, 4) * beat)
        c = dsp.pan(c, dsp.rand())
        c = fx.bend(c, [ dsp.rand() for _ in range(dsp.randint(5, 10)) ], dsp.rand(0, maxbend))
        chord[i] = dsp.pad(dsp.fill(c, length - pause), pause, 0)

    return dsp.mix(chord)

def makeHat(length, i):
    h = dsp.env(dsp.fill(hat, dsp.flen(hat) / 3), 'phasor')
    h = dsp.amp(h, 0.3)
    h = dsp.mix([ h, dsp.pad(dsp.transpose(h, dsp.rand(1.51, 2.03)), dsp.randint(1, 44), 0) ])
    return dsp.fill(h, length, silence=True)

def makeSnare(length, i):
    s = dsp.mix([ dsp.randchoose([snare, snare2, clap]) for _ in range(3) ])
    s = dsp.fill(s, dsp.randint(dsp.flen(s)/2, dsp.flen(s)))
    s = dsp.env(s, 'phasor')
    s = dsp.amp(s, dsp.rand(0.9,1))
    return dsp.fill(s, length, silence=True)

def makeRimshot(length, i):
    return dsp.fill(rimshot, length, silence=True)

def makeKick(length, i):
    k = dsp.randchoose([ kickhard, kicksoft ])
    k = dsp.mix([ k, dsp.env(sock, 'phasor') ])
    if dsp.rand() > 0.4:
        k = dsp.env(k, 'phasor')

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

def makePaper(out):
    tail = dsp.cut(paper, dsp.mstf(60), dsp.flen(out) - dsp.mstf(60))

    tail = [ dsp.transpose(tail, dsp.rand(0.95, 1.05)) for _ in range(dsp.randint(3,6)) ]
    tail = [ fx.penv(t) for t in tail ]

    out = dsp.mix(tail + [ out ])
    
    return out

tlength = dsp.stf(dsp.rand(60 * 8, 60 * 12))

out = ''
elapsed = 0
count = 1 
float_played = 0

section_choices = {
    'intro': (['intro'] * 3) + (['stasis'] * 2),
    'buildup': ['verse', 'buildup'],
    'stasis': (['intro'] * 2) + ['buildup'] + (['stasis'] * 2),
    'verse': ['verse'] * 2 + ['chorus'],
    'chorus': ['chorus'] * 2 + ['bridge'],
    'bridge': ['bridge', 'chorus', 'stasis', 'float'],
    'float': ['intro', 'buildup', 'stasis'],
}

section_defs = {
    'intro': ['prog1', 'hats'],
    'buildup': ['prog1', 'choppy', 'hats', 'rims', 'kicks', 'smashes'],
    'stasis': ['prog1', 'choppy', 'hats', 'smashes'],
    'verse': ['prog1', 'snares', 'choppy', 'swells', 'hats', 'rims', 'kicks', 'bloops'],
    'chorus': ['prog2', 'rushes', 'rims', 'smashes', 'arps', 'bloops'],
    'bridge': ['prog3', 'snares', 'rushes', 'choppy', 'hats', 'rims', 'kicks', 'smashes', 'arps', 'bloops'],
    'float': ['prog2', 'arps', 'bloops', 'swells', 'hats'],
}

def forceChange(section):
    last_section = section
    section = nextSection(section)
    if last_section == section:
        section = forceChange(section)
    return section

def forceAway(section, forced):
    section = nextSection(section)
    if forced == section:
        section = forceAway(section, forced)
    return section

def nextSection(section):
    global float_played
    section = dsp.randchoose(section_choices[section])
    if section == 'float' and float_played > 2:
        section = forceAway(section, 'float')
    elif section == 'float':
        float_played += 1

    return section

def canPlay(inst, section):
    return inst in section_defs[section]

section = 'intro'
reps = 0

while elapsed < tlength:
    last_section = section
    section = nextSection(section)

    if reps > 5:
        section = forceChange(section)

    if last_section == section:
        reps += 1
    else:
        reps = 0

    if elapsed > dsp.stf(60 * 4) and not float_played:
        section = 'float'
        float_played += 1

    print 'Rendering section %s... %s' % (count, section)

    layers = []

    # Look ma, harmonic motion!
    progression = ('i i v IV IV6 ' * 4) + 'v9 v9 ii7 vi9 IV69 ' + ('i i v IV IV6 ' * 2) + 'v9 v9 ii7 ii7 vi9 IV69 IV69'
    progression = progression.split(' ')

    if canPlay('prog1', section):
        progression = 'i i v IV IV6'.split(' ')

    if canPlay('prog2', section):
        progression = 'v9 v9 ii7 vi9 IV69'.split(' ')

    if canPlay('prog3', section):
        progression = 'II7 II7 V69'.split(' ')

    cname = progression[ count % len(progression) ]

    if cname == 'IV' or cname == 'vi9' or cname == 'IV69':
        numbeats = 16 + (4 * dsp.randint(2, 4))
    else:
        numbeats = 16

    if section == 'float':
        numbeats = 16 * 16

    bpm = 84
    beat = dsp.bpm2frames(bpm) / 4
    bar_length = beat * numbeats

    bar = dsp.pad('', 0, bar_length)

    key = 'e'
    octave = 1

    dl = ''.join([ dsp.mix([ dsp.randchoose([ dloop1, dloop2 ]), dsp.randchoose([ kickhard, kicksoft ]) ]) for _ in range(3) ])
    dl = dsp.split(dl, dsp.flen(dl) / 16)
    dl = dsp.randshuffle(dl)
    dl = [ dsp.env(dd, 'phasor') for dd in dl ]
    for i, b in enumerate(dl):
        if dsp.rand() > 0.75:
            dl[i] = dsp.pad('', 0, dsp.flen(b))
        elif dsp.rand() > 0.75:
            dl[i] = dsp.split(b, dsp.flen(b) / 2)[0] * 2

        dl[i] = dsp.amp(dl[i], dsp.rand(0.9, 2))
        dl[i] = dsp.fill(dl[i], beat, silence=True)

    dl = ''.join(dl)
    if canPlay('choppy', section):
        layers += [ dl ]

    if canPlay('swells', section) or (section in ('intro', 'stasis') and dsp.rand() > 0.5):
        swells = dsp.mix([ makeSwells(cname, nswell, bar_length, key, octave) for nswell in [8,4] ])
        layers += [ swells ]

    if canPlay('rushes', section):
        rushes = [ drums.roll(dsp.randchoose([paper, smash, snare, rimshot, kickhard]), bar_length, dsp.randint(1, 3)) for _ in range(3) ]
        layers += [ dsp.amp(dsp.mix(rushes), 0.5)]

    if canPlay('snares', section):
        snarep = '....x...'
        if elapsed > dsp.stf(120) and dsp.rand() > 0.75:
            snarep = '....xx..'

        pattern = ctl.parseBeat(snarep)
        snares = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeSnare)
        snares = dsp.amp(snares, dsp.rand(2,4))
        layers += [ snares ]

    if canPlay('hats', section):
        hatp = 'x.x.'
        pattern = ctl.parseBeat(hatp)
        hats = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeHat)
        layers += [ hats ]

    if canPlay('rims', section):
        rimshotp = '....x...'
        pattern = ctl.parseBeat(rimshotp)
        rimshots = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeRimshot)
        if dsp.rand() > 0.75:
            rimshots = dsp.amp(drums.roll(rimshot, dsp.flen(bar), dsp.randint(2, 6)), dsp.rand(0.4, 1))

        layers += [ rimshots ]

    if canPlay('kicks', section):
        kickp = 'x.......'
        pattern = ctl.parseBeat(kickp)
        kicks = ctl.makeBeat(pattern, [ beat for _ in range(numbeats) ], makeKick)
        kicks = dsp.amp(kicks, dsp.rand(2,4))
        layers += [ kicks ]

    if canPlay('smashes', section):
        sm = dsp.fill(smash, dsp.flen(bar))
        sm = dsp.mix([ dsp.alias(sm), fx.penv(sm) ])
        sm = dsp.amp(sm, dsp.rand(0.5, 2))
        sk = dsp.fill(skitter, dsp.flen(bar))
        sk = fx.penv(sk)

        layers += [ sm, sk ]

    if count % 4 == 0:
        layers += [ dsp.pad(flam, dsp.flen(bar) - dsp.flen(flam), 0) ]

    if canPlay('bloops', section):
        bfreqs = tune.chord(cname, key, 2)
        bloopp = 'x.x.--------' if dsp.rand() > 0.5 else 'xxx.--------'
        bloopp = bloopp if dsp.rand() > 0.65 else 'xxx.----'
        pattern = ctl.parseBeat(bloopp)
        bloops = ctl.makeBeat(pattern, [ beat / 2 for _ in range(16) ], makeBloop, bfreqs)

        layers += [ bloops ]

    if canPlay('arps', section):
        arpses = dsp.mix([ makeArps(dsp.flen(bar), beat, cname) for _ in range(dsp.randint(2,4)) ])
        layers += [ arpses ]


    layers += [ dsp.fill(dsp.amp(makePaper(paper), dsp.rand(2, 4)), dsp.flen(bar), silence=True) ]

    rfreqs = tune.chord(cname, key, 2)
    maxbend = 0.005 if dsp.rand() > 0.1 else 0.03
    rhodeses = makeRhodes(dsp.flen(bar), beat, rfreqs, maxbend)
    layers += [ rhodeses ]

    bar = dsp.mix(layers)

    out += bar

    elapsed += dsp.flen(bar)
    count += 1

# ha ha
out += dsp.mix([ makeSwells(cname, nswell, bar_length, key, octave) for nswell in [8,4] ])

dsp.write(out, '03-study.ix')
