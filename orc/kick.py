from pippi import dsp
from hcj import snds

kick = snds.load('mc303/kick1.wav')
bigkick = snds.load('mc303/kick2.wav')
#bigkick = dsp.read('snds/kick606.wav').data

def make(length, i):
    return dsp.taper(dsp.fill(dsp.mix([ bigkick, kick ]), length, silence=True), 40)

