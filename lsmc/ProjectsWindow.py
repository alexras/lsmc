import wx
import functools
import event_handlers
from ObjectListView import ColumnDefn

from ProjectModel import ProjectModel

import utils
from SongWindow import SongWindow

import channels

class ProjectsWindow(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        # List the projects in the currently loaded .sav
        self.sav_project_list = utils.new_obj_list_view(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.open_song,
                  self.sav_project_list)

        self.sav_project_list.SetEmptyListMsg("No .sav loaded")

        # Keep track of the projects to whose channels you're subscribing to
        # avoid subscribing multiple times
        self.subscribed_projects = {}

        def string_getter(x, attr):
            if x[1] is None:
                return "--"
            else:
                obj_attr = getattr(x[1], attr)

                if isinstance(obj_attr, (int, float, long, complex)):
                    return utils.printable_decimal_and_hex(obj_attr)
                else:
                    return obj_attr

        index_col = ColumnDefn("#", "center", 30, "index_str")

        mod_col = ColumnDefn("Modified", "center", 60, "modified")

        name_col = ColumnDefn(
            "Song Name", "left", 200, "name", isSpaceFilling=True)
        name_col.freeSpaceProportion = 2

        version_col = ColumnDefn(
            "Version", "left", 50, "version", isSpaceFilling=True)
        version_col.freeSpaceProportion = 1

        size_col = ColumnDefn(
            "Size (Blocks)", "left", 100, "size", isSpaceFilling=True)
        size_col.freeSpaceProportion = 1

        self.sav_project_list.SetColumns(
            [mod_col, index_col, name_col, version_col, size_col])

        self.open_sav_button = self.new_button(
            "Open .sav File ...", event_handlers.open_sav)

        self.save_sav_button = self.new_button(
            "Save .sav File as ...", event_handlers.save_sav,
            start_disabled=True)

        self.add_song_button = self.new_button(
            "Add Song from .lsdsng ...", event_handlers.add_song,
            start_disabled=True)

        self.add_srm_button = self.new_button(
            "Add Song from .srm ...", event_handlers.add_srm,
            start_disabled=True)

        self.export_song_button = self.new_button(
            "Export Selected as .lsdsng ...", event_handlers.save_song,
            start_disabled=True)

        self.export_song_srm_button = self.new_button(
            "Export Selected as .srm ...", event_handlers.save_song_srm,
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
        add_side_button(self.add_srm_button)
        buttons_layout.AddSpacer(20)

        add_side_button(self.open_song_button)
        add_side_button(self.export_song_button)
        add_side_button(self.export_song_srm_button)

        window_layout = wx.BoxSizer(wx.HORIZONTAL)
        window_layout.Add(self.sav_project_list, 1, wx.EXPAND | wx.ALL)
        window_layout.AddSpacer(10)
        window_layout.Add(buttons_layout)
        window_layout.AddSpacer(10)

        self.SetSizer(window_layout)

    def handle_sav_loaded(self, sav_obj):
        project_list = sav_obj.project_list

        project_views = []

        for (index, project) in sorted(project_list):
            project_views.append(
                ProjectModel(self.sav_project_list, index, project))

            channels.SONG_MODIFIED(index).subscribe(self.handle_song_modified)

        self.sav_project_list.SetObjects(project_views)

        self.modified_since_load = False

    def handle_song_modified(self, data=None):
        if data is None:
            return

        self.modified_since_load = True

    def handle_save_song(self, event, projects_window, main_window):
        song_to_save = self.sav_project_list.GetSelectedObject().project
        event_handlers.save_song_dialog(song_to_save, "save_lsdsng", "lsdsng")

    def add_song(event, projects_window, main_window):
        index, sav_obj = event_handlers.get_song_from_windows(
            projects_window, main_window)

        def ok_handler(dlg, path):
            try:
                proj = event_handlers.load_lsdsng(path)
                sav_obj.projects[index] = proj
            except Exception, e:
                utils.show_error_dialog(
                    "can't load file", 'Error loading file: %s' % (e),
                    None)

        utils.file_dialog("Open .lsdsng", "*.lsdsng", wx.OPEN, ok_handler)

        main_window.update_models()

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

    def handle_song_selection_changed(self, event):
        selected_objects = self.sav_project_list.GetSelectedObjects()

        full_song_buttons = [
            self.export_song_button, self.export_song_srm_button,
            self.open_song_button]
        empty_song_buttons = [self.add_song_button, self.add_srm_button]

        if len(selected_objects) > 0:
            if len(filter(lambda x: x.project is None, selected_objects)) > 0:
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

    def handle_close(self, event):
        try:
            if self.modified_since_load:
                message = (
                    'Some songs have been modified. Unsaved changes to the '
                    '.sav file will be lost. Save the .sav file '
                    'before closing?')
                title = ('Save .sav file?')

                save_prompt = wx.MessageDialog(
                    self, message, title, wx.YES_NO | wx.ICON_QUESTION)

                if save_prompt.ShowModal() == wx.ID_YES:
                    event_handlers.save_sav_dialog(
                        self.GetGrandParent().sav_obj)
        finally:
            self.Destroy()

    def open_song(self, event):
        selected_objects = self.sav_project_list.GetSelectedObjects()

        if len(selected_objects) != 1:
            return

        proj = selected_objects[0].project

        if proj is None:
            return

        SongWindow(self, proj, selected_objects[0].index)
