import wx

import pylsdj.bread_spec as spec
from WavePanel import WavePanel
import channels

from StaticTextViewField import StaticTextViewField


class WavesPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.wave_panels = []

        for i in xrange(spec.NUM_SYNTHS):
            self.wave_panels.append(WavePanel(self, i))

        self.wave_slider = wx.Slider(
            self, wx.ID_ANY, 0, 0, spec.WAVES_PER_SYNTH - 1)

        self.frame_number = StaticTextViewField(self, lambda x: "%02x" % (x))

        self.Bind(wx.EVT_SCROLL, self.handle_scroll, self.wave_slider)

        channels.SYNTH_CHANGE(parent.project).subscribe(
            self.handle_synth_changed)

        sizer = wx.BoxSizer(wx.VERTICAL)

        map(lambda x: sizer.Add(x, 1, wx.ALL | wx.EXPAND), self.wave_panels)

        slider_sizer = wx.BoxSizer(wx.HORIZONTAL)

        slider_sizer.Add(wx.StaticText(self, label="Frame Number: "))
        self.frame_number.add_to_sizer(slider_sizer, 0, wx.ALL)
        slider_sizer.Add(self.wave_slider, 1, wx.ALL | wx.ALIGN_LEFT)

        sizer.Add(slider_sizer)

        self.SetSizer(sizer)

        self.show_wave_panel(0)

    def handle_synth_changed(self, data):
        self.show_wave_panel(0)

    def field_changed(self):
        pass

    def handle_scroll(self, event):
        val = self.wave_slider.GetValue()
        self.show_wave_panel(val)

    def show_wave_panel(self, index):
        if self.wave_slider.GetValue() != index:
            self.wave_slider.SetValue(index)

        self.frame_number.update(index)

        for i in xrange(len(self.wave_panels)):
            if i == index:
                self.wave_panels[i].Show()
            else:
                self.wave_panels[i].Hide()

        self.Layout()
