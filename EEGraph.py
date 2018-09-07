# imports
from TransparentPanel import *
from GraphPanel import *


class EEGraph(wx.Panel):
    """this is a panel that displays
    an EEG for visual examination"""

    def __init__(self, parent, eeg, selected, v=False):
        h = parent.GetParent().GetParent().Size[1]
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w / 5)
        self.v = v
        if v:
            h = parent.Size[1]
            w = parent.Size[0]
        h = h - 187
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.ica = None
        self.selected = selected
        self.toolbar = None
        # baseSizer
        baseSizer = wx.FlexGridSizer(2, 3, gap=(0, 0))

        # and to the right the eeg graph
        w = self.Size[0] - 65
        h = self.Size[1]
        self.graph = graphPanel(self, eeg, w, h)
        self.zoomP = zoomPanel(self, self.graph)
        self.windowP = windowPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, self.eeg.duration]
        self.timeRuler = customRuler(self, wx.HORIZONTAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels))

        # left amplitud ruler side
        # creating a ruler for each channell
        values = [self.eeg.amUnits[0]]
        half = (self.eeg.amUnits[0] - self.eeg.amUnits[1]) / 2
        values.append(self.eeg.amUnits[0] - half)
        values.append(self.eeg.amUnits[1])
        self.ampRuler = customRuler(self, wx.VERTICAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels))
        self.channelList = customList(self, wx.VERTICAL, wx.SUNKEN_BORDER)
        baseSizer.Add(self.channelList, 0, wx.EXPAND, 0)
        baseSizer.Add(self.ampRuler, 0, wx.EXPAND, 0)
        baseSizer.Add(self.graph, 0, wx.EXPAND, 0)

        baseSizer.AddSpacer(30)
        baseSizer.AddSpacer(30)
        baseSizer.Add(self.timeRuler, 0, wx.EXPAND, 0)
        self.SetSizer(baseSizer)

    def setToolbar(self, toolbar):
        self.toolbar = toolbar

    # method to redraw EEG graph after changing the selected electrodes
    def changeElectrodes(self):
        self.graph.apply()

    def checkV(self):
        return self.graph.getViewChannels()


class customList(wx.Panel):
    # List of channel labels
    def __init__(self, parent, orientation, style):
        wx.Panel.__init__(self, parent, style=style, size=(30, parent.graph.Size[1]))
        self.eeg = parent.eeg
        baseSizer = wx.BoxSizer(orientation)
        self.adjustment(-1)
        self.SetSizer(baseSizer)

    def adjustment(self, channels=-1):
        if channels == -1:
            channels = self.getChecked()
        self.DestroyChildren()
        if len(channels) > 0:
            h = (self.Size[1] - 5) / len(channels)
            fontSize = int(h) - 3
            if h > 15:
                fontSize = 10
            i = 0
            posy = 0
            while i < len(channels):
                center = posy + (h / 2) - (fontSize / 2)
                rule = wx.StaticText(self, i, channels[i].label, style=wx.ALIGN_CENTER,
                                     pos=(0, center),
                                     size=(30, h))
                rule.SetFont(wx.Font(fontSize, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
                posy += h
                i += 1

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix - len(self.eeg.channels)])
        return channels


class customRuler(wx.Panel):
    """this is a custom ruler where you can send the values
    you want to show instead of a normal count
    it also will add the zooming future for the eeg
    values are sent in as minAmp and maxAmp"""

    def __init__(self, parent, orientation, style, values, nCh):
        self.lapse = values
        self.font = wx.Font(5, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.height = parent.graph.Size[1] - 3
        self.width = parent.graph.Size[0]
        self.place = (self.width / 10)
        # Amplitude range
        self.values = values
        self.graph = parent.graph
        self.eeg = parent.eeg
        # Number of channels
        self.nCh = nCh
        self.increment = 0
        self.minTime = 0
        self.maxTime = self.graph.msShowing + self.minTime
        self.opc = 0
        self.zoom = False
        self.num = 0

        baseSizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            self.opc = 1
            wx.Panel.__init__(self, parent, size=(self.width, 35),
                              style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
            self.makeTimeRuler()
        else:
            self.opc = 2
            wx.Panel.__init__(self, parent, style=style, size=(30, self.height))
            self.makeAmpRuler()
        self.SetSizer(baseSizer)

    def msToPixel(self, ms, msE):
        length = self.graph.msShowing
        return ((length - (msE - ms)) * self.graph.incx) / self.graph.timeLapse

    def makeTimeRuler(self):
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen('#000000'))
        dc.SetTextForeground('#000000')
        dc.SetFont(self.font)
        if self.opc == 1:
            dc.DrawRectangle(0, 0, self.Size[0] - 4, 30)
            dc = wx.PaintDC(self)

            msS = self.graph.strMs
            msE = msS + self.graph.msShowing
            part = self.graph.msShowing / 100
            i = 0
            RM = 0
            while i < 101:
                f = self.msToPixel((part * i) + msS, msE)
                if (i % 10) == 0:
                    y = int(part * i + msS)
                    w, h = dc.GetTextExtent(str(y))
                    if i == 0:
                        RM = w / 2
                        f = f + 1
                    st = "ms"
                    if i == 100:
                        y = int(y / 1000)
                        w, h = dc.GetTextExtent(str(y))
                        RM = w * -1
                        f = f - 6
                        st = "s"

                    dc.DrawLine(f, 0, f, 10)

                    dc.DrawText(str(y), f + RM - w / 2, 11)
                    dc.DrawText(st, f + RM + w / 2, 11)
                    RM = 0

                elif (i % 5) == 0:
                    dc.DrawLine(f, 0, f, 8)

                elif not (i % 1):
                    dc.DrawLine(f, 0, f, 4)
                i += 1
        else:
            channel = self.getChecked()
            self.nCh = len(channel)
            if self.nCh > 0:
                h = self.height / self.nCh
                if self.zoom:
                    h = self.height / self.num
                i = 0
                posy = 0
                while i < self.nCh:
                    dc.DrawRectangle(0, posy, 30, posy + h)
                    posy += h
                    i += 1
            self.zoom = False

    def makeAmpRuler(self):
        self.font = wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def zoomManager(self, num):
        self.zoom = True
        self.num = num
        self.Refresh()

    def update(self):
        self.Refresh()

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix - len(self.eeg.channels)])
        return channels
