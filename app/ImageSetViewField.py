import wx

from ViewField import ViewField

class ImageSetViewField(ViewField):
    def __init__(self, parent, attr_fn, image_array):
        empty_img = wx.BitmapFromImage(wx.EmptyImage(
            image_array[0].GetWidth(), image_array[0].GetHeight()))
        ViewField.__init__(
            self, parent, wx.StaticBitmap(parent, wx.ID_ANY, empty_img))
        self.image_array = image_array
        self.attr_fn = attr_fn

    def update(self, data):
        instr = data

        self.field.SetBitmap(wx.BitmapFromImage(
            self.image_array[self.attr_fn(instr)]))
        super(ImageSetViewField, self).update(data)
