# Imports
import os

import pydotplus as pydotplus
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel
import wx.lib.scrolledpanel as scrolled

# Local Imports
from shutil import copyfile
from WindowEditor import *
from DecisionTree import *

wildcard = "Portable Network Graphics (*.png)|*.png"


class DecisionTreeWindow(wx.Frame):

    def __init__(self, parent, wDB, labels, actions, p):
        wx.Frame.__init__(self, parent, -1, "Árbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(300, 210)
        self.Centre()
        self.actions = actions
        self.pbutton = p
        self.data = wDB
        self.db = []
        self.target = []
        self.getData()
        self.labels = labels
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        self.H1 = wx.BoxSizer(wx.HORIZONTAL)
        self.H2 = wx.BoxSizer(wx.HORIZONTAL)
        titleLabel = wx.StaticText(self.pnl, label="Nombre del árbol: ")
        titleTex = wx.TextCtrl(self.pnl, value="")

        mlLabel = wx.StaticText(self.pnl, label="Limite maximo de niveles:")
        self.mlC = wx.SpinCtrl(self.pnl, value="100", style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=100)
        mmLabel = wx.StaticText(self.pnl, label="Mín de muestras requeridas por hoja:")
        self.mmC = wx.SpinCtrl(self.pnl, value="1", style=wx.SP_ARROW_KEYS, min=1, max=100, initial=1)

        hbox = wx.BoxSizer()
        hbox.Add(titleLabel, proportion=0, flag=wx.RIGHT, border=5)
        hbox.Add(titleTex, proportion=1, flag=wx.EXPAND)
        self.baseSizer.Add(hbox, -1, wx.EXPAND | wx.ALL, 5)
        self.H1.Add(mlLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.H1.Add(self.mlC, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.H1, -1, wx.EXPAND | wx.ALL, 5)
        self.H2.Add(mmLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.H2.Add(self.mmC, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.H2, -1, wx.EXPAND | wx.ALL, 5)

        applyButton = wx.Button(self.pnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.dtree)
        self.baseSizer.Add(applyButton, -1, wx.EXPAND | wx.ALL, 5)

        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Destroy()

    def ReDo(self, actions, eegs):
        dtree = DecisionTree(self.db, self.target, self.labels, self.mlC.GetValue(), self.mmC.GetValue())
        tv = treeView(self, dtree)

    def dtree(self, event):
        self.actions = [self.mlC.GetValue(), self.mmC.GetValue()]
        dtree = DecisionTree(self.db, self.target, self.labels, self.mlC.GetValue(), self.mmC.GetValue())

        tv = treeView(self, dtree)
        tv.Show()

    def getData(self):
        data = self.data
        for r in range(len(data)):
            t = []
            for c in range(len(data[r]) - 1):
                t.append(data[r][c])
            self.db.append(t)
        for r in range(len(data)):
            self.target.append(data[r - 1][len(data[r]) - 1])



class treeView(wx.Frame):

    def __init__(self, parent, dtree):
        wx.Frame.__init__(self, parent, -1, "Arbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.Centre()
        self.Maximize()
        basePanel = wx.Panel(self, size=(300, 1000), style=wx.TAB_TRAVERSAL)
        baseSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.imgPanel = scrolled.ScrolledPanel(basePanel, size=(2000, 2000), style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.imgPanel.SetBackgroundColour(wx.WHITE)
        self.imgPanel.SetAutoLayout(1)
        self.imgPanel.SetupScrolling()
        self.imgSizer = wx.BoxSizer(wx.HORIZONTAL)

        pydotplus.graph_from_dot_data(dtree.dotfile.getvalue()).write_png("tree.png")
        png = wx.Image("tree.png", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.StaticBitmap(self.imgPanel, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))

        opcPanel = wx.Panel(basePanel, size=(300, 1000), style=wx.TAB_TRAVERSAL)
        opcSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(opcPanel, label="Opciones: ")
        applyButton = wx.Button(opcPanel, label="Salvar como .PNG")
        applyButton.Bind(wx.EVT_BUTTON, self.OnSave)

        opcPanel.SetSizer(opcSizer)
        opcSizer.Add(infoLabel)
        opcSizer.Add(applyButton)

        self.imgPanel.SetSizer(self.imgSizer)
        self.imgSizer.Add(bitmap, 0, wx.EXPAND | wx.ALL, 5)

        baseSizer.Add(opcPanel, 0, wx.EXPAND | wx.ALL, 5)
        baseSizer.Add(self.imgPanel, 0, wx.EXPAND | wx.ALL, 5)
        basePanel.SetSizer(baseSizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        os.remove("tree.png")
        self.Destroy()

    def OnSave(self, event):
        dlg = wx.FileDialog(self, "Guardar como", os.getcwd(), "", wildcard, \
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            copyfile("tree.png", path)
