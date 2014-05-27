import wx, os

import common.savfile as cs
import common.project as cp

import utils

def open_sav(event, projects_window, main_window):
    def ok_handler(dlg, path):
        # When loading the .sav file, we'll update a progress dialog box
        progress_dlg = wx.ProgressDialog(
            "Loading %s" % (path), "Starting import ...", 100)

        sav_obj = None

        def progress_update_function(message, step, total_steps, still_working):
            progress_dlg.Update((step * 100) / total_steps, newmsg = message)

        try:
            sav_obj = cs.SAVFile(path, callback=progress_update_function)
        except ValueError, e:
            show_error_dialog("Failed to load '%s'" % (dlg.GetFilename()),
                              str(e))

        if sav_obj is not None:
            main_window.set_sav(sav_obj)
            main_window.update_models()
            progress_dlg.Destroy()

    # Display an open dialog box so the user can select a .sav file
    utils.file_dialog("Choose a .sav file", '*.sav', wx.OPEN, ok_handler)

def save_sav(event, projects_window, main_window):
    def ok_handler(dlg, path):
        progress_dlg = wx.ProgressDialog(
            "Saving %s" % (path), "Reticulating splines", 100)

        def progress_update_function(message, step, total_steps, still_working):
            progress_dlg.Update((step * 100) / total_steps, newmsg = message)

        main_window.sav_obj.save(path, callback=progress_update_function)

    utils.file_dialog("Save .sav as ...", "*.sav", wx.SAVE, ok_handler)

def save_song(event, projects_window, main_window):
    song_to_save = projects_window.sav_project_list.GetSelectedObject()[1]

    def ok_handler(dlg, path):
        song_to_save.save(path)

    utils.file_dialog(
        "Save '%s'" % (song_to_save.name), "*.lsdsng", wx.SAVE, ok_handler)

def add_song(event, projects_window, main_window):
    selected_obj = projects_window.sav_project_list.GetSelectedObject()
    index, current_proj = selected_obj

    if current_proj is not None:
        show_error_dialog(
            "Invalid Selection",
            "Song slot %d is currently occupied and cannot be saved over" %
            (index + 1))
        return

    sav_obj = main_window.get_sav()

    def ok_handler(dlg, path):
        proj = cp.load_project(path)
        sav_obj.projects[index] = proj

    utils.file_dialog("Open .lsdsng", "*.lsdsng", wx.OPEN, ok_handler)

    main_window.update_models()

def show_error_dialog(caption, msg, parent):
    errorWindow = wx.MessageDialog(parent, msg, "Error - " + caption)

    errorWindow.ShowModal()
