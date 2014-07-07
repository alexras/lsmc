from wx.lib.pubsub import pub

class Channel(object):
    def __init__(self, name, domain=None):
        if domain is not None:
            self._pubsub_channel = name + '+' + repr(domain)
        else:
            self._pubsub_channel = name

    def subscribe(self, function):
        pub.subscribe(function, self._pubsub_channel)

    def publish(self, data):
        pub.sendMessage(self._pubsub_channel, data=data)

# This is essentially a poor man's functools.partial to allow channel
# declaration to look a little cleaner
def new_channel(name):
    def inner(domain):
        return Channel(name, domain)

    return inner

PULSE_CHANGE = new_channel("PULSE_CHANGE")
WAVE_CHANGE = new_channel("WAVE_CHANGE")
NOISE_CHANGE = new_channel("NOISE_CHANGE")
KIT_CHANGE = new_channel("KIT_CHANGE")

INSTR_IMPORT = new_channel("INSTR_IMPORT")

SYNTH_CHANGE = new_channel("SYNTH_CHANGE")
