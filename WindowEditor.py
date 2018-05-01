#Import
import wx
import wx.lib.agw.aquabutton as AB
import wx.lib.scrolledpanel
import wx.html2
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import bokeh.plotting as bk
from bokeh.resources import CDN
from bokeh.embed import file_html
mpl.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

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
        # panel for zoom buttons
        zoomPanel = wx.Panel(leftPnl)
        zoomSizer = wx.BoxSizer(wx.VERTICAL)
        zoomLabel = wx.StaticText(zoomPanel, label="Zoom:")
        zoomSizer.Add(zoomLabel, 0, wx.CENTER | wx.ALL, 5)
        zoom_plus = AB.AquaButton(zoomPanel, label="+", size=(30, 30))
        zoom_plus.SetForegroundColour("black")
        self.Bind(wx.EVT_BUTTON, self.zoomIn, zoom_plus)
        zoomSizer.Add(zoom_plus, 0, wx.CENTER | wx.ALL, 5)
        zoom_minus = AB.AquaButton(zoomPanel, label="-", size=(30, 30))
        zoom_minus.SetForegroundColour("black")
        self.Bind(wx.EVT_BUTTON, self.zoomOut, zoom_minus)
        zoomSizer.Add(zoom_minus, 0, wx.CENTER | wx.ALL, 5)
        zoomPanel.SetSizer(zoomSizer)
        leftSizer.Add(zoomPanel, 0, wx.EXPAND | wx.ALL, 5)
        leftPnl.SetSizer(leftSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 20)

        #eeg grafic information right side

        rightPnl = wx.Panel(self.pnl)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        #panel for eeg graph
        self.eegGraph = CanvasPanel(rightPnl, self)
        graphContainer.Add(self.eegGraph, 0, wx.EXPAND | wx.ALL, 20)
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
        self.canvas.SetInitialSize(size=(self.GetSize()[0], self.GetSize()[1]))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

    def draw(self):
        #get amount of columns
        n = len(self.eeg.channels)
        self.axes = [None] * n
        self.figure, (self.axes) = plt.subplots(n, sharex=True, sharey=False)
        plt.subplots_adjust(hspace=0)
        i = 0
        for ax in self.axes:
            channel = self.eeg.channels[i]
            x = np.arange(len(channel.readings))
            ax.plot(x, channel.readings)
            ax.set_title(channel.label, x=0)
            i += 1
