#!/usr/bin/env python

import wx, functools, event_handlers
from ObjectListView import ObjectListView, ColumnDefn

import utils

import common.utils as cu

app = wx.App(False)

class ProjectsWindow(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # List the projects in the currently loaded .sav
        self.sav_project_list = ObjectListView(
            self, wx.ID_ANY, style=wx.LC_REPORT)
        utils.enable_single_selection(self.sav_project_list, self)

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

        self.open_sav_button = wx.Button(
            self, wx.ID_ANY, label="Open .sav File ...")

        self.save_sav_button = wx.Button(
            self, wx.ID_ANY, label="Save .sav File as ...")
        self.save_sav_button.Disable()

        self.add_proj_button = wx.Button(
            self, wx.ID_ANY, label="Add Song as .lsdsng ...")
        self.add_proj_button.Disable()

        self.export_proj_button = wx.Button(
            self, wx.ID_ANY, label="Export Selected as .lsdsng ...")
        self.export_proj_button.Disable()

        self.Bind(wx.EVT_BUTTON,
                  functools.partial(event_handlers.save_sav, main_window=self),
                  self.save_sav_button)
        self.Bind(wx.EVT_BUTTON,
                  functools.partial(event_handlers.open_sav, main_window=self),
                  self.open_sav_button)
        self.Bind(wx.EVT_BUTTON,
                  functools.partial(event_handlers.add_song, main_window=self),
                  self.add_proj_button)
        self.Bind(wx.EVT_BUTTON,
                  functools.partial(event_handlers.save_song, main_window=self),
                  self.export_proj_button)

        self.Bind(
            wx.EVT_LIST_ITEM_SELECTED, self.handle_song_selection_changed,
            self.sav_project_list)
        self.Bind(
            wx.EVT_LIST_ITEM_DESELECTED, self.handle_song_selection_changed,
            self.sav_project_list)

        buttons_layout = wx.BoxSizer(wx.VERTICAL)

        def add_side_button(btn):
            buttons_layout.Add(btn, 0, flag=wx.EXPAND)
            buttons_layout.AddSpacer(10)

        add_side_button(self.open_sav_button)
        add_side_button(self.save_sav_button)
        buttons_layout.AddSpacer(30)

        add_side_button(self.add_proj_button)
        add_side_button(self.export_proj_button)

        window_layout = wx.BoxSizer(wx.HORIZONTAL)
        window_layout.Add(self.sav_project_list, 1, wx.EXPAND | wx.ALL)
        window_layout.AddSpacer(10)
        window_layout.Add(buttons_layout)
        window_layout.AddSpacer(10)

        self.SetSizer(window_layout)

    def update_models(self):
        self.sav_project_list.SetObjects(
            self.GetGrandParent().sav_obj.project_list)

    def handle_song_selection_changed(self, event):
        selected_objects = self.sav_project_list.GetSelectedObjects()

        if len(selected_objects) > 0:
            self.export_proj_button.Enable()

            if len([x for x in selected_objects if x[1] is None]) > 0:
                self.add_proj_button.Enable()
                self.export_proj_button.Disable()
        else:
            self.add_proj_button.Disable()
            self.export_proj_button.Disable()

        # Make sure event propagation can continue
        event.Skip()

class MainNotebook(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.sav_obj = None

        self.songs_window = ProjectsWindow(self)

        self.AddPage(self.songs_window, "Songs")

        # Event binding
        # self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)
        # self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)

class MainMenuBar(wx.MenuBar):
    def __init__(self, parent):
        wx.MenuBar.__init__(self)
        self.parent = parent

        file_menu = wx.Menu()
        open_menu_item = file_menu.Append(
            wx.ID_ANY, "&Open .sav ...", "Open a .sav file")

        self.Bind(wx.EVT_MENU, functools.partial(
            event_handlers.open_sav, main_window=parent), open_menu_item)

        self.Append(file_menu, "&File")

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "LSDJ .sav Utils",
                          size=(600,400))

        self.sav_obj = None

        panel = wx.Panel(self)
        self.songs_window = ProjectsWindow(panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.songs_window, 1, wx.ALL|wx.EXPAND, 5)

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
