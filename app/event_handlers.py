import wx, os

def open_sav(event, songs_window):
    # Display an open dialog box so the user can select a .sav file
    dlg = wx.FileDialog(None, "Choose a .sav file", '.', '',
                        '*.sav', wx.OPEN)

    if dlg.ShowModal() == wx.ID_OK:
        sav_file_path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())



    dlg.Destroy()
