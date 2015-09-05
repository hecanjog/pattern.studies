from pippi import dsp, tune
from hcj import fx
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

def makeSnare(length, i):
    return dsp.fill(snare, length, silence=True)

def makeKick(length, i):
    k = dsp.randchoose([ kickhard, kicksoft ])
    return dsp.fill(k, length, silence=True)

while elapsed < tlength:
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
    bar = dsp.mix([ bar, sm, sk, snares, kicks ])

    if count % 4 == 0:
        bar = dsp.mix([ bar, dsp.pad(flam, dsp.flen(bar) - dsp.flen(flam), 0) ])

    out += bar

    elapsed += dsp.flen(bar)
    count += 1

dsp.write(out, 'study.ix')
