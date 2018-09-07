# Imports
import wx.lib.scrolledpanel
import wx.lib.agw.buttonpanel

# Local Imports
from TabManager import *
from EEGraph import *
from WindowDialog import WindowDialog


class WindowEditor(wx.Frame):
    title = "Edición de Ventanas"

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Editor de Ventanas", style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Maximize(True)
        self.SetMinSize((self.Size[0], self.Size[1]))
        self.project = parent.GetParent().project
        # frame will contain the base container of window editor and eeg tabs
        frameSizer = wx.BoxSizer(wx.VERTICAL)
        # EEG tabs
        self.eegTabs = aui.AuiNotebook(self, size=(self.Size[0], self.Size[1]),
                                       style=aui.AUI_NB_DEFAULT_STYLE ^ (aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE)
                                             | aui.AUI_NB_WINDOWLIST_BUTTON)
        # filling the tabs
        self.fillEEGTabs()
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.loadingNew)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.loadingFinished)
        frameSizer.Add(self.eegTabs, 0, wx.EXPAND, 3)

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.SetSizer(frameSizer)
        # creating a status bar to inform user of process.
        self.CreateStatusBar()
        # setting the cursor to loading.
        self.SetStatus("Loading EEG...", 1)
        self.Centre()
        self.Show()
        wx.CallLater(0, lambda: self.SetStatus("", 0))

    def setEEG(self, e):
        eegs = self.GetParent().GetParent().project.EEGS
        i = 0
        for eeg in eegs:
            if e.name == eeg.name:
                break
            i += 1
        # setting the selection to eeg user clicked
        self.eegTabs.ChangeSelection(i)

    def loadingNew(self, event):
        # set loading status when eeg is changed
        self.SetStatus("Loading EEG...", 1)

    def loadingFinished(self, event):
        # return mouse to normal after load
        event.GetEventObject().CurrentPage.eegGraph.graph.paint = True
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

    def addTab(self, e):
        page = EEGTab(self.eegTabs, e)
        self.eegTabs.AddPage(page, e.name)

    def fillEEGTabs(self):
        eegs = self.GetParent().GetParent().project.EEGS
        for eeg in eegs:
            self.addTab(eeg)

    # every eeg must have the same channels
    def updateChannels(self, selected):
        i = 0
        # to reset selection since notebook changes it with this
        currentSelection = self.eegTabs.GetSelection()
        while i < self.eegTabs.GetPageCount():
            self.eegTabs.GetPage(i).updateChannels(selected)
            i += 1
        self.eegTabs.SetSelection(currentSelection)

    def addWindow(self, st, tbe):
        currentTab = self.eegTabs.GetPage(self.eegTabs.GetSelection())
        currentTab.tabManager.addWindow(st, self.project.windowLength, tbe)

    def updateDataAllWindows(self, tbe, l):
        i = 0
        while i < self.eegTabs.GetPageCount():
            tab = self.eegTabs.GetPage(i)
            tab.tabManager.updateAll(l, tbe)
            i += 1
        # update on project
        self.GetParent().GetParent().project.updateWindowInfo(l, tbe)
        # refresh graph
        self.eegTabs.GetPage(self.eegTabs.GetSelection()).eegGraph.Refresh()

    def onClose(self, event):
        self.GetParent().onWEClose()
        self.Destroy()


class EEGTab(wx.Panel):
    '''Panel that contains graph of an EEG
    and window tools'''

    def __init__(self, p, e, edit=True):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.eeg = e
        self.eegGraph = None
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)

        # container of window information
        leftPnl = wx.Panel(self)
        tabLabel = wx.StaticText(leftPnl, label="Ventanas:")
        project = self.GetParent().GetParent().project
        self.tabManager = TabManager(leftPnl, self, project.windowLength)

        leftSizer = wx.BoxSizer(wx.VERTICAL)
        leftSizer.Add(tabLabel, 0, wx.CENTER, 5)
        leftSizer.Add(self.tabManager, 0, wx.EXPAND | wx.ALL, 5)
        # panel for tab buttons
        tabBtnPanel = wx.Panel(leftPnl)
        tbpSizer = wx.BoxSizer(wx.HORIZONTAL)
        tabBtnPanel.SetSizer(tbpSizer)
        leftSizer.Add(tabBtnPanel, 0, wx.EXPAND | wx.ALL, 5)
        # panel for electrode selector
        electrodePanel = wx.Panel(leftPnl)
        elecSizer = wx.BoxSizer(wx.VERTICAL)
        elecLabel = wx.StaticText(electrodePanel, label="Selección de Electrodos:")
        elecSizer.Add(elecLabel, 0, wx.EXPAND | wx.ALL, 5)

        self.electrodeList = wx.CheckListBox(electrodePanel, choices=self.eeg.getLabels())
        # select all the channel items to view
        if len(self.eeg.selectedCh) == 0:
            # let's fill them with all the channels
            for i in range(len(self.eeg.channels)):
                self.electrodeList.Check(i, check=True)
            self.eeg.setSelected(self.electrodeList.GetCheckedItems())
        else:
            # fill checklist with the saved selection
            for i in self.eeg.selectedCh:
                self.electrodeList.Check(i, check=True)
        if edit:
            elecSizer.Add(self.electrodeList, 1, wx.EXPAND | wx.ALL, 5)
            # button to apply changes from electrode selector
            applyChanges = wx.Button(electrodePanel, label="Aplicar")
            elecSizer.Add(applyChanges, 0, wx.CENTER | wx.ALL, 5)
            electrodePanel.SetSizer(elecSizer)
            leftSizer.Add(electrodePanel, 0, wx.EXPAND | wx.ALL, 5)
            leftPnl.SetSizer(leftSizer)
            baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 5)
            self.Bind(wx.EVT_BUTTON, self.updateElectrodes, applyChanges)
        # eeg graphic information right side
        rightPnl = wx.Panel(self)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        # panel for eeg graph
        self.eegGraph = EEGraph(rightPnl, self.eeg, self.electrodeList)
        # creation of toolbar
        self.toolbar = Toolbar(rightPnl, self.eegGraph)
        # sending toolbar to graph to bind
        self.eegGraph.setToolbar(self.toolbar)
        graphContainer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        graphContainer.Add(self.eegGraph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(baseContainer)

    def createNewWindow(self, e, l):
        # creates a new window on every eeg
        self.GetParent().GetParent().addWindow(e, l)

    # redraws the eeg with the selected electrodes
    def updateElectrodes(self, event):
        self.GetParent().GetParent().updateChannels(self.electrodeList.GetCheckedItems())

    def updateChannels(self, selected):
        # even if it is redundant it is needed to update all eegs
        self.electrodeList.SetCheckedItems(selected)
        self.eegGraph.changeElectrodes()
        ch = self.eegGraph.checkV()
        self.eegGraph.channelList.adjustment(ch)
        self.eegGraph.ampRuler.zoomManager(len(ch))
        self.eeg.setSelected(self.electrodeList.GetCheckedItems())
        self.tabManager.GetPage(self.tabManager.GetSelection()).Refresh()


class EEGTabV(wx.Panel):
    '''Panel that contains graph of an EEG
    and window tools'''

    def __init__(self, p, e):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(p.Size))
        self.eeg = e
        self.eegGraph = None
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        project = self.GetParent().GetParent().project
        leftPnl = wx.Panel(self)
        self.tabManager = TabManager(leftPnl, self, project.windowLength)
        self.electrodeList = wx.CheckListBox(leftPnl, choices=self.eeg.getLabels())
        # select all the channel items to view
        if len(self.eeg.selectedCh) == 0:
            # let's fill them with all the channels
            for i in range(len(self.eeg.channels)):
                self.electrodeList.Check(i, check=True)
            self.eeg.setSelected(self.electrodeList.GetCheckedItems())
        else:
            # fill checklist with the saved selection
            for i in self.eeg.selectedCh:
                self.electrodeList.Check(i, check=True)
        # button to apply changes from electrode selector

        # baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 5)
        # eeg graphic information right side
        rightPnl = wx.Panel(self, size=self.Size)
        graphContainer = wx.BoxSizer(wx.VERTICAL)
        # panel for eeg graph
        self.eegGraph = EEGraph(rightPnl, self.eeg, self.electrodeList, True)
        # creation of toolbar
        self.toolbar = Toolbar(rightPnl, self.eegGraph, False)
        # sending toolbar to graph to bind
        self.eegGraph.setToolbar(self.toolbar)
        graphContainer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, 0)
        graphContainer.Add(self.eegGraph, 1, wx.EXPAND | wx.ALL, 0)
        rightPnl.SetSizer(graphContainer)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(baseContainer)


class Toolbar(wx.lib.agw.buttonpanel.ButtonPanel):
    """
       Create small toolbar which is added to the main panel
       par:  parent
       """

    def __init__(self, par, graph, edit=True):
        wx.lib.agw.buttonpanel.ButtonPanel.__init__(self, par)
        self.ID_FIT = wx.NewId()
        self.ID_ZOOM = wx.NewId()
        self.ID_ZOOMOUT = wx.NewId()
        self.ID_MOVE = wx.NewId()
        self.ID_VIEW = wx.NewId()
        self.ID_NEWWIN = wx.NewId()
        self.graph = graph
        self.AddSpacer()
        self.buttons = []
        self.edit = edit
        self.window_s = 0
        # button to fit graph to screen
        self.btnRestart = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_FIT,
                                                            wx.Bitmap("src/restart.png", wx.BITMAP_TYPE_PNG),
                                                            shortHelp='Reiniciar Zoom')
        self.btnRestart.SetKind(wx.ITEM_CHECK)
        self.AddButton(self.btnRestart)
        self.buttons.append(self.btnRestart)
        self.Bind(wx.EVT_BUTTON, self.ZoomFit, self.btnRestart)
        # button for zooming out
        self.btnZoomO = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_ZOOMOUT,
                                                          wx.Bitmap("src/zoom_out.png", wx.BITMAP_TYPE_PNG),
                                                          shortHelp='Alejar')
        self.AddButton(self.btnZoomO)
        self.buttons.append(self.btnZoomO)
        self.Bind(wx.EVT_BUTTON, self.ZoomO, self.btnZoomO)

        # button for zooming in
        self.btnZoom = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_ZOOM,
                                                         wx.Bitmap("src/zoom_in.png", wx.BITMAP_TYPE_PNG),
                                                         shortHelp='Acercar')
        self.btnZoom.SetKind(wx.ITEM_CHECK)
        self.AddButton(self.btnZoom)
        self.buttons.append(self.btnZoom)
        self.Bind(wx.EVT_BUTTON, self.Zoom, self.btnZoom)

        # button for moving graph
        self.btnMove = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_MOVE,
                                                         wx.Bitmap("src/move.png", wx.BITMAP_TYPE_PNG),
                                                         shortHelp='Desplazar')
        self.btnMove.SetKind(wx.ITEM_CHECK)
        self.AddButton(self.btnMove)
        self.buttons.append(self.btnMove)
        self.Bind(wx.EVT_BUTTON, self.Move, self.btnMove)

        if edit:
            self.btnNewwin = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_NEWWIN,
                                                               wx.Bitmap("src/new_window.png", wx.BITMAP_TYPE_PNG),
                                                               shortHelp='Nueva Ventana')
            self.btnNewwin.SetKind(wx.ITEM_CHECK)
            self.AddButton(self.btnNewwin)
            self.buttons.append(self.btnNewwin)
            self.Bind(wx.EVT_BUTTON, self.newWindow, self.btnNewwin)

        self.all_w = wx.Bitmap("src/all_windows.png", wx.BITMAP_TYPE_PNG)
        self.no_w = wx.Bitmap("src/no_windows.png", wx.BITMAP_TYPE_PNG)
        self.sel_w = wx.Bitmap("src/selected_window.png", wx.BITMAP_TYPE_PNG)

        # button for change view
        self.btnView = wx.lib.agw.buttonpanel.ButtonInfo(self, self.ID_VIEW,
                                                         self.all_w,
                                                         shortHelp='Todas las ventanas')
        self.AddButton(self.btnView)
        self.buttons.append(self.btnView)
        self.Bind(wx.EVT_BUTTON, self.changeview, self.btnView)
        ica = 0
        if self.graph.ica == None:
            max = self.graph.eeg.amUnits[0]
            min = self.graph.eeg.amUnits[1]
        else:
            ica = 43
            max = self.graph.ica.amUnits[0]
            min = self.graph.ica.amUnits[1]

        b1 = wx.StaticText(self, 0, " ", style=wx.ALIGN_CENTER, pos=(2, 2), size=(96 + ica, 46))
        b1.SetBackgroundColour((0, 0, 0))
        b2 = wx.StaticText(self, 0, " ", style=wx.ALIGN_CENTER, pos=(3, 3), size=(94 + ica, 44))
        r1 = wx.StaticText(self, -1, "Amplitud Promedio ", style=wx.ALIGN_CENTER, pos=(5, 4), size=(-1, -1))
        r2 = wx.StaticText(self, -1, "Máxima:  " + str(round(max, 3)), style=wx.ALIGN_CENTER,
                           pos=(5, 18),
                           size=(-1, -1))
        r3 = wx.StaticText(self, -1, "Mínima:  " + str(round(min, 3)), style=wx.ALIGN_CENTER,
                           pos=(5, 32),
                           size=(-1, -1))
        r1.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        r2.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        r3.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self.AddSpacer()
        self.DoLayout()

    def unToggleOthers(self, toggled):
        for btn in self.buttons:
            if btn.GetId() != toggled:
                btn.SetToggled(False)
            if btn.GetId() == self.ID_NEWWIN and btn.GetToggled() == False:
                self.graph.windowP.hide()

    def ZoomFit(self, event):
        if event.GetEventObject().GetToggled():
            # setting to zoom cursor in graph
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.graph.SetCursor(myCursor)
            # untoggling others
            self.unToggleOthers(self.ID_FIT)
            self.graph.graph.move = False
            self.graph.zoomP.zoom = False
            self.graph.windowP.fill = False
            self.graph.graph.newWin = False

            self.graph.graph.resetZoom()
            self.graph.ampRuler.update()
            self.graph.timeRuler.update()
            self.graph.channelList.adjustment()
        event.Skip()

    def ZoomO(self, event):
        # setting to zoom cursor in graph
        myCursor = wx.Cursor(wx.CURSOR_ARROW)
        self.graph.SetCursor(myCursor)
        self.graph.graph.move = False
        self.graph.windowP.fill = False
        self.graph.zoomP.zoom = False
        self.graph.graph.newWin = False
        self.graph.graph.returnZoom()
        # untoggling others
        self.unToggleOthers(self.ID_ZOOMOUT)
        event.Skip()

    def Zoom(self, event):
        if event.GetEventObject().GetToggled():
            # setting to zoom cursor in graph
            myCursor = wx.Cursor(wx.CURSOR_CROSS)
            self.graph.SetCursor(myCursor)
            self.graph.graph.move = False
            self.graph.graph.newWin = False
            self.graph.windowP.fill = False
            self.graph.zoomP.zoom = True
            # untoggling others
            self.unToggleOthers(self.ID_ZOOM)
        else:
            # setting to zoom cursor in graph
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.graph.SetCursor(myCursor)
            self.graph.zoomP.zoom = False
        event.Skip()

    def Move(self, event):
        if event.GetEventObject().GetToggled():
            # setting to move cursor in graph
            myCursor = wx.Cursor(wx.CURSOR_SIZING)
            self.graph.SetCursor(myCursor)
            self.graph.graph.move = True
            self.graph.graph.newWin = False
            self.graph.windowP.fill = False
            # untoggling others
            self.unToggleOthers(self.ID_MOVE)
        else:
            # setting to zoom cursor in graph
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.graph.SetCursor(myCursor)
            self.graph.graph.move = False
        event.Skip()

    def changeview(self, event):
        self.window_s += 1
        if self.window_s > 2:
            self.window_s = 0
        if self.window_s == 0:
            self.btnView.SetBitmap(self.all_w)
            self.graph.windowP.setWindowState(2)
            self.btnView.SetShortHelp("Todas las ventanas")
        if not self.edit and self.window_s == 1:
            self.window_s += 1
        if self.window_s == 1:
            self.btnView.SetBitmap(self.sel_w)
            self.graph.windowP.setWindowState(1)
            self.btnView.SetShortHelp("Solo la ventana seleccionada")
        if self.window_s == 2:
            self.btnView.SetBitmap(self.no_w)
            self.graph.windowP.setWindowState(0)
            self.btnView.SetShortHelp("Ninguna ventana")

    def newWindow(self, event):
        if event.GetEventObject().GetToggled():
            # Check for a window
            dad = self.GetParent().GetParent().GetParent().GetParent()
            if dad.project.windowTBE is None:
                l, tbe = self.getWindowData()
                dad.project.windowLength = l
                dad.project.windowTBE = tbe

            self.graph.windowP.windowLength = dad.project.windowLength
            self.graph.windowP.windowTBE = dad.project.windowTBE
            self.graph.windowP.show()

            myCursor = wx.Cursor(wx.CURSOR_BULLSEYE)
            self.graph.SetCursor(myCursor)
            self.graph.graph.newWin = True
            self.graph.windowP.fill = True
            self.graph.zoomP.zoom = False
            self.graph.graph.move = False
            self.unToggleOthers(self.ID_NEWWIN)
        else:
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.graph.SetCursor(myCursor)
            self.graph.graph.newWin = False
            self.graph.windowP.fill = False
            self.graph.windowP.hide()
            self.graph.windowP.update()

        event.Skip()

    def getWindowData(self):
        # giving a default value in ms to avoid user errors
        l = 50
        tbe = 10
        with WindowDialog(self, l, tbe) as dlg:
            dlg.ShowModal()
            # handle dialog being cancelled or ended by some other button
            if dlg.length.GetValue() != "":
                try:
                    l = int(dlg.length.GetValue())
                except:
                    # it was not an integer
                    dlg.length.SetValue(str(l))
            if dlg.tbe.GetValue() != "":
                try:
                    tbe = int(dlg.tbe.GetValue())
                except:
                    # it was not an integer
                    dlg.tbe.SetValue(str(tbe))
        return l, tbe
