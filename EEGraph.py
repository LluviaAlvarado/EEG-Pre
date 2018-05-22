#imports
import wx
import wx.lib.agw.rulerctrl as RC

class EEGraph(wx.Panel):
    '''this is a panel that displays
    an EEG for visual examination'''

    def __init__(self, parent, eeg, selected):
        h = parent.GetParent().GetParent().Size[1]
        h = h - (h/10)
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w/4)
        wx.Panel.__init__(self, parent, size=(w, h))
        self.eeg = eeg
        self.selected = selected
        #baseSizer
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        #top part will have the left ruler for amplitude
        #and to the right the eeg graph
        centerSizer = wx.BoxSizer(wx.HORIZONTAL)
        ampRuler = RC.RulerCtrl(self, -1, orient=wx.VERTICAL, style=wx.SUNKEN_BORDER)
        self.graph = graphPanel(self)
        centerSizer.Add(ampRuler, 0, wx.EXPAND, 0)
        centerSizer.Add(self.graph, 0 , wx.EXPAND | wx.ALL, 0)
        #bottom is reserved just for the time ruler
        timeRuler = RC.RulerCtrl(self, -1, orient=wx.HORIZONTAL, style=wx.SUNKEN_BORDER)

        baseSizer.Add(centerSizer, 0, wx.EXPAND | wx.ALL, 0)
        baseSizer.Add(timeRuler, 0, wx.EXPAND, 0)
        self.SetSizer(baseSizer)

class graphPanel(wx.Panel):

    def __init__(self, parent):
        w = parent.Size[0] - 30
        h = parent.Size[1] - 80
        wx.Panel.__init__(self, parent, size=(w, h))
        self.eeg = parent.eeg
        self.subSampling = 0
        self.nSamp = self.eeg.frequency * self.eeg.duration
        self.setSamplingRate(50)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
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
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        y = 0
        channels = self.getChecked()
        hSpace = self.Size[1] / len(channels)
        #TODO if there is zoom hspace will change
        for channel in self.eeg.channels:
            x = 0
            while(x < self.nSamp):
                ny = self.ChangeRange(channel.readings[x], y+hSpace, y)
                dc.DrawPoint(x, ny)
                x += self.subSampling
            y += hSpace
