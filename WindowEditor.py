#Imports
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
#Local Imports
from TabManager import *

class WindowEditor (wx.Frame):
    title = "Window Editor"
    def __init__(self, e, parent):
        wx.Frame.__init__(self, parent, -1, "Window Editor",)
        self.Maximize(True)
        self.SetMinSize((1000, 700))
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN)
        self.eeg = e
        #updating length to max size of eeg if it has not been initialized
        if parent.WindowLength is None:
            self.updateLength(self.eeg.duration)
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        #container of window information
        leftPnl = wx.Panel(self.pnl)
        self.tabManager = TabManager(leftPnl, self, self.GetParent().WindowLength)
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(self.tabManager, 0, wx.EXPAND | wx.ALL, 5)
        #panel for tab buttons
        tabBtnPanel = wx.Panel(leftPnl)
        tbpSizer = wx.BoxSizer(wx.HORIZONTAL)
        newTab = wx.Button(tabBtnPanel, label="New")
        newTab.Bind(wx.EVT_BUTTON, self.createNewWindow)
        deleteTab = wx.Button(tabBtnPanel, label="Delete")
        deleteTab.Bind(wx.EVT_BUTTON, self.deleteWindow)
        tbpSizer.Add(newTab, 0, wx.EXPAND | wx.ALL, 5)
        tbpSizer.Add(deleteTab, 0, wx.EXPAND | wx.ALL, 5)
        tabBtnPanel.SetSizer(tbpSizer)
        leftSizer.Add(tabBtnPanel, 0, wx.EXPAND | wx.ALL, 5)
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
        #button to apply changes from electrode selector
        applyChanges = wx.Button(electrodePanel, label="Apply")

        elecSizer.Add(applyChanges, 0, wx.CENTER | wx.ALL, 5)
        electrodePanel.SetSizer(elecSizer)
        leftSizer.Add(electrodePanel, 0, wx.EXPAND | wx.ALL, 5)
        leftPnl.SetSizer(leftSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 20)
        #eeg grafic information right side
        rightPnl = wx.Panel(self.pnl)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        #panel for eeg graph
        self.eegGraph = CanvasPanel(rightPnl, self, self.electrodeList)
        self.toolbar = NavigationToolbar2Wx(self.eegGraph.canvas)
        self.toolbar.Realize()
        self.toolbar.Hide()
        self.customTools = customToolbar(rightPnl, self.toolbar)
        graphContainer.Add(self.customTools, 0, wx.EXPAND | wx.LEFT, 0)
        graphContainer.Add(self.eegGraph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 20)
        self.pnl.SetSizer(baseContainer)
        self.Bind(wx.EVT_BUTTON, self.redrawEEG, applyChanges)
        self.Centre()
        self.Show()

    def createNewWindow(self, event):
        self.tabManager.addWindow()
        event.Skip()

    def deleteWindow(self, event):
        self.tabManager.deleteWindow()
        event.Skip()

    def updateLength(self, l):
        self.GetParent().WindowLength = l

    #redraws the eeg with the selected electrodes
    def redrawEEG(self, event):
        self.eegGraph.figure.clear()
        self.eegGraph.draw()
        self.eegGraph.setCanvas()


class CanvasPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, win, eList):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, size=(win.GetSize()[0], win.GetSize()[1]),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN | wx.HSCROLL | wx.VSCROLL | wx.ALWAYS_SHOW_SB)
        self.SetupScrolling()
        self.eeg = win.eeg
        self.electrodeList = eList
        self.figure = None
        self.axes = None
        self.draw()
        self.sizer = None
        self.canvas = None
        self.setCanvas()
        self.SetAutoLayout(1)

    def setCanvas(self):
        self.canvas = FigureCanvas(self, 0, self.figure)
        n = 100 * len(self.eeg.channels)
        self.canvas.SetInitialSize(size=(self.GetSize()[0], n))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)

    def getChecked(self):
        checked = self.electrodeList.GetCheckedItems()
        channels = []
        for ix in checked:
            channels.append(self.eeg.channels[ix])
        return channels

    def draw(self):
        #get amount of columns
        n = len(self.electrodeList.GetCheckedItems())
        self.axes = [None] * n
        self.figure, (self.axes) = plt.subplots(n, sharex=True, sharey=False)
        plt.subplots_adjust(left=0.04, bottom=0.01, right=0.99, top=0.99, hspace=0.5)
        i = 0
        #check if electrode is checked to plot
        channelsPlot = self.getChecked()
        for ax in self.axes:
            channel = channelsPlot[i]
            x = np.linspace(0, self.eeg.duration, len(channel.readings))
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