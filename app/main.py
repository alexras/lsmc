#!/usr/bin/env python

import wx

app = wx.App(False)

class OpenOrImportWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="LSDJ .sav Utils - Let's-a-Go!")

        self.SetBackgroundColour((255,255,255))

        # Set up window elements
        open_button = wx.Button(self, wx.ID_ANY, label="Open Existing")
        import_button = wx.Button(self, wx.ID_ANY, label="Import .sav Data")

        title_image = wx.Image("images/lsdj_logo.png")
        title_image_widget = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(title_image))

        # Configure element layout - image above buttons
        window_layout = wx.BoxSizer(wx.VERTICAL)

        window_layout.Add(title_image_widget, flag=wx.ALIGN_CENTER)

        button_layout = wx.BoxSizer(wx.HORIZONTAL)

        button_layout.Add(open_button, flag=wx.ALIGN_CENTER)
        button_layout.Add(import_button, flag=wx.ALIGN_CENTER)

        window_layout.Add(button_layout, flag=wx.ALIGN_CENTER)
        window_layout.AddSpacer(10)

        self.SetSizer(window_layout)
        # Resize the frame to fit the UI elements
        window_layout.Fit(self)

        # Event binding for buttons
        self.Bind(wx.EVT_BUTTON, self.on_open_button, open_button)
        self.Bind(wx.EVT_BUTTON, self.on_import_button, import_button)

        self.Show(True)

    def on_open_button(self, event):
        print "Open button pressed!"

    def on_import_button(self, event):
        print "Import button pressed!"

starting_window = OpenOrImportWindow()
app.MainLoop()
