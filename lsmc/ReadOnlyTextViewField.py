import wx

from ViewField import ViewField


class ReadOnlyTextViewField(ViewField):

    def __init__(self, parent, format_fn):
        ViewField.__init__(
            self, parent, wx.StaticText(parent))
        self.format_fn = format_fn

    def update(self, data):
        instr = data

        self.field.SetLabel(self.format_fn(instr))
        super(ReadOnlyTextViewField, self).update(data)
