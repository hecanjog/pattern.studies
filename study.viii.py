from pippi import dsp, tune
from hcj import fx
import math
import orc.wes

guitars = [ dsp.read('samples/guitar%s.wav' % (i + 1)).data for i in range(5) ]

# Intro
##########

def makeShape():
    shape = []

    num_shapelets = dsp.randint(3, 8)

    for _ in range(num_shapelets):
        shapelet_size = dsp.randint(20, 100)
        num_points = dsp.randint(4, shapelet_size / dsp.randint(3, 4))
        shapelet = dsp.breakpoint([ dsp.rand() for _ in range(num_points) ], shapelet_size)

        shape += shapelet

    return shape

def makeGrains():
    guitar = dsp.randchoose(guitars)
    guitar = dsp.transpose(guitar, dsp.randchoose([1, 2, 3, 4, 8]))

    max_grain_length = dsp.mstf(dsp.rand(10, 500))

    positions = [ math.floor(pos * (dsp.flen(guitar) - max_grain_length)) for pos in makeShape() ]
    lengths = [ math.floor(length * (max_grain_length - 1) + 1) for length in makeShape() ]
    pans = makeShape()
    amps = [ amp * dsp.rand(0, 10) for amp in makeShape() ]

    num_grains = dsp.randint(500, 1000)

    grains = []

    for i in range(num_grains):
        grain = dsp.cut(guitar, positions[ i % len(positions) ], lengths[ i % len(lengths) ])
        grain = dsp.pan(grain, pans[ i % len(pans) ])
        grain = dsp.amp(grain, amps[ i % len(amps) ])
        grain = dsp.taper(grain, 20)

        grains += [ grain ]

    return ''.join(grains)

wes = fx.spider(orc.wes.fetch())

intro = dsp.mix([ dsp.amp(makeGrains(), dsp.rand(0.01, 0.2)) for _ in range(dsp.randint(5, 10)) ])
intro = wes + dsp.env(intro, 'phasor')

# Buildup
##########

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

sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq, amp=0.4) ]
sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq * 1.067, amp=0.4) ]
sines += [ dsp.tone((dsp.flen(out) / 4) * 3, lowfreq * 1.667, amp=0.25) ]

sines = [ dsp.mix([ fx.penv(s), s ]) for s in sines ]

sines = dsp.mix(sines)
sines = dsp.env(sines, 'line')
sines = dsp.pad(sines, dsp.flen(out) - dsp.flen(sines), 0)

out = dsp.mix([ intro, out, sines ])

dsp.write(out, '01-friction_i')
