#Imports
import wx
import wx.lib.agw.aquabutton as AB
import wx.lib.scrolledpanel
import wx.html2
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import wx.lib.agw.buttonpanel

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

#Local Imports
from TabManager import *
from EEGraph import *

class WindowEditor (wx.Frame):
    title = "Edición de Ventanas"
    def __init__(self, e, parent):
        wx.Frame.__init__(self, parent, -1, "Editor de Ventanas", style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Maximize(True)
        self.SetMinSize((self.Size[0], self.Size[1]))
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
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
        newTab = wx.Button(tabBtnPanel, label="Nueva")
        newTab.Bind(wx.EVT_BUTTON, self.createNewWindow)
        deleteTab = wx.Button(tabBtnPanel, label="Eliminar")
        deleteTab.Bind(wx.EVT_BUTTON, self.deleteWindow)
        tbpSizer.Add(newTab, 0, wx.EXPAND | wx.ALL, 5)
        tbpSizer.Add(deleteTab, 0, wx.EXPAND | wx.ALL, 5)
        tabBtnPanel.SetSizer(tbpSizer)
        leftSizer.Add(tabBtnPanel, 0, wx.EXPAND | wx.ALL, 5)
        # panel for electrode selector
        electrodePanel = wx.Panel(leftPnl)
        elecSizer = wx.BoxSizer(wx.VERTICAL)
        elecLabel = wx.StaticText(electrodePanel, label="Selección de Electrodos:")
        elecSizer.Add(elecLabel, 0, wx.EXPAND | wx.ALL, 5)

        self.electrodeList = wx.CheckListBox(electrodePanel, choices=self.eeg.getLabels())
        #select all items
        for i in range(len(self.electrodeList.GetItems())):
            self.electrodeList.Check(i, check=True)
        elecSizer.Add(self.electrodeList, 1, wx.EXPAND | wx.ALL, 5)
        #button to apply changes from electrode selector
        applyChanges = wx.Button(electrodePanel, label="Aplicar")

        elecSizer.Add(applyChanges, 0, wx.CENTER | wx.ALL, 5)
        electrodePanel.SetSizer(elecSizer)
        leftSizer.Add(electrodePanel, 0, wx.EXPAND | wx.ALL, 5)
        leftPnl.SetSizer(leftSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 20)
        #eeg grafic information right side
        rightPnl = wx.Panel(self.pnl)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        #panel for eeg graph
        self.eegGraph = EEGraph(rightPnl, self.eeg, self.electrodeList)
        self.toolbar = Toolbar(rightPnl)
        graphContainer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        graphContainer.Add(self.eegGraph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 20)
        self.pnl.SetSizer(baseContainer)
        self.Bind(wx.EVT_BUTTON, self.updateElectrodes, applyChanges)
        #creating a status bar to inform user of process
        self.CreateStatusBar()
        self.SetStatusText("Loading EEG Readings...")
        self.Centre()
        self.Show()
        wx.CallLater(0, lambda: self.SetStatus(""))

    def SetStatus(self, st):
        self.SetStatusText(st)

    def createNewWindow(self, event):
        self.tabManager.addWindow()
        event.Skip()

    def deleteWindow(self, event):
        self.tabManager.deleteWindow()
        event.Skip()

    def updateLength(self, l):
        self.GetParent().WindowLength = l

    #redraws the eeg with the selected electrodes
    def updateElectrodes(self, event):
        self.eegGraph.changeElectrodes()

class Toolbar(wx.lib.agw.buttonpanel.ButtonPanel):
    """
       Create small toolbar which is added to the main panel
       par:  parent
       """

    def __init__(self, par):
        wx.lib.agw.buttonpanel.ButtonPanel.__init__(self, par)
        self.ID_FIT = wx.NewId()
        self.ID_ZOOM = wx.NewId()
        self.ID_BACK = wx.NewId()
        self.ID_FWD = wx.NewId()

        self.AddSpacer()

        self.btnRestart = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_FIT, wx.Bitmap("src/restart.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Reiniciar Zoom')
        self.AddButton(self.btnRestart)
        self.Bind(wx.EVT_BUTTON, self.ZoomFit, self.btnRestart)

        self.btnZoom = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_ZOOM, wx.Bitmap("src/zoom.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Acercar')
        self.AddButton(self.btnZoom)
        self.Bind(wx.EVT_BUTTON, self.Zoom, self.btnZoom)

        self.btnBack = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_BACK, wx.Bitmap("src/back.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Deshacer')
        self.AddButton(self.btnBack)
        self.Bind(wx.EVT_BUTTON, self.Back, self.btnBack)

        self.btnFwd = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_FWD, wx.Bitmap("src/forward.png", wx.BITMAP_TYPE_PNG),
                             shortHelp='Rehacer')
        self.AddButton(self.btnFwd)
        self.Bind(wx.EVT_BUTTON, self.FWD, self.btnFwd)

        self.AddSpacer()

        self.DoLayout()

    def ZoomFit(self, event):

        event.Skip()

    def Zoom(self, event):

        event.Skip()

    def Back(self, event):

        event.Skip()

    def FWD(self, event):

        event.Skip()