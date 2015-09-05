from pippi import dsp, tune
from hcj import fx

tlength = dsp.stf(60 * 3)

out = ''
elapsed = 0

dloop = dsp.read('samples/jess/loop2.wav').data
kicksoft = dsp.read('samples/jess/kickshuffle.wav').data
kickhard = dsp.read('samples/jess/kickcym.wav').data
snare = dsp.read('samples/jess/snare.wav').data
flam = dsp.read('samples/jess/snareflam.wav').data
smash = dsp.read('samples/jess/smash.wav').data

while elapsed < tlength:
    bar = ''

    bar += dsp.mix([ dloop, kickhard ])
    bar += dsp.mix([ dloop, kicksoft ])
    bar += dsp.mix([ dloop, kicksoft ])

    bar = dsp.mix([ bar, dsp.fill(smash, dsp.flen(bar)) ])

    out += bar

    elapsed += dsp.flen(bar)

dsp.write(out, 'study.ix')
