#imports
import wx
import wx.lib.agw.rulerctrl as RC
import wx.lib.scrolledpanel as SP
import math

class EEGraph(wx.Panel):
    '''this is a panel that displays
    an EEG for visual examination'''

    def __init__(self, parent, eeg, selected):
        h = parent.GetParent().GetParent().Size[1]
        h = h - 200
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w/5)
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.selected = selected
        #baseSizer
        baseSizer = wx.FlexGridSizer(2, 2, gap=(0, 0))

        #and to the right the eeg graph
        # bottom is reserved just for the time ruler
        self.graph = graphPanel(self)

        self.timeRuler = RC.RulerCtrl(self, -1, orient=wx.HORIZONTAL, style=wx.SUNKEN_BORDER)
        self.timeRuler.SetFormat(2)
        # setting the range to EEG duration
        self.timeRuler.SetRange(0, self.eeg.duration)
        self.timeRuler.SetUnits("s")
        # left amplitud ruler side
        # creating a ruler for each channel
        values = []
        values.append(self.eeg.amUnits[0])
        half = (self.eeg.amUnits[0] - self.eeg.amUnits[1]) / 2
        values.append(self.eeg.amUnits[0] - half)
        values.append(self.eeg.amUnits[1])
        ampRuler = customRuler(self, wx.VERTICAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels))

        baseSizer.Add(ampRuler, 0, wx.EXPAND, 0)
        baseSizer.Add(self.graph, 0, wx.EXPAND, 0)
        baseSizer.AddSpacer(30)
        baseSizer.Add(self.timeRuler, 0, wx.EXPAND, 0)
        self.SetSizer(baseSizer)

class customRuler(wx.Panel):
    '''this is a custom ruler where you can send the values
    you want to show instead of a normal count
    it also will add the zooming future for the eeg
    values are sent in as minAmp and maxAmp'''
    def __init__(self, parent, orientation, style, values, nCh):
        h = parent.graph.Size[1]
        wx.Panel.__init__(self, parent, style=style, size=(30, h))
        baseSizer = wx.BoxSizer(orientation)
        h = (self.Size[1]) / nCh
        i = 0
        while i < nCh:
            ruler = RC.RulerCtrl(self, -1, orient=wx.VERTICAL, size=(self.Size[0], h))
            ruler.SetFormat(2)
            ruler.SetRange(values[0], values[1])
            baseSizer.Add(ruler, 0, wx.EXPAND, 0)
            i += 1

        self.SetSizer(baseSizer)


class graphPanel(SP.ScrolledPanel):

    def __init__(self, parent):
        w = parent.Size[0] - 30
        h = parent.Size[1]
        SP.ScrolledPanel.__init__(self, parent, size=(w, h),
            style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN | wx.HSCROLL | wx.VSCROLL)
        self.SetupScrolling()
        self.eeg = parent.eeg
        self.subSampling = 0
        self.nSamp = self.eeg.frequency * self.eeg.duration
        if self.nSamp > 10000 and len(self.eeg.channels) > 5:
            self.setSamplingRate(10)
        else:
            self.setSamplingRate(50)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    '''sets the how many readings will we skip
     is set as a value from 0 to 100 represents 
     the % of the readings to use'''
    def setSamplingRate(self, r):
        self.subSampling = int(self.nSamp/round((r * self.nSamp) / 100))

    #gets the selected electrodes to graph
    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
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
        channels = self.getChecked()
        hSpace = (self.Size[1]-5) / len(channels)
        #TODO if there is zoom hspace will change
        for channel in self.eeg.channels:
            x = 0
            while(x < self.nSamp):
                ny = self.ChangeRange(channel.readings[x], y+hSpace, y)
                dc.DrawPoint(x, ny)
                x += self.subSampling
            y += hSpace
