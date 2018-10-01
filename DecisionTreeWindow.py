# Imports
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel

# Local Imports
from WindowEditor import *
from DecisionTree import *


class DecisionTreeWindow(wx.Frame):

    def __init__(self, parent, wDB, labels, actions, p):
        wx.Frame.__init__(self, parent, -1, "Árbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(300, 250)
        self.Centre()
        self.actions = actions
        self.pbutton = p
        self.data = wDB
        self.labels = labels
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        self.H1 = wx.BoxSizer(wx.HORIZONTAL)
        self.H2 = wx.BoxSizer(wx.HORIZONTAL)
        titleLabel = wx.StaticText(self.pnl, label="Nombre: ")
        titleTex = wx.TextCtrl(self.pnl, value="")

        mlLabel = wx.StaticText(self.pnl, label="Limite maximo de niveles:")
        self.mlC = wx.SpinCtrl(self.pnl, value="100", style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=100)
        mmLabel = wx.StaticText(self.pnl, label="Mín de muestras requeridas por hoja:")
        self.mmC = wx.SpinCtrl(self.pnl, value="1", style=wx.SP_ARROW_KEYS, min=1, max=100, initial=1)

        self.baseSizer.Add(titleLabel, -1, wx.EXPAND, 5)
        self.baseSizer.Add(titleTex, -1, wx.EXPAND | wx.ALL, 5)
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
        # TODO fix when module finished
        pass

    def dtree(self, event):
        self.actions = [self.mlC.GetValue(), self.mmC.GetValue()]
        data = self.data
        self.db = []
        self.target = []
        for r in range(len(data)):
            t = []
            for c in range(len(data[r]) - 1):
                t.append(data[r][c])
            self.db.append(t)
        for r in range(len(data)):
            self.target.append(data[r-1][len(data[r])-1])
        dtree = DecisionTree(self.db, self.target)
        print("")
        tv = treeView(self, dtree)
        tv.Show()


class treeView(wx.Frame):

    def __init__(self, parent, dtree):
        wx.Frame.__init__(self, parent, -1, "Arbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(300, 250)
        self.Centre()
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)

        tree = wx.TreeCtrl()
        tree.AddRoot("tree",data=dtree)

        self.baseSizer.Add(tree,0, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
