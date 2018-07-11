# Imports
import wx.lib.scrolledpanel
import wx.lib.agw.buttonpanel

# Local Imports
from WindowEditor import *


class BFPWindow (wx.Frame):
    title = "Visualizar"

    def __init__(self, parent):
            wx.Frame.__init__(self, parent, -1, "Filtrado", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
            self.Maximize(True)
            self.SetMinSize((self.Size[0], self.Size[1]))
            self.project = parent.GetParent().project
            # frame will contain the base container of window editor and eeg tabs
            frameSizer = wx.BoxSizer(wx.VERTICAL)
            # EEG tabs
            self.navigationTabs = aui.AuiNotebook(self, size=(self.Size[0], self.Size[1]),
                                           style=aui.AUI_NB_DEFAULT_STYLE ^ (aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE)
                                                 | aui.AUI_NB_WINDOWLIST_BUTTON)
            # filling the tabs
            # self.fillEEGTabs()
            self.fillnavigationTabs()
            self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.loadingNew)
            self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.loadingFinished)
            frameSizer.Add(self.navigationTabs, 0, wx.EXPAND, 3)
            self.Bind(wx.EVT_CLOSE, self.onClose)
            self.SetSizer(frameSizer)
            # creating a status bar to inform user of process
            self.CreateStatusBar()
            # setting the cursor to loading
            self.SetStatus("", 0)
            self.Centre()
            self.Show()

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
        for eeg in eegs:
            if "_" not in eeg.name:
                self.addNav(eeg)

    def addNav(self, e):
        page = tab(self.navigationTabs, self.project, e.name)
        self.navigationTabs.AddPage(page, e.name)

    def onClose(self, event):
        self.Hide()


class tab(wx.Panel):
    '''Panel that contains graph of an EEG
    and window tools'''
    def __init__(self, p, project, name):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(p.Size[0]-10 ,p.Size[1]-10 ))
        self.project = project
        self.name = name
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
        self.Centre()
        self.Show()

    def loadingNew(self, event):
        self.GetParent().GetParent().SetStatus("Loading EEG...", 0)

    def loadingFinished(self, event):
        wx.CallLater(0, lambda: self.GetParent().GetParent().SetStatus("", 0))

    def addTab(self, e):
        page = EEGTabV(self.eegTabs, e)
        self.eegTabs.AddPage(page, e.name)

    def fillEEGTabs(self):
        eegs = self.GetParent().GetParent().project.EEGS
        for eeg in eegs:
            if self.name in eeg.name:
                self.addTab(eeg)

    def onClose(self, event):
        self.Destroy()
