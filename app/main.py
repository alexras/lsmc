#!/usr/bin/env python

import wxversion
wxversion.ensureMinimal('2.8')

import wx, functools, event_handlers
from ObjectListView import ColumnDefn

import utils

import common.utils as cu

app = wx.App(False)

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
