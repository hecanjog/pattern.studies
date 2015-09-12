from pippi import dsp, tune
import ctl

out = ''

kick = dsp.read('samples/jess/kickshuffle.wav').data

def makeKick(length, i):
    return dsp.fill(dsp.amp(kick, dsp.rand(1, 5)), length, silence=True)

nchords = 12
npulses = 200
nlayers = 3

for _ in range(nchords):
    layers = []

    for _ in range(nlayers):
        layer = ''
        highs = dsp.breakpoint([ dsp.rand(60, 15000) for _ in range(npulses / 50) ], npulses)
        lows = [ dsp.rand(20, freq) for freq in highs ]
        amps = dsp.breakpoint([ dsp.rand(0.1, 0.3) for _ in range(npulses / 50) ], npulses)
        pans = dsp.breakpoint([ dsp.rand(0, 1) for _ in range(npulses / 10) ], npulses)
        lengths = [ dsp.mstf(l) for l in dsp.breakpoint([ dsp.rand(1, 30) for _ in range(npulses / 10) ], npulses) ]

        for high, low, amp, pan, length in zip(highs, lows, amps, pans, lengths):
            p = dsp.bln(length, low, high, wform=dsp.randchoose(['hann', 'sine2pi', 'tri']))
            p = dsp.env(p, 'hann')
            p = dsp.taper(p, 20)
            p = dsp.amp(p, amp)
            p = dsp.pan(p, pan)

            layer += p

        layers += [ layer ]

    freqs = tune.fromdegrees([dsp.randint(1, 9) for _ in range(nlayers)], octave=1, root='a')

    for i, freq in enumerate(freqs):
        layers[i] = dsp.pine(layer, dsp.flen(layer) * 10, freq)

    section = dsp.mix(layers)

    plen = dsp.randint(16, 32)
    pattern = dsp.eu(plen, dsp.randint(4, plen))
    pattern = [ 'x' if h == 1 else '.' for h in pattern ]
    beat = dsp.flen(section) / plen
    kicks = ctl.makeBeat(pattern, [ beat for _ in range(plen) ], makeKick)

    out += dsp.mix([ kicks, section ])

dsp.write(out, '04-study.x')
