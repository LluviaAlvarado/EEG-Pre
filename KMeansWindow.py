# Imports
import matplotlib

matplotlib.use('WXAgg')
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# Local Imports
from WindowEditor import *
from KMeans import *
from sklearn.metrics import silhouette_samples, silhouette_score
from SilhouetteWindow import *


class KMeansWindow(wx.Frame):

    def __init__(self, parent, wDB, p):
        wx.Frame.__init__(self, parent, -1, "K-Means", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(230, 290)
        self.Centre()
        self.k = None
        self.pbutton = p
        self.data = []
        self.parent = wDB
        if wDB != None:
            self.data = wDB.windowDB
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        self.H1 = wx.BoxSizer(wx.HORIZONTAL)
        self.H2 = wx.BoxSizer(wx.HORIZONTAL)
        self.H3 = wx.BoxSizer(wx.HORIZONTAL)

        clusLabel = wx.StaticText(self.pnl, label="Numero de Clusters:")
        self.clusC = wx.SpinCtrl(self.pnl, value="8", style=wx.SP_ARROW_KEYS, min=1, max=100, initial=1)

        typeLabel = wx.StaticText(self.pnl, label="Tipo de inicialización")
        self.tipeC = wx.ComboBox(self.pnl, value='k-means++', style=wx.CB_READONLY, choices=['k-means++', 'random'])

        iterLabel = wx.StaticText(self.pnl, label="Interaciones:            ")
        self.iterC = wx.SpinCtrl(self.pnl, value="10", style=wx.SP_ARROW_KEYS, min=1, max=10000, initial=1)

        epochsLabel = wx.StaticText(self.pnl, label="Numero de epocas:")
        self.epochsC = wx.SpinCtrl(self.pnl, value="300", style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=1)

        applyButton = wx.Button(self.pnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.kmeans)

        self.viewButton = wx.Button(self.pnl, label="Visualizar")
        self.viewButton.Bind(wx.EVT_BUTTON, self.openview)
        self.viewButton.Disable()

        self.H3.Add(clusLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.H3.Add(self.clusC, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.H3, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(typeLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.tipeC, -1, wx.EXPAND | wx.ALL, 5)
        self.H1.Add(iterLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.H1.Add(self.iterC, -1, wx.EXPAND | wx.ALL, 1)
        self.baseSizer.Add(self.H1, -1, wx.EXPAND | wx.ALL, 5)
        self.H2.Add(epochsLabel, -1, wx.EXPAND | wx.ALL, 5)
        self.H2.Add(self.epochsC, -1, wx.EXPAND | wx.ALL, 1)
        self.baseSizer.Add(self.H2, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(applyButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Destroy()

    def ReDo(self, actions, eegs):
        self.db = []
        if self.data != []:
            for r in range(len(self.data)):
                t = []
                for c in range(len(self.data[r]) - 1):
                    t.append(self.data[r][c])
                self.db.append(t)
            self.k = KMeans(self.db, actions[0], actions[1], actions[2], actions[3])
            self.viewButton.Enable()

    def kmeans(self, event):
        self.db = []
        self.GetParent().setStatus("Aplicando K-means...", 1)
        for r in range(len(self.data)):
            t = []
            for c in range(len(self.data[r]) - 1):
                t.append(self.data[r][c])
            self.db.append(t)
        self.pbutton.actions = [self.clusC.GetValue(), self.tipeC.GetStringSelection(), self.iterC.GetValue(),
                                self.epochsC.GetValue()]
        self.k = KMeans(self.db, self.clusC.GetValue(), self.tipeC.GetStringSelection(), self.iterC.GetValue(),
                        self.epochsC.GetValue())
        self.parent.km = self.k
        self.viewButton.Enable()
        self.GetParent().setStatus("", 0)

    def openview(self, event):
        v = KMeansV(self, self.data, self.k, self.parent.windowSelec, self.GetParent().project.EEGS)
        v.Show()


class KMeansV(wx.Frame):

    def __init__(self, p, data, k, selected, eeg):
        wx.Frame.__init__(self, p, -1, "Resultado de K-Means")
        self.SetSize(600, 600)
        self.Centre()
        self.name = []
        for i in eeg:
            self.name.append(i.name)
        self.data = data
        self.selceted = selected
        self.kmeans = k
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        Pnl = wx.Panel(self, size=(600, 600))
        pnlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Tabs = aui.AuiNotebook(Pnl, size=(Pnl.Size),
                                    style=aui.AUI_NB_DEFAULT_STYLE ^ (
                                            aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE)
                                          | aui.AUI_NB_WINDOWLIST_BUTTON)
        self.fillTabs()
        pnlSizer.Add(self.Tabs, 0, wx.EXPAND | wx.ALL, 1)
        Pnl.SetSizer(pnlSizer)
        baseContainer.Add(Pnl, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(baseContainer)

    def fillTabs(self):
        page = GridTab(self.Tabs, self.data, self.kmeans, self.selceted, 0, self.name)
        self.Tabs.AddPage(page, "Clasificación")
        page = GridTab(self.Tabs, self.data, self.kmeans, self.selceted, 1, self.name)
        self.Tabs.AddPage(page, "Clusters")


class GridTab(wx.Panel):

    def __init__(self, p, data, k, selected, type, eeg):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(p.Size))
        self.data = data
        self.selceted = selected
        self.kmeans = k
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        self.table = wx.grid.Grid(self)
        color = [(200, 200, 196), (150, 90, 196), (196, 239, 198),
                 (196, 239, 236), (196, 203, 239), (229, 196, 239), (239, 196, 196), (247, 230, 230)]
        label = ["EM", "FM", "Area bajo la curva", "Voltaje máximo", "Voltaje mínimo"]
        if type == 0:
            self.table.CreateGrid(len(data), len(data[0]))
            i = 0
            for la in eeg:
                self.table.SetRowLabelValue(i, la)
                i += 1
            for i in range(len(selected)):
                self.table.SetColLabelValue(i, selected[i])
            self.table.SetColLabelValue(len(selected), "Etiqueta")
            for row in range(len(data)):
                co = color[k.labels[row]]
                for col in range(len(data[row])):
                    self.table.SetCellValue(row, col, str(self.data[row][col]))
                    self.table.SetReadOnly(row, col, True)
                    self.table.SetCellBackgroundColour(row, col, wx.Colour(co))
            self.table.AutoSize()
            baseContainer.Add(self.table, 0, wx.EXPAND | wx.ALL, 0)

        if type == 1:
            self.table.CreateGrid(len(self.kmeans.kmean.cluster_centers_), len(data[0]))
            self.table.SetColLabelValue(0, "Cluster")
            u = 1
            for i in range(len(selected)):
                self.table.SetColLabelValue(i + 1, selected[i])

            clusters = self.kmeans.kmean.cluster_centers_

            for col in range(len(self.kmeans.kmean.cluster_centers_)):
                self.table.SetCellValue(col, 0, "Centro " + str(col + 1))
                co = color[col]
                self.table.SetCellBackgroundColour(col, 0, wx.Colour(co))

            for row in range(len(clusters)):
                co = color[row]
                for col in range(len(clusters[row])):
                    self.table.SetCellValue(row, col + 1, str(clusters[row][col]))
                    self.table.SetReadOnly(row, col + 1, True)
                    self.table.SetCellBackgroundColour(row, col + 1, wx.Colour(co))
            self.table.AutoSize()
            baseContainer.Add(self.table, 0, wx.EXPAND | wx.ALL, 0)
        if type == 2:
            self.table.Hide()
            leftpnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
            lefSizer = wx.BoxSizer(wx.VERTICAL)
            rightpnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
            rightSizer = wx.BoxSizer(wx.VERTICAL)
            labels = []
            u = 0
            for i in range(len(selected)):
                for y in range(selected[i]):
                    if selected[i] > 1:
                        labels.append(label[i] + str(u + 1))
                    else:
                        labels.append(label[i])
                    u += 1
            infoLabel = wx.StaticText(leftpnl, label="Atributo")
            self.opc1C = wx.ComboBox(leftpnl, value=labels[0], style=wx.CB_READONLY, choices=labels)
            self.opc2C = wx.ComboBox(leftpnl, value=labels[1], style=wx.CB_READONLY, choices=labels)
            scater = Scaterplot(rightpnl, data, k, selected)
            lefSizer.Add(infoLabel, 0, wx.EXPAND | wx.ALL, 2)
            lefSizer.Add(self.opc1C, 0, wx.EXPAND | wx.ALL, 2)
            lefSizer.Add(self.opc2C, 0, wx.EXPAND | wx.ALL, 2)
            rightSizer.Add(scater, 0, wx.EXPAND | wx.ALL, 2)
            leftpnl.SetSizer(lefSizer)
            rightpnl.SetSizer(rightSizer)
            baseContainer.Add(leftpnl, 0, wx.EXPAND | wx.ALL, 0)
            baseContainer.Add(rightpnl, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(baseContainer)


class Scaterplot(wx.Panel):

    def __init__(self, parent, data, k, selected):
        wx.Panel.__init__(self, parent, size=(500, 600),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.data = data
        self.selceted = selected
        self.kmeans = k
        self.SetCanvas(0, 1)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def changeRange(self, OldValue, OldMax, OldMin, NewMax, NewMin):
        OldRange = (OldMax - OldMin)
        NewRange = (NewMax - NewMin)
        return (((OldValue - OldMin) * NewRange) / OldRange) + NewMin

    def SetCanvas(self, X, Y):
        B = np.asmatrix(self.data)
        self.sideX = B[:, X]
        self.DrawX = []
        self.DrawY = []
        self.sideY = B[:, Y]
        p = max(self.sideX)[0]
        for i in range(len(self.sideX)):
            self.DrawX.append(self.changeRange(self.sideX[i], max(self.sideX)[0], min(self.sideX)[0], 20, 400))
        for i in self.sideY:
            self.DrawY.append(self.changeRange(self.sideY[i], max(self.sideY)[0], min(self.sideY)[0], 20, 490))

    def OnPaint(self, event=None):
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 3))
        dc.DrawLine(20, 20, 20, 490)
        dc.DrawLine(20, 490, 400, 490)

        dc.SetPen(wx.Pen(wx.BLACK, 2))
        for i in range(len(self.DrawX)):
            dc.DrawPoint(self.DrawX[i], self.DrawY[i])
