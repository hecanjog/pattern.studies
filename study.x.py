from pippi import dsp, tune

out = ''

npulses = 1000
lengths = [ dsp.mstf(l) for l in dsp.breakpoint([ dsp.rand(80, 400) for _ in range(npulses / 10) ], npulses) ]

layers = []

nlayers = 3

for _ in range(nlayers):
    layer = ''
    highs = dsp.breakpoint([ dsp.rand(60, 15000) for _ in range(npulses / 100) ], npulses)
    lows = [ dsp.rand(20, freq) for freq in highs ]
    amps = dsp.breakpoint([ dsp.rand(0.1, 0.3) for _ in range(npulses / 100) ], npulses)
    pans = dsp.breakpoint([ dsp.rand(0, 1) for _ in range(npulses / 10) ], npulses)

    for high, low, amp, pan, length in zip(highs, lows, amps, pans, lengths):
        p = dsp.bln(length, low, high, wform=dsp.randchoose(['hann', 'sine2pi', 'tri']))
        p = dsp.env(p, 'hann')
        p = dsp.taper(p, 20)
        p = dsp.amp(p, amp)
        p = dsp.pan(p, pan)

        layer += p

    layers += [ layer ]

out = dsp.mix(layers)

dsp.write(out, '04-study.x')
