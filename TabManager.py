import wx
'''custom tab manager that contains
    the information of the selected
    windows'''
from EEGraph import graphPanel

class TabManager(wx.Notebook):

    def __init__(self, p, parent, winL):
        #calling the sup init
        wx.Notebook.__init__(self, p)
        #parameters for window size
        self.par = parent
        #this takes the global window length
        self.length = winL
        #creating the base window
        self.addWindow()

    #for iterating over tabs
    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    #updating length changes on all windows
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

    #this is called on new button
    def addWindow(self):
        page = windowTab(self)
        self.AddPage(page, str(self.GetPageCount()+1))

    #called on delete button delete selected tab
    def deleteWindow(self):
        self.DeletePage(self.GetSelection())
        #renaming all tabs
        for i in range(self.GetPageCount()):
            self.SetPageText(i, str(i+1))

class windowTab(wx.Panel):

    def __init__(self, p):
        #calling sup init
        wx.Panel.__init__(self, p)
        self.SetBackgroundColour("#eff2f4")
        pageSizer = wx.BoxSizer(wx.VERTICAL)
        #panel for the window thumb
        windowThumb = WindowThumb(self, p.par.eeg, 215, 215)
        pageSizer.Add(windowThumb, 0, wx.EXPAND | wx.ALL, 5)
        pageSizer.Add(wx.StaticText(self, label="Marcador:",
                                    style=wx.ALIGN_CENTRE_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 5)
        parameters = wx.Panel(self)
        paramSizer = wx.FlexGridSizer(4, 2, (5, 5))
        # for testing purposes
        self._start = 0
        self._end = p.length
        self.readings = p.par.eeg.frequency * p.par.eeg.duration
        self.slider = wx.Slider(parameters, value=self.readings / 2, minValue=self._start, maxValue=self.readings,
                                style=wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SLIDER, self.changeMarker)
        self.marker = wx.TextCtrl(parameters, style=wx.TE_PROCESS_ENTER)
        self.marker.SetValue(str(self.GetSliderValue()))
        self._marker = self.GetSliderValue()
        lthLabel = wx.StaticText(parameters, label="Longitud (s):")
        strLabel = wx.StaticText(parameters, label="Inicio (s):")
        endLabel = wx.StaticText(parameters, label="Fin (s):")
        self.length = wx.TextCtrl(parameters, style=wx.TE_PROCESS_ENTER, name="length")
        self.length.SetValue(str(p.length))
        self.start = wx.TextCtrl(parameters, style=wx.TE_PROCESS_ENTER)
        self.start.SetValue(str(self._start))
        self.end = wx.TextCtrl(parameters, style=wx.TE_PROCESS_ENTER)
        self.end.SetValue(str(self._end))
        #binding for changes by user
        self.length.Bind(wx.EVT_TEXT_ENTER, self.onLengthChange)
        self.start.Bind(wx.EVT_TEXT_ENTER, self.onLengthChange)
        self.end.Bind(wx.EVT_TEXT_ENTER, self.onLengthChange)
        self.marker.Bind(wx.EVT_TEXT_ENTER, self.changeSlider)
        paramSizer.AddMany(
            [(self.slider, 1, wx.EXPAND), (self.marker, 1, wx.EXPAND), lthLabel, (self.length, 1, wx.EXPAND),
             strLabel, (self.start, 1, wx.EXPAND), endLabel, (self.end, 1, wx.EXPAND)])
        parameters.SetSizer(paramSizer)
        pageSizer.Add(parameters, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(pageSizer)

    #set float value to int for slider
    def SetSliderValue(self, v):
        oldRange = self.GetParent().par.eeg.duration - 0
        newRange = self.readings - 0
        newV = round((((v - 0) * newRange) / oldRange) + 0, 2)
        self.slider.SetValue(int(newV))

    #we need to change the value to float
    def GetSliderValue(self):
        oldRange = self.readings - 0
        newRange = self.GetParent().par.eeg.duration - 0
        v = float(self.slider.GetValue())
        return round((((v - 0) * newRange) / oldRange) + 0, 2)

    def returnLastValue(self):
        self.end.SetValue(str(self._end))
        self.start.SetValue(str(self._start))
        self.length.SetValue(str(self._end - self._start))

    def onLengthChange(self, event):
        try:
            if float(self.end.GetValue()) > self.GetParent().par.eeg.duration or \
                float(self.end.GetValue()) < 0:
                self.end.SetValue(str(self._end))
            if float(self.start.GetValue()) > self.GetParent().par.eeg.duration or \
                float(self.start.GetValue()) < 0:
                self.start.SetValue(str(self._start))
            if float(self.length.GetValue()) > self.GetParent().par.eeg.duration or \
                float(self.length.GetValue()) < 0:
                self.returnLastValue()
        except:
            #not a numeric number return to last value
            self.returnLastValue()
        l = round(float(self.end.GetValue()) - float(self.start.GetValue()), 2)
        #if the one changed was the length
        if event.EventObject.Name == "length":
            #we need to change the end if possible
            nE = float(self.start.GetValue()) + float(self.length.GetValue())
            if nE > self.GetParent().par.eeg.duration:
                nE = self.GetParent().par.eeg.duration
            self.end.SetValue(str(round(nE,2)))
            #change to valid length
            l = round(float(self.end.GetValue()) - float(self.start.GetValue()), 2)
        self.length.SetValue(str(l))

        #updating new values
        self._start = float(self.start.GetValue())
        self._end = float(self.end.GetValue())
        #changing marker pos to middle of new values if not between them
        if self._marker > self._end or self._marker < self._start:
            half = round(self._start + (l/2), 2)
            self.marker.SetValue(str(half))
            self.SetSliderValue(half)
        #updating length on all windows, they always need to be the same
        #TODO change window size in viewer
        self.GetParent().updateLengthOnAll(l)

    def changeSlider(self, event):
        try:
            if float(self.marker.GetValue()) > float(self.end.GetValue()) or \
                    float(self.marker.GetValue()) < float(self.start.GetValue()):
                self.marker.SetValue(str(self._marker))
        except:
            #change to last valid marker
            self.marker.SetValue(str(self._marker))
        self._marker = float(self.marker.GetValue())
        # changing the slider
        self.SetSliderValue(self._marker)

    #changes de marker of a window
    def changeMarker(self, event):
        self._marker = self.GetSliderValue()
        self.marker.SetValue(str(self.GetSliderValue()))

class WindowThumb(wx.Panel):

    def __init__(self, parent, eeg, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
            style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.subSampling = 0
        self.incx = 1
        self.nSamp = self.eeg.frequency * self.eeg.duration
        self.setSamplingRate(self.nSamp)
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

    #gets the selected electrodes to graph
    def getChecked(self):
        print(self.GetParent())
        checked = self.GetParent().GetParent().par.electrodeList.GetCheckedItems()
        channels = []
        for ix in checked:
            channels.append(self.eeg.channels[ix])
        return channels

    #changes the value for printable porpuses
    def ChangeRange(self, v, nu, nl):
        oldRange = self.eeg.amUnits[0] - self.eeg.amUnits[1]
        newRange = nu - nl
        newV = round((((v - self.eeg.amUnits[1]) * newRange) / oldRange) + nl, 2)
        return newV

    def OnPaint(self, event=None):
        #buffered so it doesn't paint channel per channel
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        y = 0

        amUnits = self.eeg.amUnits
        subSampling=self.subSampling
        incx = self.incx
        self.chanPosition = []
        #defining channels to plot
        channels = self.getChecked()
        hSpace = (self.Size[1] - 5) / len(channels)
        w = self.Size[0]
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        for channel in channels:
            x = 0
            i = 0
            self.chanPosition.append([channel.label, y])
            while x < w - incx:
                ny = (((channel.readings[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                dc.DrawPoint(x, ny)
                i += subSampling
                x += incx
            y += hSpace