#Import
import wx
import wx.lib.agw.aquabutton as AB
import wx.lib.scrolledpanel
import wx.html2
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import wx.lib.agw.buttonpanel
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx


class WindowEditor (wx.Frame):
    title = "Window Editor"
    def __init__(self, e):
        wx.Frame.__init__(self, None, -1, "Window Editor",)
        self.Maximize(True)
        self.SetMinSize((1000, 700))
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN)
        #number of windows
        self.n = 1
        self.slider = None
        self.marker = None
        self.start = None
        self.end = None
        self.length = None
        self.eeg = e
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        #container of window information
        leftPnl = wx.Panel(self.pnl)
        self.tabWindows = wx.Notebook(leftPnl)
        self.addWindow()
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(self.tabWindows, 0, wx.EXPAND | wx.ALL, 5)
        # panel for electrode selector
        electrodePanel = wx.Panel(leftPnl)
        elecSizer = wx.BoxSizer(wx.VERTICAL)
        elecLabel = wx.StaticText(electrodePanel, label="Electrodes to view:")
        elecSizer.Add(elecLabel, 0, wx.EXPAND | wx.ALL, 5)

        self.electrodeList = wx.CheckListBox(electrodePanel, choices=self.eeg.getLabels())
        #select all items
        for i in range(len(self.electrodeList.GetItems())):
            self.electrodeList.Check(i, check=True)
        elecSizer.Add(self.electrodeList, 1, wx.EXPAND | wx.ALL, 5)
        electrodePanel.SetSizer(elecSizer)
        leftSizer.Add(electrodePanel, 0, wx.EXPAND | wx.ALL, 5)
        leftPnl.SetSizer(leftSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 20)
        #eeg grafic information right side
        rightPnl = wx.Panel(self.pnl)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        #panel for eeg graph
        self.eegGraph = CanvasPanel(rightPnl, self)
        self.toolbar = NavigationToolbar2Wx(self.eegGraph.canvas)
        self.toolbar.Realize()
        self.toolbar.Hide()
        self.customTools = customToolbar(rightPnl, self.toolbar)
        graphContainer.Add(self.customTools, 0, wx.EXPAND | wx.LEFT, 0)
        graphContainer.Add(self.eegGraph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 20)
        self.pnl.SetSizer(baseContainer)
        self.Centre()
        self.Show()

    def addWindow(self):
        page = wx.Panel(self.tabWindows)
        page.SetBackgroundColour("#eff2f4")
        pageSizer = wx.BoxSizer(wx.VERTICAL)
        windowThumb = wx.Panel(page, size=(200,200))
        windowThumb.SetBackgroundColour('#FFFFFF')
        pageSizer.Add(windowThumb, 0, wx.EXPAND | wx.ALL, 5)
        pageSizer.Add(wx.StaticText(page, label="Current Marker:",
                                  style=wx.ALIGN_CENTRE_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 5)

        parameters = wx.Panel(page)
        paramSizer = wx.FlexGridSizer(4, 2, (5, 5))
        #for testing purposes
        self.start = 0
        self.end = 3
        self.slider = wx.Slider(parameters, value=self.end/2, minValue=self.start, maxValue=self.end,
                                style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.changeMarker)
        self.marker = wx.TextCtrl(parameters)
        self.marker.SetValue(str(self.slider.GetValue()) + "s")
        lthLabel = wx.StaticText(parameters, label="Length:")
        strLabel = wx.StaticText(parameters, label="Start:")
        endLabel = wx.StaticText(parameters, label="End:")
        length = wx.TextCtrl(parameters)
        length.SetValue(str(self.end) + "s")
        start = wx.TextCtrl(parameters)
        start.SetValue(str(self.start) + "s")
        end = wx.TextCtrl(parameters)
        end.SetValue(str(self.end) + "s")
        paramSizer.AddMany([(self.slider, 1, wx.EXPAND), (self.marker, 1, wx.EXPAND), (lthLabel), (length, 1, wx.EXPAND),
                            (strLabel), (start, 1, wx.EXPAND), (endLabel), (end, 1, wx.EXPAND)])
        parameters.SetSizer(paramSizer)
        pageSizer.Add(parameters, 0, wx.EXPAND | wx.ALL, 5)
        page.SetSizer(pageSizer)
        self.tabWindows.AddPage(page, str(self.n))
        self.n += 1

    def changeMarker(self, event):
        self.marker.SetValue(str(self.slider.GetValue()) + "s")

    def zoomIn(self, event):
        aw, ah = self.eegGraph.figure.get_figwidth(), self.eegGraph.figure.get_figheight()
        aw *= 1.2
        ah *= 1.2
        self.eegGraph.figure.set_size_inches(aw, ah, forward=True)
        pix_w = aw * self.eegGraph.figure._dpi
        pix_h = ah * self.eegGraph.figure._dpi
        self.eegGraph.canvas.draw()
        self.eegGraph.canvas.SetSize(pix_w, pix_h)
        self.eegGraph.canvas.SetMinSize(size=(pix_w, pix_h))
        self.eegGraph.sizer.Layout()
        self.eegGraph.FitInside()

    def zoomOut(self, event):
        aw, ah = self.eegGraph.figure.get_figwidth(), self.eegGraph.figure.get_figheight()
        if (aw !=0) and (ah != 0):
            aw /= 1.2
            ah /= 1.2
            self.eegGraph.figure.set_size_inches(aw, ah, forward=True)
            pix_w = aw * self.eegGraph.figure._dpi
            pix_h = ah * self.eegGraph.figure._dpi
            self.eegGraph.canvas.draw()
            self.eegGraph.canvas.SetSize(pix_w, pix_h)
            self.eegGraph.canvas.SetMinSize(size=(pix_w, pix_h))
            self.eegGraph.sizer.Layout()
            self.eegGraph.FitInside()

class CanvasPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, win):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(win.GetSize()[0], win.GetSize()[1]),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN | wx.HSCROLL | wx.VSCROLL | wx.ALWAYS_SHOW_SB)
        self.SetupScrolling()
        self.eeg = win.eeg
        self.figure = None
        self.axes = None
        self.draw()
        self.canvas = FigureCanvas(self, 0, self.figure)
        n = 100*len(self.eeg.channels)
        self.canvas.SetInitialSize(size=(self.GetSize()[0], n))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

    def draw(self):
        #get amount of columns
        n = len(self.eeg.channels)
        self.axes = [None] * n
        self.figure, (self.axes) = plt.subplots(n, sharex=True, sharey=False)
        plt.subplots_adjust(left=0.04, bottom=0.01, right=0.99, top=0.99, hspace=0.5)
        i = 0
        #TODO check if electrode is checked to plot
        for ax in self.axes:
            channel = self.eeg.channels[i]
            x = np.arange(len(channel.readings))
            ax.plot(x, channel.readings)
            ax.set_title(channel.label, x=0)
            i += 1

class customToolbar(wx.lib.agw.buttonpanel.ButtonPanel):
    """
       Create small toolbar which is added to the main panel
       par:  parent
       """

    def __init__(self, par, tlb):
        wx.lib.agw.buttonpanel.ButtonPanel.__init__(self, par)
        self.toolbar = tlb
        self.ID_FIT = wx.NewId()
        self.ID_ZOOM = wx.NewId()
        self.ID_BACK = wx.NewId()
        self.ID_FWD = wx.NewId()

        self.AddSpacer()

        self.btnRestart = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_FIT, wx.Bitmap("src/restart.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Restart Zoom')
        self.AddButton(self.btnRestart)
        self.Bind(wx.EVT_BUTTON, self.ZoomFit, self.btnRestart)

        self.btnZoom = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_ZOOM, wx.Bitmap("src/zoom.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Zoom in/out')
        self.AddButton(self.btnZoom)
        self.Bind(wx.EVT_BUTTON, self.Zoom, self.btnZoom)

        self.btnBack = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_BACK, wx.Bitmap("src/back.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Undo Action')
        self.AddButton(self.btnBack)
        self.Bind(wx.EVT_BUTTON, self.Back, self.btnBack)

        self.btnFwd = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_FWD, wx.Bitmap("src/forward.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Redo Action')
        self.AddButton(self.btnFwd)
        self.Bind(wx.EVT_BUTTON, self.FWD, self.btnFwd)

        self.AddSpacer()

        self.DoLayout()

    def ZoomFit(self, event):
        self.toolbar.home()
        event.Skip()

    def Zoom(self, event):
        self.toolbar.zoom()
        event.Skip()

    def Back(self, event):
        self.toolbar.back()
        event.Skip()

    def FWD(self, event):
        self.toolbar.forward()
        event.Skip()