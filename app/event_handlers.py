import wx, os

import common.savfile as cs
import common.project as cp

def open_sav(event, projects_window, main_window):
    # Display an open dialog box so the user can select a .sav file
    dlg = wx.FileDialog(None, "Choose a .sav file", '.', '',
                        '*.sav', wx.OPEN)

    if dlg.ShowModal() == wx.ID_OK:
        sav_file_path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())

        # When loading the .sav file, we'll update a progress dialog box
        progress_dlg = wx.ProgressDialog(
            "Loading %s" % (sav_file_path), "Starting import ...", 100)

        sav_obj = None

        def progress_update_function(message, step, total_steps, still_working):
            progress_dlg.Update((step * 100) / total_steps, newmsg = message)

        try:
            sav_obj = cs.SAVFile(sav_file_path,
                                 callback=progress_update_function)
        except ValueError, e:
            show_error_dialog("Failed to load '%s'" % (dlg.GetFilename()),
                              str(e))

        if sav_obj is not None:
            main_window.set_sav(sav_obj)
            main_window.update_models()
            progress_dlg.Destroy()

    dlg.Destroy()

def save_sav(event, projects_window, main_window):
    dlg = wx.FileDialog(None, "Save .sav as ...", '.', '', "*.sav", wx.SAVE)

    if dlg.ShowModal() == wx.ID_OK:
        sav_file_path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())

        progress_dlg = wx.ProgressDialog(
            "Saving %s" % (sav_file_path), "Reticulating splines", 100)

        def progress_update_function(message, step, total_steps, still_working):
            progress_dlg.Update((step * 100) / total_steps, newmsg = message)

        main_window.sav_obj.save(
            sav_file_path, callback=progress_update_function)

def save_song(event, projects_window, main_window):
    song_to_save = projects_window.sav_project_list.GetSelectedObject()[1]

    dlg = wx.FileDialog(
        None, "Save '%s'" % (song_to_save.name), '.', '', "*.lsdsng", wx.SAVE)

    if dlg.ShowModal() == wx.ID_OK:
        song_file_path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())

        song_to_save.save(song_file_path)

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

    dlg = wx.FileDialog(None, "Open .lsdsng", '.', '', "*.lsdsng", wx.OPEN)

    if dlg.ShowModal() == wx.ID_OK:
        song_file_path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
        proj = cp.load_project(song_file_path)
        sav_obj.projects[index] = proj

    main_window.update_models()

def show_error_dialog(caption, msg, parent):
    errorWindow = wx.MessageDialog(parent, msg, "Error - " + caption)

    errorWindow.ShowModal()
