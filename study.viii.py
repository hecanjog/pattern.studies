from pippi import dsp, tune
from hcj import fx

guitars = [ dsp.read('samples/guitar%s.wav' % (i + 1)).data for i in range(5) ]

layers = []
nlayers = 3
length = dsp.stf(120)

for _ in range(nlayers):
    frags = []
    elapsed = 0

    while elapsed < length:
        # pick a fragment
        g = dsp.randchoose(guitars)

        # transpose to A
        g = dsp.transpose(g, 1.125)

        # rand octave or 5th transpose
        g = dsp.transpose(g, dsp.randchoose([1, 1.5, 2]))

        # slice fragment btwn 60ms and 1/2 frag length
        fraglen = dsp.mstf(dsp.rand(60, dsp.flen(g) / 2))
        pos = dsp.randint(0, dsp.flen(g) - fraglen)
        g = dsp.cut(g, pos, fraglen)

        # attenuate
        g = dsp.amp(g, dsp.rand(0.1, 0.5))

        # randomly pan
        g = dsp.pan(g, dsp.rand())

        # add frag length to elapsed time
        elapsed += dsp.flen(g)

        # add fragment to frag list
        frags += [ g ]

    # concat all frags
    layer = ''.join(frags)

    # add frags to layers
    layers += [ layer ]

# mix down frag layers
out = dsp.mix(layers)

# Add sine buildup

sines = []

lowfreq = tune.ntf('g', octave=2)

sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq, 0.5) ]
sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq * 1.067, 0.5) ]
sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq * 1.667, 0.25) ]

sines = [ dsp.mix([ fx.penv(s), s ]) for s in sines ]

sines = dsp.mix(sines)
sines = dsp.env(sines, 'line')
sines = dsp.pad(sines, dsp.flen(out) - dsp.flen(sines), 0)

out = dsp.mix([ out, sines ])

dsp.write(out, 'study.viii')
