# Imports
import wx
import wx.aui as aui

# Local imports
from WindowEEG import *
'''custom tab manager that contains
    the information of the selected
    windows'''


class TabManager(aui.AuiNotebook):

    def __init__(self, p, parent, winL):
        # calling the sup init
        w = parent.GetParent().Size[0] / 6
        h = parent.GetParent().Size[1] / 2.1
        aui.AuiNotebook.__init__(self, p, size=(w, h),
                                 style=aui.AUI_NB_DEFAULT_STYLE ^ (aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE )
                                       | aui.AUI_NB_WINDOWLIST_BUTTON)
        # parameters for window size
        self.par = parent
        # this takes the global window length
        self.length = winL
        # bind when window is changed to update window showed on graph
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.changeWindow)
        # bind when a window is deleted
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.deleteWindow)
        # filling windows if exist
        self.fillTabs()

    def changeWindow(self, event):
        # refreshing the windows panel
        if self.par.eegGraph is not None:
            self.par.eegGraph.windowP.update()
            # return mouse to normal after load
            self.par.GetParent().GetParent().SetStatus("", 0)

    def fillTabs(self):
        for i in range(len(self.par.eeg.windows)):
            page = windowTab(self, i)
            self.AddPage(page, str(i + 1))
        if self.GetPageCount() == 0:
            self.showInfoTab()

    def showInfoTab(self):
        infoTab = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(self.Size[1]/3)
        info = wx.StaticText(infoTab, label='No hay Ventanas que mostrar.')
        sizer.Add(info, 0, wx.CENTER | wx.ALL, 5)
        info = wx.StaticText(infoTab, label='Cree una con la herramienta de "Ventana".')
        sizer.Add(info, 0, wx.CENTER | wx.ALL, 5)
        infoTab.SetSizer(sizer)
        self.AddPage(infoTab, "")

    # for iterating over tabs
    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    # updating length changes on all windows
    def updateLengthOnAll(self, l):
        self.length = l
        self.par.updateLength(l)
        for tab in self:
            tab.length.SetValue(str(l))
            tab.end.SetValue(str(float(tab.start.GetValue()) + l))
            # changing marker pos to middle of new values if not between them
            if tab._marker > tab._end or tab._marker < tab._start:
                half = round(tab._start + (l / 2), 2)
                tab.marker.SetValue(str(half))
                tab.SetSliderValue(half)

    # this is called on new button
    def addWindow(self, est, len, tbe):
        if self.GetPageCount() == 1 and self.GetPageText(0) == "":
            # there only was the info tab so remove it
            self.DeletePage(0)
        # adding to eeg from project
        window = WindowEEG(est, len, tbe)
        self.par.eeg.addWindow(window)
        page = windowTab(self, self.GetPageCount())
        self.AddPage(page, str(self.GetPageCount()+1))


    # called on delete button delete selected tab
    def deleteWindow(self, event):
        # delete on all eegs
        self.par.GetParent().GetParent().deleteWindow(event.Selection)
        # removing from eeg from project
        eegs = self.par.GetParent().GetParent().project.EEGS
        length = len(eegs)
        i = 0
        while i < length:
            eegs[i].removeWindow(event.Selection)
            i += 1
        event.Veto()

    def renameWindows(self):
        if self.GetPageCount() == 0:
            self.showInfoTab()
        else:
            # renaming all tabs
            for i in range(self.GetPageCount()):
                self.SetPageText(i, str(i+1))

class windowTab(wx.Panel):

    def __init__(self, p, w):
        # calling sup init1
        wx.Panel.__init__(self, p)
        self.SetBackgroundColour("#eff2f4")
        pageSizer = wx.BoxSizer(wx.VERTICAL)
        # the window we are working on
        self.window = p.par.eeg.windows[w]
        # get windowThumb size
        length = self.GetParent().Size[1] / 1.8
        # panel for the window thumb
        self.windowThumb = WindowThumb(self, p.par.eeg, self.window, length, length)
        pageSizer.Add(self.windowThumb, 0, wx.CENTER | wx.ALL, 5)
        parameters = wx.Panel(self)
        paramSizer = wx.FlexGridSizer(4, 2, (5, 5))
        self._start = self.window.stimulus - self.window.TBE
        self._l = self.window.length
        self._end = self._start + self._l
        self.stimulus = self.window.stimulus
        self._tbe = self.window.TBE
        # Data to show of the window
        # Time Before Estimulus (TBE)
        TBELabel = wx.StaticText(parameters, label="TAE (ms):")
        lthLabel = wx.StaticText(parameters, label="Longitud (ms):")
        strLabel = wx.StaticText(parameters, label="Inicio (ms):")
        endLabel = wx.StaticText(parameters, label="Fin (ms):")
        self.tbe = wx.TextCtrl(parameters, style=wx.TE_PROCESS_ENTER)
        self.tbe.SetValue(str(self._tbe))
        self.length = wx.TextCtrl(parameters, style=wx.TE_READONLY, name="length")
        self.length.SetValue(str(self._l))
        self.start = wx.TextCtrl(parameters, style=wx.TE_READONLY)
        self.start.SetValue(str(self._start))
        self.end = wx.TextCtrl(parameters, style=wx.TE_READONLY)
        self.end.SetValue(str(self._end))
        # binding for changes by user on the TBE
        self.tbe.Bind(wx.EVT_TEXT_ENTER, self.changeTBE)
        paramSizer.AddMany(
            [(TBELabel, 1, wx.EXPAND), (self.tbe, 1, wx.EXPAND), lthLabel, (self.length, 1, wx.EXPAND),
             strLabel, (self.start, 1, wx.EXPAND), endLabel, (self.end, 1, wx.EXPAND)])
        parameters.SetSizer(paramSizer)
        pageSizer.Add(parameters, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(pageSizer)

    def toMilis(self, seconds):
        return seconds * 1000

    def toSeconds(self, milis):
        return milis / 1000

    def changeTBE(self, event):
        duration = self.toMilis(self.GetParent().par.eeg.duration)
        try:
            # make sure it is a valid value
            if float(self.tbe.GetValue()) > duration or \
                    float(self.tbe.GetValue()) < 0:
                self.tbe.SetValue(str(self._tbe))
        except:
            # not a numeric number return to last value and finish
            self.tbe.SetValue(str(self._tbe))
            return
        # modify the other parameters if valid
        tbe = float(self.tbe.GetValue())
        start = self.stimulus - tbe
        end = start + self._l
        # valid start
        if start <= self.stimulus and start >= 0:
            # valid end
            if end >= self.stimulus and end <= duration:
                # now we can change the TBE
                self._tbe = int(tbe)
                self._start = int(start)
                self.start.SetValue(str(self._start))
                self._end = int(end)
                self.end.SetValue(str(self._end))
                # modify window data
                self.window.modifyTBE(self._tbe)
                # refresh window graph
                self.windowThumb.setDelimiters(self.window)
                self.windowThumb.Refresh()
        # return to valid TBE to make sure
        self.tbe.SetValue(str(self._tbe))


'''this panel shows a thumbnail of
    the window for viewing purposes'''
class WindowThumb(wx.Panel):
    def __init__(self, parent, eeg, window, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
            style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.subSampling = 0
        self.incx = 1
        self.nSamp = self.eeg.frequency * self.eeg.duration
        self.setSamplingRate(self.nSamp)
        # info for window delimiting
        self.strReading = 0
        self.stimulusReading = 0
        self.setDelimiters(window)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    '''sets the how many readings will we skip
    and how many pixels'''
    def setSamplingRate(self, nSamp):
        if nSamp < self.Size[0]:
            self.incx = int(self.Size[0] / nSamp)
            self.subSampling = 1
        else:
            self.subSampling = int(nSamp / self.Size[0])
            self.incx = 1

    def milisToReading(self, milis):
        freq = self.eeg.frequency / 1000
        return milis * freq

    # sets the limits to graph of the window
    def setDelimiters(self, window):
        # getting the readings to show
        start = window.stimulus - window.TBE
        end = start + window.length
        self.strReading = self.milisToReading(start)
        endRead = self.milisToReading(end)
        nsamp = endRead - self.strReading
        if nsamp < 10:
            nsamp = 10
        self.setSamplingRate(nsamp)
        self.stimulusReading = self.milisToReading(window.stimulus)


    # gets the selected electrodes to graph
    def getChecked(self):
        checked = self.GetParent().GetParent().par.electrodeList.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix-len(self.eeg.channels)])
        return channels

    # changes the value for printable porpuses
    def ChangeRange(self, v, nu, nl):
        oldRange = self.eeg.amUnits[0] - self.eeg.amUnits[1]
        newRange = nu - nl
        newV = round((((v - self.eeg.amUnits[1]) * newRange) / oldRange) + nl, 2)
        return newV

    def OnPaint(self, event=None):
        # buffered so it doesn't paint channel per channel
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        y = 0
        amUnits = self.eeg.amUnits
        subSampling=self.subSampling
        incx = self.incx
        self.chanPosition = []
        # defining channels to plot
        channels = self.getChecked()
        if len(channels) != 0:
            hSpace = (self.Size[1] - 5) / len(channels)
            w = self.Size[0]
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            for channel in channels:
                x = 0
                i = int(self.strReading)
                self.chanPosition.append([channel.label, y])
                while x < w - incx:
                    ny = (((channel.readings[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                    dc.DrawPoint(x, ny)
                    i += subSampling
                    x += incx
                y += hSpace