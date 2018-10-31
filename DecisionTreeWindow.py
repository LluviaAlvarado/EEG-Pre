# Imports
from shutil import copyfile
import pydotplus as pydotplus
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel
import wx.lib.scrolledpanel as scrolled

from DecisionTree import *
from WindowEditor import *

wildcard = "Portable Network Graphics (*.png)|*.png"


class DecisionTreeWindow(wx.Frame):

    def __init__(self, parent, wDB, labels, p):
        wx.Frame.__init__(self, parent, -1, "Árbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(300, 210)
        self.Centre()
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
        mlLabel = wx.StaticText(self.pnl, label="Límite máximo de niveles:")
        self.mlC = wx.SpinCtrl(self.pnl, value="100", style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=100)
        mmLabel = wx.StaticText(self.pnl, label="Número de folds (Cross validation):")
        self.mmC = wx.SpinCtrl(self.pnl, value="3", style=wx.SP_ARROW_KEYS, min=1, max=100, initial=3)
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
        pass

    def dtree(self, event):
        self.GetParent().setStatus("Generando Árbol...", 1)
        self.pbutton.actions = [self.mlC.GetValue(), self.mmC.GetValue()]
        dtree = DecisionTree(self.db, self.target, self.labels, self.mlC.GetValue(), self.mmC.GetValue())
        tv = treeView(self, dtree)
        self.GetParent().setStatus("", 0)
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
        wx.Frame.__init__(self, parent, -1, "Árbol de decisión", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.Centre()
        self.Maximize()
        basePanel = wx.Panel(self, size=(300, 1000), style=wx.TAB_TRAVERSAL)
        baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.imgPanel = scrolled.ScrolledPanel(basePanel, size=(4000, 4000), style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.imgPanel.SetBackgroundColour(wx.WHITE)
        self.imgPanel.SetAutoLayout(1)
        self.imgPanel.SetupScrolling()
        self.imgSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.imgSizer.SetMinSize(4000, 4000)

        pydotplus.graph_from_dot_data(dtree.dotfile.getvalue()).write_png("tree.png")
        self.im = wx.Image("tree.png", wx.BITMAP_TYPE_ANY)
        self.size = self.im.GetSize()
        self.png = self.im.ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self.imgPanel, -1, self.png, (10, 5), (self.png.GetWidth(), self.png.GetHeight()))

        opcPanel = wx.Panel(basePanel, size=(300, 1000), style=wx.TAB_TRAVERSAL)
        b1 = wx.StaticText(opcPanel, 0, " ", style=wx.ALIGN_CENTER, pos=(2, 7), size=(200, 46))
        b1.SetBackgroundColour((0, 0, 0))
        b2 = wx.StaticText(opcPanel, 0, " ", style=wx.ALIGN_CENTER, pos=(3, 8), size=(198, 44))

        opcSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(opcPanel, label="Datos: ")
        train = wx.StaticText(opcPanel, label=dtree.ATr)
        opc = wx.StaticText(opcPanel, label="Opciones: ")
        zoomL = wx.StaticText(opcPanel, label="Zoom: ")
        applyButton = wx.Button(opcPanel, label="Guardar como (.PNG)")
        applyButton.Bind(wx.EVT_BUTTON, self.OnSave)
        #self.sp = wx.Slider(opcPanel, value=0, minValue=0, maxValue=1000)
        #self.sp.Bind(wx.EVT_COMMAND_SCROLL_CHANGED, self.zoom)
        opcPanel.SetSizer(opcSizer)
        opcSizer.Add(infoLabel)
        opcSizer.Add(train, border=15)
        opcSizer.AddSpacer(30)
        opcSizer.Add(opc, border=10)
        #opcSizer.Add(zoomL, border=10)
        #opcSizer.Add(self.sp, border=10)
        opcSizer.AddSpacer(10)
        opcSizer.Add(applyButton, border=10)
        self.imgPanel.SetSizer(self.imgSizer)
        self.imgSizer.Add(self.bitmap)

        baseSizer.Add(opcPanel, 0, wx.EXPAND | wx.ALL, 5)
        baseSizer.Add(self.imgPanel, 0, wx.EXPAND | wx.ALL, 5)
        basePanel.SetSizer(baseSizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        os.remove("tree.png")
        self.Destroy()

    def zoom(self, event):
        value = self.sp.GetValue()
        bit = self.im.Scale(self.size[0] + value, self.size[1] + value, wx.IMAGE_QUALITY_HIGH)
        self.bitmap.SetBitmap(bit.ConvertToBitmap())
        self.bitmap.SetSize(self.size[0] + value, self.size[1] + value)
        self.imgSizer.SetMinSize(self.size[0] + value, self.size[1] + value)
        self.imgPanel.AdjustScrollbars()

    def OnSave(self, event):
        dlg = wx.FileDialog(self, "Guardar como", os.getcwd(), "", wildcard, \
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            copyfile("tree.png", path)
