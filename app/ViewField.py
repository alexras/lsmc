from wx.lib.pubsub import pub

class ViewField(object):
    def __init__(self, parent, field):
        self.parent = parent
        self.field = field

    def subscribe(self, channel):
        pub.subscribe(self.update, channel)

    def update(self, data):
        self.parent.field_changed()

    def add_to_sizer(self, sizer, *args, **kwargs):
        sizer.Add(self.field, *args, **kwargs)
