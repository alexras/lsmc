import wx
import random
import os
from ObjectListView import ObjectListView
import traceback

import images.images as compiled_images
import dirs


def random_pos(window_dimensions):
    win_width, win_height = window_dimensions
    screen_width, screen_height = wx.DisplaySize()
    padding = 20

    max_x = screen_width - win_width - padding
    max_y = screen_height - win_height - padding

    if max_x < 0 or max_y < 0:
        show_error_dialog(
            "Screen Resolution Too Small",
            "Screen resolution must be at least %d x %d to display a song" %
            (win_width + padding, win_height + padding), None)
        return None

    return (random.randint(0, max_x), random.randint(0, max_y))


def show_error_dialog(caption, msg, parent):
    if isinstance(msg, Exception):
        msg = traceback.format_exc()

    print msg

    errorWindow = wx.MessageDialog(
        parent, msg, "Error - " + caption, wx.OK | wx.ICON_ERROR)
    errorWindow.ShowModal()


def new_obj_list_view(parent, edit_mode=ObjectListView.CELLEDIT_NONE):
    view = ObjectListView(
        parent, wx.ID_ANY, style=wx.LC_REPORT, cellEditMode=edit_mode)
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


def file_dialog(message, wildcard, style, ok_handler, default_file=''):
    last_opened_dir_file = os.path.join(dirs.CACHE_DIR, 'last_opened_dir')

    last_opened_dir = None

    if os.path.exists(last_opened_dir_file):
        with open(last_opened_dir_file, 'r') as fp:
            last_opened_dir = fp.read().strip()

    if last_opened_dir is None or len(last_opened_dir) == 0:
        last_opened_dir = os.path.expanduser('~')

    dlg = wx.FileDialog(
        None, message, last_opened_dir, default_file, wildcard, style)

    try:
        if dlg.ShowModal() == wx.ID_OK:
            last_opened_dir = dlg.GetDirectory()

            path = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            ok_handler(dlg, path)
    finally:
        dlg.Destroy()

    if not os.path.exists(dirs.CACHE_DIR):
        os.makedirs(dirs.CACHE_DIR)

    with open(last_opened_dir_file, 'w+') as fp:
        fp.write(last_opened_dir)


def make_image(image_name):
    assert image_name in compiled_images.catalog

    return compiled_images.catalog[image_name].GetImage()


def name_empty(name):
    return map(ord, name) == [0] * len(name)


def printable_decimal_and_hex(num):
    return "{0:d} (0x{0:x})".format(num)
