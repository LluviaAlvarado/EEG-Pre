# Imports
import wx.lib.agw.buttonpanel
import wx.lib.scrolledpanel

# Local Imports
from WindowEditor import *
from CGraphPanel import *


class ComponentViewer(wx.Frame):

    def __init__(self, parent, icas):
        wx.Frame.__init__(self, parent, -1, "Visor de Componentes Independientes",
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.Maximize(True)
        self.SetMinSize((self.Size[0], self.Size[1]))
        self.project = parent.GetParent().project
        self.icas = icas
        # frame will contain the base container of window editor and eeg tabs9
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        # button to eliminate artifacts
        eliminate = wx.Button(self, label="Eliminar Artefactos")
        topSizer.AddSpacer(self.Size[1] )
        topSizer.Add(eliminate, 0, wx.EXPAND | wx.ALL, 1)
        eliminate.Bind(wx.EVT_BUTTON, self.Eliminate)
        frameSizer.Add(topSizer, 0, wx.EXPAND | wx.ALL, 1)
        # EEG tabs
        self.navigationTabs = aui.AuiNotebook(self, size=(self.Size[0], self.Size[1]),
                                              style=aui.AUI_NB_DEFAULT_STYLE ^ (
                                                      aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE)
                                                    | aui.AUI_NB_WINDOWLIST_BUTTON)
        self.fillnavigationTabs()
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.loadingNew)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.loadingFinished)
        frameSizer.Add(self.navigationTabs, 0, wx.EXPAND | wx.ALL, 3)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.SetSizer(frameSizer)
        # creating a status bar to inform user of process
        self.CreateStatusBar()
        # setting the cursor to loading
        self.SetStatus("", 0)
        self.Centre()
        self.Show()

    def Eliminate(self, e):
        # calls the elimination function of his parent
        self.GetParent().EliminateComponents()
        self.Close()

    def loadingNew(self, event):
        # set loading status when eeg is changed
        self.SetStatus("Loading EEG...", 0)

    def loadingFinished(self, event):
        # return mouse to normal after load
        event.GetEventObject().CurrentPage.Refresh()
        wx.CallLater(0, lambda: self.SetStatus("", 0))

    def SetStatus(self, st, mouse):
        self.SetStatusText(st)
        if mouse == 0:
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.SetCursor(myCursor)
        elif mouse == 1:
            myCursor = wx.Cursor(wx.CURSOR_WAIT)
            self.SetCursor(myCursor)

    def fillnavigationTabs(self):
        eegs = self.GetParent().GetParent().project.EEGS
        i = 0
        for eeg in eegs:
            self.addNav(eeg, self.icas[i])
            i += 1

    def addNav(self, e, ica):
        page = ComponentTab(self.navigationTabs, e, ica)
        self.navigationTabs.AddPage(page, e.name)

    def onClose(self, event):
        self.Hide()


class ComponentTab(wx.Panel):
    '''Panel that contains the independent components found by FastICA'''

    def __init__(self, p, e, ica):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(p.Size))
        self.eeg = e
        self.graph = None
        self.eegGraph = None
        self.ica = ica
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        leftPnl = wx.Panel(self)
        labels = []
        for i in range(len(self.ica.components)):
            labels.append("C" + str(i))
        self.componentList = wx.CheckListBox(leftPnl, choices=labels)
        project = self.GetParent().GetParent().project
        self.tabManager = TabManager(leftPnl, self, project.windowLength)
        self.tabManager.Hide()

        # select all the components to view
        if len(self.ica.selectedComponents) == 0:
            # let's fill them with all the components
            for i in range(len(self.ica.components)):
                self.componentList.Check(i, check=True)
            self.ica.setComponents(self.componentList.GetCheckedItems())
        else:
            # fill checklist with the saved selection
            for i in self.ica.selectedComponents:
                self.componentList.Check(i, check=True)
        # button to apply changes from electrode selector
        applyChanges = wx.Button(leftPnl, label="Aplicar")
        applyChanges.Bind(wx.EVT_BUTTON, self.setSelected)
        labelComponent = wx.StaticText(self, -1, "  Selección de Componentes", style=wx.ALIGN_CENTER, size=(-1, -1))
        componentContainer = wx.BoxSizer(wx.VERTICAL)
        componentContainer.AddSpacer(20)
        componentContainer.Add(labelComponent, 0, wx.EXPAND | wx.ALL, 0)
        componentContainer.AddSpacer(10)
        componentContainer.Add(self.componentList, 0, wx.EXPAND | wx.ALL, 0)
        componentContainer.AddSpacer(4)
        componentContainer.Add(applyChanges, 0, wx.EXPAND | wx.ALL, 0)
        leftPnl.SetSizer(componentContainer)

        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 5)
        # component graphic information right side
        rightPnl = wx.Panel(self, size=self.Size)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        # panel for component graph
        self.graph = CGraph(rightPnl, self.ica, self.componentList, True)
        # creation of toolbar
        self.toolbar = Toolbar(rightPnl, self.graph, False)
        # sending toolbar to graph to bind
        self.graph.setToolbar(self.toolbar)
        graphContainer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        graphContainer.Add(self.graph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)

        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(baseContainer)

    def setSelected(self, event):
        self.ica.setComponents(self.componentList.GetCheckedItems())
        self.graph.changeComponents()
        self.graph.componentList.adjustment(self.componentList.GetCheckedItems())


class CGraph(wx.Panel):
    """this is a panel that displays
    the components found by FastICA
     for visual examination"""

    def __init__(self, parent, ica, selected, v=False):
        h = parent.GetParent().GetParent().Size[1]
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w / 5)
        self.v = v
        if v:
            h = parent.Size[1]
            w = parent.Size[0]
        h = h - 187
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.ica = ica

        self.eeg = ica
        self.selected = selected
        self.toolbar = None
        # baseSizer
        # baseSizer = wx.FlexGridSizer(1, 3, gap=(0, 0))
        baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        # and to the right the eeg graph
        w = self.Size[0] - 65
        h = self.Size[1]
        self.graph = CgraphPanel(self, ica, w, h)
        self.zoomP = zoomPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, len(self.ica.components)]
        self.timeRuler = customRuler(self, wx.HORIZONTAL, wx.SUNKEN_BORDER, values, len(self.ica.components))

        # left amplitud ruler side
        # creating a ruler for each component
        values = [self.ica.amUnits[0]]
        half = (self.ica.amUnits[0] - self.ica.amUnits[1]) / 2
        values.append(self.ica.amUnits[0] - half)
        values.append(self.ica.amUnits[1])
        self.ampRuler = customRuler(self, wx.VERTICAL, wx.SUNKEN_BORDER, values, len(self.ica.components))
        self.componentList = customList(self, wx.VERTICAL, wx.SUNKEN_BORDER)
        baseSizer.Add(self.componentList, 0, wx.EXPAND, 0)
        baseSizer.Add(self.ampRuler, 0, wx.EXPAND, 0)
        baseSizer.Add(self.graph, 0, wx.EXPAND, 0)
        self.SetSizer(baseSizer)

    def setToolbar(self, toolbar):
        self.toolbar = toolbar

    # method to redraw EEG graph after changing the selected electrodes
    def changeComponents(self):
        self.graph.apply()

    def checkV(self):
        return self.graph.getViewChannels()


class customList(wx.Panel):
    # List of channel labels
    def __init__(self, parent, orientation, style):
        wx.Panel.__init__(self, parent, style=style, size=(30, parent.Size[1]))
        self.ica = parent.ica
        baseSizer = wx.BoxSizer(orientation)
        self.adjustment(-1)
        self.SetSizer(baseSizer)

    def adjustment(self, components=-1):
        if components == -1:
            components = self.getChecked()
        self.DestroyChildren()
        if len(components) > 0:
            h = (590) / len(components)
            fontSize = int(h) - 3
            if h > 15:
                fontSize = 10
            i = 0
            posy = 0
            while i < len(components):
                center = posy + (h / 2) - (fontSize / 2)
                rule = wx.StaticText(self, i, "C" + str(components[i]), style=wx.ALIGN_CENTER,
                                     pos=(0, center),
                                     size=(30, h))
                rule.SetFont(wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                posy += h
                i += 1

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.ica.components):
                channels.append(self.ica.components[ix])
        return checked


class customRuler(wx.Panel):
    """this is a custom ruler where you can send the values
    you want to show instead of a normal count
    it also will add the zooming future for the eeg
    values are sent in as minAmp and maxAmp"""

    def __init__(self, parent, orientation, style, values, nCh):
        self.lapse = values
        self.font = wx.Font(5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.height = parent.graph.Size[1] - 3
        self.width = parent.graph.Size[0]
        self.place = (self.width / 10)
        # Amplitude range
        self.values = values
        self.graph = parent.graph
        self.ica = parent.ica
        # Number of channels
        self.nCh = nCh
        self.increment = 0
        self.minTime = 0
        self.maxTime = self.graph.msShowing + self.minTime
        self.opc = 0
        self.zoom = False
        self.num = 0

        baseSizer = wx.BoxSizer(orientation)
        self.opc = 2
        wx.Panel.__init__(self, parent, style=style, size=(30, self.height))
        self.makeAmpRuler()

        self.SetSizer(baseSizer)

    def msToPixel(self, ms, msE):
        length = self.graph.clShowing
        return ((length - (msE - ms)) * self.graph.incx) / self.graph.timeLapse

    def makeTimeRuler(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen('#000000'))
        dc.SetTextForeground('#000000')
        dc.SetFont(self.font)
        if self.opc == 1:
            pass
        else:
            channel = self.getChecked()
            self.nCh = len(channel)
            if self.nCh > 0:
                h = 600 / self.nCh
                if self.zoom:
                    h = 600 / self.num
                i = 0
                posy = 0
                while i < self.nCh:
                    dc.DrawRectangle(0, posy, 30, posy + h)
                    posy += h
                    i += 1
            self.zoom = False

    def makeAmpRuler(self):
        self.font = wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def zoomManager(self, num):
        self.zoom = True
        self.num = num
        self.Refresh()

    def update(self):
        self.Refresh()

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.ica.components):
                channels.append(self.ica.components[ix])
        return channels
