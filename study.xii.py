from pippi import dsp, tune
from hcj import drums, keys

ssnd = dsp.read('samples/jess/snare.wav').data
lssnd = dsp.read('samples/jess/rimshot.wav').data
hsnd = dsp.read('samples/jess/tamb_rattle.wav').data
ohsnd = dsp.read('samples/jess/skitter.wav').data
ksnd = dsp.read('samples/jess/kickshuffle.wav').data
bksnd = dsp.read('samples/jess/kickcym.wav').data
bksnd = dsp.mix([ bksnd, dsp.read('samples/jess/smash.wav').data ])

beat = dsp.bpm2frames(166)
key = 'b'

out = ''
elapsed = 0
count = 0

tlength = dsp.stf(120)

def makeRhodes(length, beat, freqs):
    root = tune.ntf(key, 2)

    for i, freq in enumerate(freqs):
        if freq > root * 2.5:
            freqs[i] = freq * 0.5

    chord = [ keys.rhodes(length, freq, dsp.rand(0.4, 0.6)) for freq in freqs ]
    chord = dsp.randshuffle(chord)
    pause = 0
    for i, c in enumerate(chord):
        pause = pause + (dsp.randint(1, 4) * beat)
        c = dsp.pan(c, dsp.rand())
        chord[i] = dsp.pad(dsp.fill(c, length - pause), pause, 0)

    chord = dsp.mix(chord)

    chord = dsp.split(chord, dsp.flen(chord) / 16)
    chord = dsp.randshuffle(chord)
    chord = [ dsp.env(ch, 'phasor') for ch in chord ]

    chord = [ dsp.mix([ dsp.amp(dsp.pan(grain, dsp.rand()), dsp.rand(0.1, 0.8)), dsp.amp(dsp.pan(dsp.randchoose(chord), dsp.rand()), dsp.rand(0.1, 0.8)) ]) for grain in chord ]
    chord = ''.join(chord)

    return chord


while elapsed < tlength:
    print 'rendering bar %s...' % (count + 1)
    length = beat * 8

    if dsp.rand() > 0.5:
        kick =   'x--x-x-x--------'
    else:
        kick =   'x----x----------'

    hat =    'x-x-x-x-xx-x-x-x'
    ohat =   'x------x--------'

    if dsp.rand() > 0.5:
        lsnare = '---------x--x---'
    else:
        lsnare = '--x--x--x--x--x-'

    if dsp.rand() > 0.5:
        snare =  '--x--x--x--xxxx-'
    else:
        snare =  '--x--x--x--x--x-'

    def makeOHat(length, i, amp):
        return dsp.fill(hsnd, length, silence=True)

    def makeHat(length, i, amp):
        h = dsp.fill(ohsnd, length)
        h = dsp.env(h, 'phasor')
        return h

    def makeKick(length, i, amp):
        k = dsp.fill(ksnd, length, silence=True)
        return dsp.amp(k, 3)

    def makeSnare(length, i, amp):
        s = dsp.fill(ssnd, length, silence=True)
        return dsp.amp(s, 3)

    def makeLSnare(length, i, amp):
        s = dsp.fill(lssnd, length, silence=True)
        return dsp.amp(s, 2)

    hats = drums.parsebeat(hat, 8, beat, length, makeHat, 5)
    ohats = drums.parsebeat(ohat, 8, beat, length, makeOHat, 0)
    kicks = drums.parsebeat(kick, 8, beat, length, makeKick, 0)
    snares = drums.parsebeat(snare, 8, beat, length, makeSnare, 0)
    lsnares = drums.parsebeat(lsnare, 8, beat, length, makeLSnare, 0)

    snaresnstuff = dsp.mix([ohats,snares])
    snaresnstuff= dsp.split(snaresnstuff, dsp.flen(snaresnstuff) / 32)
    snaresnstuff = dsp.randshuffle(snaresnstuff)
    snaresnstuff = [ dsp.env(sns, 'phasor') for sns in snaresnstuff ]
    snaresnstuff = ''.join(snaresnstuff)
    snaresnstuff = dsp.amp(snaresnstuff, 0.5)

    bar = dsp.mix([kicks,lsnares,snares,hats,ohats,snaresnstuff])
    #bar = dsp.mix([hats,ohats])

    if count % 4 == 0:
        bar = dsp.mix([ bar, dsp.fill(bksnd, dsp.flen(bar), silence=True) ])

    progression = 'ii6 ii69'.split(' ')
    cname = progression[ count % len(progression) ]
    rfreqs = tune.chord(cname, key, 2)
    rhodes = makeRhodes(dsp.flen(bar), beat / 8, rfreqs)

    out += dsp.mix([ bar, dsp.fill(rhodes, dsp.flen(bar)) ])
    #out += bar

    count += 1
    elapsed += dsp.flen(bar)

dsp.write(out, 'study.xii')
