from rich_comparable_mixin import RichComparableMixin

class Synth(RichComparableMixin):
    """The wave channel can be used as a soft synthesizer to generate sounds."""
    def __init__(self, raw_synth):
        self.waves = []
        self.waveform = raw_synth.waveform
        self.filter_type = raw_synth.filter_type
        self.filter_resonance = raw_synth.filter_resonance
        self.distortion = raw_synth.distortion
        self.phase_type = raw_synth.phase_type
        self.start_sound = raw_synth.start
        self.end_sound = raw_synth.end
