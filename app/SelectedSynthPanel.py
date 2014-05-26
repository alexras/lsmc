import wx
from wx.lib.pubsub import pub

import channels

from ImageSetViewField import ImageSetViewField
from ReadOnlyTextViewField import ReadOnlyTextViewField
from viewutils import instr_attr, one_digit_hex_format, two_digit_hex_format, \
    within

WAVE_IMAGES = {
    "sawtooth": wx.Image("images/synth_saw.gif", wx.BITMAP_TYPE_GIF),
    "square": wx.Image("images/synth_square.gif", wx.BITMAP_TYPE_GIF),
    "sine": wx.Image("images/synth_sine.gif", wx.BITMAP_TYPE_GIF)
}

class SelectedSynthPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        pub.subscribe(self.handle_synth_changed, channels.SYNTH_CHANGE)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_params_sizer = wx.FlexGridSizer(cols=2, hgap=20, vgap=7)

        self.wave_type = ImageSetViewField(
            self, instr_attr("waveform"), WAVE_IMAGES)
        self.filter_type = ReadOnlyTextViewField(
            self, instr_attr("filter_type"))
        self.resonance = ReadOnlyTextViewField(
            self, one_digit_hex_format("filter_resonance"))
        self.distortion = ReadOnlyTextViewField(
            self, instr_attr("distortion"))
        self.phase_type = ReadOnlyTextViewField(
            self, instr_attr("phase_type"))

        self.add_field("Wave", self.wave_type, main_params_sizer)
        self.add_field("Filter", self.filter_type, main_params_sizer)
        self.add_field("Q", self.resonance, main_params_sizer)
        self.add_field("Dist", self.distortion, main_params_sizer)
        self.add_field("Phase", self.phase_type, main_params_sizer)

        self.sizer.Add(main_params_sizer, 1, wx.ALL | wx.EXPAND)

        self.range_fields = {
            "start": [],
            "end": []
        }

        for range_param in self.range_fields.keys():
            range_param_sizer = wx.FlexGridSizer(cols=2, hgap=20, vgap=7)

            volume = ReadOnlyTextViewField(
                self, within(range_param, two_digit_hex_format("volume")))
            filter_cutoff = ReadOnlyTextViewField(
                self, within(range_param, two_digit_hex_format(
                    "filter_cutoff")))
            phase_amount = ReadOnlyTextViewField(
                self, within(range_param, two_digit_hex_format(
                    "phase_amount")))
            vertical_shift = ReadOnlyTextViewField(
                self, within(range_param, two_digit_hex_format(
                    "vertical_shift")))

            self.range_fields[range_param].extend(
                [volume, filter_cutoff, phase_amount, vertical_shift])

            self.add_field("Volume", volume, range_param_sizer)
            self.add_field("Cutoff", filter_cutoff, range_param_sizer)
            self.add_field("Phase", phase_amount, range_param_sizer)
            self.add_field("VShift", vertical_shift, range_param_sizer)

            self.sizer.Add(range_param_sizer, 1, wx.ALL | wx.EXPAND)

        # Wave
        # Filter
        # Q
        # Dist
        # Phase
        # Start volume, cutoff, phase, vshift
        # End volume, cutoff, phase, vshift

        self.SetSizer(self.sizer)
        self.Layout()

    def field_changed(self):
        pass

    def handle_synth_changed(self, data):
        synth = data
        self.Layout()

    def add_field(self, label_text, control, sizer):
        label = wx.StaticText(self, label=label_text)

        sizer.Add(label, 0, wx.ALL)

        control.subscribe(channels.SYNTH_CHANGE)

        control.add_to_sizer(sizer, 0, wx.ALL)
