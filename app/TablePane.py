import wx
from ObjectListView import ColumnDefn

import utils

from common.table import Table
import common.bread_spec as spec

class TableRowView(object):
    def __init__(self, index, volume, transpose, command1, command1_params,
                 command2, command2_params):
        self.id = index
        self.volume = volume
        self.transpose = transpose
        self.cmd1 = command1
        self.cmd2 = command2
        self.cmd1_params = command1_params
        self.cmd2_params = command2_params

    def get_cmd_view(self, field):
        if field == "cmd1":
            command = self.cmd1
            params =  self.cmd1_params
        elif field == "cmd2":
            command = self.cmd2
            params = self.cmd2_params

        view = params

        if command == "O":
            if params == 1:
                view = "L"
            elif params == 2:
                view = "R"
            elif params == 3:
                view = "LR"
        elif command == "W":
            if params == 0:
                view = "12.5%"
            elif params == 1:
                view = "25%"
            elif params == 2:
                view = "50%"
            elif params == 3:
                view = "75%"
        else:
            view = "%02x" % (params)

        return view

def table_list_index_format(x):
    (index, table) = x

    index_string = "%02x" % (index)

    if table is None:
        index_string += " (unused)"

    return index_string

class TablePane(wx.Panel):
    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

        self.project = project

        self.table_list = utils.new_obj_list_view(self)
        self.table_list.SetEmptyListMsg("Loading table list ...")

        id_col = ColumnDefn("", "left", 30, table_list_index_format,
                            isSpaceFilling=True)

        self.table_list.SetColumns([id_col])
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.handle_table_changed,
                  self.table_list)

        self.table_list.SetObjects(list(enumerate(
            self.project.song.tables.as_list())))

        self.table_view = utils.new_obj_list_view(self)
        self.table_view.SetEmptyListMsg("No Table Selected")

        row_number = ColumnDefn("", "center", 30, lambda x: "%02x" %
                                (x.id), isSpaceFilling=True)

        volume = ColumnDefn("Vol", "center", 30, lambda x: "%02x" %
                            (x.volume))
        transpose = ColumnDefn("Tsp", "center", 30, lambda x: "%02x" %
                               (x.transpose))

        command1_fx = ColumnDefn("Cmd", "center", 40, lambda x: x.cmd1)
        command1_params = ColumnDefn(
            "", "center", 50, lambda x: x.get_cmd_view("cmd1"))
        command2_fx = ColumnDefn("Cmd", "center", 40, lambda x: x.cmd2)
        command2_params = ColumnDefn(
            "", "center", 50, lambda x: x.get_cmd_view("cmd2"))

        self.table_view.SetColumns(
            [row_number, volume, transpose, command1_fx, command1_params,
             command2_fx, command2_params])

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.sizer.Add(self.table_list, 1, wx.ALL | wx.EXPAND)
        self.sizer.AddSpacer(20)
        self.sizer.Add(self.table_view, 2, wx.ALL | wx.EXPAND)
        self.sizer.AddStretchSpacer()

        self.SetSizer(self.sizer)

    def handle_table_changed(self, event):
        selected_tables = self.table_list.GetSelectedObjects()
        table = None

        if len(selected_tables) > 0:
            index, table = selected_tables[0]

        self.show_table(table)

    def show_table(self, table):
        rows = []

        if table is None:
            # Construct an empty table view
            for i in xrange(spec.ENTRIES_PER_TABLE):
                rows.append(TableRowView(i, 0, 0, 0, 0, 0, 0))

        else:
            for i in xrange(spec.ENTRIES_PER_TABLE):
                rows.append(TableRowView(
                    i, table.envelopes[i], table.transposes[i], table.fx1[i],
                    table.fx1_vals[i], table.fx2[i], table.fx2_vals[i]))

        self.table_view.SetObjects(rows)
