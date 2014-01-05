import wx, os

import common.savfile as cs

def open_sav(event, main_window):
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
            print "PROGRESS! ", message, step, total_steps, still_working
            progress_dlg.Update((step * 100) / total_steps, newmsg = message)

        try:
            sav_obj = cs.SAVFile(sav_file_path,
                                 callback=progress_update_function)
        except ValueError, e:
            print "ERROR!", e

        if sav_obj is not None:
            main_window.update_models(sav_obj)
            progress_dlg.Destroy()

    dlg.Destroy()
