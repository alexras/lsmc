import wx, time
from ObjectListView import ObjectListView

def new_obj_list_view(parent):
    view = ObjectListView(parent, wx.ID_ANY, style=wx.LC_REPORT)
    enable_single_selection(view, parent)
    view.oddRowsBackColor = wx.LIGHT_GREY

    return view

def _single_select_event_handler(event):
    view = event.GetEventObject()

    selected_objects = view.GetSelectedObjects()

    if len(selected_objects) > 1:
        view.DeselectAll()
        view.SelectObject(selected_objects[0])

def enable_single_selection(obj_list_view, window):
    window.Bind(wx.EVT_LIST_ITEM_SELECTED, _single_select_event_handler,
                obj_list_view)
