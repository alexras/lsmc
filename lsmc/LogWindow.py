import sys

import wx


class RedirectText(object):

    def __init__(self, aWxTextCtrl):
        self.out = aWxTextCtrl

    def write(self, string):
        wx.CallAfter(self.out.WriteText, string)


class LogWindow(wx.Frame):

    def __init__(self, initial_position):
        frame_size = (500, 300)

        wx.Frame.__init__(
            self, None, wx.ID_ANY, "Console Log",
            size=frame_size,
            pos=initial_position)

        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
        log = wx.TextCtrl(
            panel, wx.ID_ANY, size=(300, 100),
            style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        # Add widgets to a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(log, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

        # redirect text here
        redir = RedirectText(log)
        sys.stdout = redir
        sys.stderr = redir


def open_log_window(event, main_window):
    offsets = (20, 10)

    main_window_pos = main_window.GetPosition()

    log_window = LogWindow(
        (main_window_pos[0] + main_window.GetSize()[0] + offsets[0],
         main_window_pos[1] + offsets[1]))

    log_window.Show()
