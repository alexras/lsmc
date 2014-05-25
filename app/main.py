#!/usr/bin/env python

import wxversion
wxversion.ensureMinimal('2.8')

import wx, functools, event_handlers
from ObjectListView import ColumnDefn

import utils

import common.utils as cu

app = wx.App(False)

from InstrumentPane import InstrumentPane
from SynthPane import SynthPane
from TablePane import TablePane

class SongWindow(wx.Frame):
    def __init__(self, parent, project):
        frame_size = (650,550)

        wx.Frame.__init__(
            self, parent, wx.ID_ANY, "Song - %s" % (project.name),
            size=frame_size, pos=utils.random_pos(frame_size),
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        panel = wx.Panel(self)

        self.notebook = wx.Notebook(panel, wx.ID_ANY, style=wx.BK_DEFAULT)
        self.project = project

        instrument_pane = InstrumentPane(self.notebook, project)
        synth_pane = SynthPane(self.notebook, project)
        table_pane = TablePane(self.notebook, project)

        self.notebook.AddPage(instrument_pane, "Instruments")
        self.notebook.AddPage(synth_pane, "Synths")
        self.notebook.AddPage(table_pane, "Tables")

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.notebook, 1, flag=wx.ALL | wx.EXPAND, border=5)

        panel.SetSizer(sizer)

        self.Layout()
        self.Show()

class ProjectsWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # List the projects in the currently loaded .sav
        self.sav_project_list = utils.new_obj_list_view(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_song, self.sav_project_list)


        self.sav_project_list.SetEmptyListMsg("No .sav loaded")

        def string_getter(x, attr):
            if x[1] is None:
                return "--"
            else:
                obj_attr = getattr(x[1], attr)

                if isinstance(obj_attr, (int, float, long, complex)):
                    return cu.printable_decimal_and_hex(obj_attr)
                else:
                    return obj_attr
        index_col = ColumnDefn("#", "left", 40, lambda x: "%02d" % (x[0] + 1))

        name_col = ColumnDefn(
            "Song Name", "left", 200,
            functools.partial(string_getter, attr="name"), isSpaceFilling=True)
        name_col.freeSpaceProportion = 2

        version_col = ColumnDefn(
            "Version", "left", 50,
            functools.partial(string_getter, attr="version"),
            isSpaceFilling=True)
        version_col.freeSpaceProportion = 1

        size_col = ColumnDefn(
            "Size (Blocks)", "left", 100,
            functools.partial(string_getter, attr="size_blks"),
            isSpaceFilling=True)

        size_col.freeSpaceProportion = 1
        self.sav_project_list.SetColumns(
            [index_col, name_col, version_col, size_col])

        self.open_sav_button = self.new_button(
            "Open .sav File ...", event_handlers.open_sav)

        self.save_sav_button = self.new_button(
            "Save .sav File as ...", event_handlers.save_sav,
            start_disabled=True)

        self.add_song_button = self.new_button(
            "Add Song as .lsdsng ...", event_handlers.add_song,
            start_disabled=True)

        self.export_song_button = self.new_button(
            "Export Selected as .lsdsng ...", event_handlers.save_song,
            start_disabled=True)

        self.open_song_button = self.new_button(
            "Open Song ...", self.open_song, start_disabled=True,
            internal_handler=True)

        self.Bind(
            wx.EVT_LIST_ITEM_SELECTED, self.handle_song_selection_changed,
            self.sav_project_list)
        self.Bind(
            wx.EVT_LIST_ITEM_DESELECTED, self.handle_song_selection_changed,
            self.sav_project_list)

        buttons_layout = wx.BoxSizer(wx.VERTICAL)

        def add_side_button(btn):
            buttons_layout.Add(btn, 1, flag=wx.EXPAND | wx.ALL)
            buttons_layout.AddSpacer(10)

        buttons_layout.AddSpacer(20)
        add_side_button(self.open_sav_button)
        add_side_button(self.save_sav_button)
        buttons_layout.AddSpacer(20)

        add_side_button(self.add_song_button)
        buttons_layout.AddSpacer(20)

        add_side_button(self.open_song_button)
        add_side_button(self.export_song_button)

        window_layout = wx.BoxSizer(wx.HORIZONTAL)
        window_layout.Add(self.sav_project_list, 1, wx.EXPAND | wx.ALL)
        window_layout.AddSpacer(10)
        window_layout.Add(buttons_layout)
        window_layout.AddSpacer(10)

        self.SetSizer(window_layout)

    def new_button(self, label, evt_button_handler, start_disabled=False,
                   internal_handler=False):
        btn = wx.Button(self, wx.ID_ANY, label=label)

        if start_disabled:
            btn.Disable()

        if internal_handler:
            handler = evt_button_handler
        else:
            handler = functools.partial(
                evt_button_handler, projects_window=self,
                main_window=self.GetGrandParent())

        self.Bind(wx.EVT_BUTTON, handler, btn)

        return btn

    def update_models(self):
        self.sav_project_list.SetObjects(
            self.GetGrandParent().sav_obj.project_list)

    def handle_song_selection_changed(self, event):
        selected_objects = self.sav_project_list.GetSelectedObjects()

        full_song_buttons = [self.export_song_button, self.open_song_button]
        empty_song_buttons = [self.add_song_button]

        if len(selected_objects) > 0:
            if len(filter(lambda x: x[1] is None, selected_objects)) > 0:
                map(lambda x: x.Disable(), full_song_buttons)
                map(lambda x: x.Enable(), empty_song_buttons)
            else:
                map(lambda x: x.Enable(), full_song_buttons)
                map(lambda x: x.Disable(), empty_song_buttons)
        else:
            map(lambda x: x.Disable(), full_song_buttons)
            map(lambda x: x.Disable(), empty_song_buttons)

        # Make sure event propagation can continue
        event.Skip()

    def open_song(self, event):
        selected_objects = self.sav_project_list.GetSelectedObjects()

        if len(selected_objects) != 1:
            return

        proj = selected_objects[0][1]

        if proj is None:
            return

        song_window = SongWindow(self, proj)

class MainMenuBar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent = parent

        file_menu = wx.Menu()
        open_menu_item = file_menu.Append(
            wx.ID_ANY, "&Open .sav ...", "Open a .sav file")

        self.Bind(wx.EVT_MENU,
                  functools.partial(
                      event_handlers.open_sav,
                      main_window=parent,
                      projects_window=parent.songs_window),
                  open_menu_item)

        self.Append(file_menu, "&File")

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(
            self, None, wx.ID_ANY, "LSDJ .sav Utils", size=(600,400),
            style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.sav_obj = None

        panel = wx.Panel(self)
        self.songs_window = ProjectsWindow(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.songs_window, 1, flag=wx.ALL|wx.EXPAND, border=10)

        panel.SetSizer(sizer)

        self.SetMenuBar(MainMenuBar(self))

        # Display
        self.Layout()
        self.Show()

    def set_sav(self, sav_obj):
        self.sav_obj = sav_obj
        self.songs_window.sav_project_list.SetObjects(sav_obj.project_list)
        self.songs_window.save_sav_button.Enable()

    def get_sav(self):
        return self.sav_obj

    def update_models(self):
        self.songs_window.update_models()


starting_window = MainWindow()
app.MainLoop()
