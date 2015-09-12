from pippi import dsp, tune
from hcj import keys

notes = []
numnotes = 55

for _ in range(numnotes):
    n = keys.rhodes(dsp.mstf(dsp.rand(200, 300)), 900)

    #n = dsp.benv(n, [0,0.1,0.6,0.8,1,0.9,0.9,0.85,0.8,0.75,0.7,0.5,0.4,0.3,0.2,0])

    if dsp.rand() < 0.1:
        n = dsp.drift(n, 0.1)

    notes += [ n ]

filtered = []

for i, n in enumerate(notes):
    if dsp.rand() > 0.5 and i != 0:
        filtered[-1] += n
    else:
        filtered += [ n ]

for i, n in enumerate(filtered):
    nn = keys.rhodes(dsp.flen(n), 700)

    filtered[i] = dsp.mix([n, nn])

out = ''.join(filtered)

dsp.write(out, '05-study.xi')
