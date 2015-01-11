import wx

from ViewField import ViewField


class ImageSetViewField(ViewField):

    def __init__(self, parent, attr_fn, images):
        if isinstance(images, list):
            first_image = images[0]
        elif isinstance(images, dict):
            first_image = images[images.keys()[0]]

        empty_img = wx.BitmapFromImage(wx.EmptyImage(
            first_image.GetWidth(), first_image.GetHeight()))

        ViewField.__init__(
            self, parent, wx.StaticBitmap(parent, wx.ID_ANY, empty_img))
        self.images = images
        self.attr_fn = attr_fn

    def update(self, data):
        instr = data

        self.field.SetBitmap(wx.BitmapFromImage(
            self.images[self.attr_fn(instr)]))
        super(ImageSetViewField, self).update(data)
