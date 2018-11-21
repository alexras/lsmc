import wx
from ObjectListView import ColumnDefn, ObjectListView

import channels

import utils

from NoInstrumentSelectedPanel import NoInstrumentSelectedPanel
from PulseInstrumentPanel import PulseInstrumentPanel
from WaveInstrumentPanel import WaveInstrumentPanel
from KitInstrumentPanel import KitInstrumentPanel
from NoiseInstrumentPanel import NoiseInstrumentPanel


class InstrumentPane(wx.Panel):

    def __init__(self, parent, project, index):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.instr_list = utils.new_obj_list_view(
            self, edit_mode=ObjectListView.CELLEDIT_DOUBLECLICK)
        self.instr_list.SetEmptyListMsg("Loading instrument list ...")
        self.selected_instrument = None

        def instr_name_printer(x):
            name = getattr(x, "name")

            if utils.name_empty(name):
                return "[UNNAMED]"
            else:
                return name

        song_modified_channel = channels.SONG_MODIFIED(index)

        def name_setter(instrument, new_name):
            instrument.name = new_name.upper()[:5]
            song_modified_channel.publish(self.project)

        id_col = ColumnDefn("#", "center", 30, lambda x: "%02x" %
                            (getattr(x, "index")), isEditable=False)
        name_col = ColumnDefn(
            "Name", "left", 200, instr_name_printer, isSpaceFilling=True,
            valueSetter=name_setter)


        type_col = ColumnDefn("Type", "left", 50, "type", isSpaceFilling=True,
                              isEditable=False)
        self.instr_list.SetColumns([id_col, name_col, type_col])

        self.update_instr_list()

        self.instr_panels = {
            None: NoInstrumentSelectedPanel(self),
            "pulse": PulseInstrumentPanel(self),
            "wave": WaveInstrumentPanel(self),
            "kit": KitInstrumentPanel(self),
            "noise": NoiseInstrumentPanel(self)
        }

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_instr_changed,
                  self.instr_list)

        channel = channels.INSTR_IMPORT(project)

        channel.subscribe(self.handle_instr_changed)
        channel.subscribe(self.update_instr_list)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        sizer.Add(self.instr_list, 0, wx.ALL | wx.EXPAND, border=5)

        for panel in self.instr_panels.values():
            sizer.Add(panel, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.show_instr_panel(None)

    def update_instr_list(self, data=None):
        self.instr_list.SetObjects(self.project.song.instruments.as_list())

    def refresh(self):
        self.update_instr_list()

    def show_instr_panel(self, instrument):
        instr_type = None

        if instrument is not None:
            instr_type = instrument.type

        for (key, val) in self.instr_panels.items():
            if key == instr_type:
                val.Show()
                val.change_instrument(instrument)
            else:
                val.Hide()

        self.Layout()

    def handle_instr_changed(self, data=None):
        if data is None:
            return

        selected_instruments = self.instr_list.GetSelectedObjects()

        instrument = None

        if len(selected_instruments) > 0:
            instrument = selected_instruments[0]

        if instrument.index == self.selected_instrument:
            return

        self.selected_instrument = instrument.index

        if (instrument is not None and
            self.project.song.instruments[instrument.index] is not None):

            instrument = self.project.song.instruments[instrument.index]

        self.show_instr_panel(instrument)
