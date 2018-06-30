# imports

from TransparentPanel import *
from GraphPanel import *

class EEGraph(wx.Panel):
    '''this is a panel that displays
    an EEG for visual examination'''

    def __init__(self, parent, eeg, selected):
        h = parent.GetParent().GetParent().Size[1]
        h = h - 187
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w / 5)
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.eeg = eeg
        num = len(self.eeg.channelMatrix[0])
        self.selected = selected
        self.toolbar = None
        # baseSizer
        baseSizer = wx.FlexGridSizer(2, 3, gap=(0, 0))

        # and to the right the eeg graph
        w = self.Size[0] - 30
        h = self.Size[1]
        self.graph = graphPanel(self, eeg, w, h)
        self.zoomP = zoomPanel(self, self.graph)
        self.windowP = windowPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, self.eeg.duration]
        self.timeRuler = customRuler(self, wx.HORIZONTAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels), num)

        # left amplitud ruler side
        # creating a ruler for each channell
        values = []
        values.append(self.eeg.amUnits[0])
        half = (self.eeg.amUnits[0] - self.eeg.amUnits[1]) / 2
        values.append(self.eeg.amUnits[0] - half)
        values.append(self.eeg.amUnits[1])
        self.ampRuler = customRuler(self, wx.VERTICAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels), num)
        self.channelList = customList(self, wx.VERTICAL, wx.SUNKEN_BORDER, self.eeg.channels)
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
    def __init__(self, parent, orientation, style, channels):
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
            h = (self.Size[1]-5) / len(channels)
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
                channels.append(self.eeg.additionalData[ix-len(self.eeg.channels)])
        return channels


class customRuler(wx.Panel):
    '''this is a custom ruler where you can send the values
    you want to show instead of a normal count
    it also will add the zooming future for the eeg
    values are sent in as minAmp and maxAmp'''

    def __init__(self, parent, orientation, style, values, nCh, num):
        self.height = parent.graph.Size[1] - 3
        self.width = parent.graph.Size[0]
        # Amplitude range
        self.values = values
        self.eeg = parent.eeg
        # Number of channels
        self.nCh = nCh
        self.increment = 0



        self.numReads = num
        self.t_r = self.eeg.duration / num
        self.maxPile = []
        self.minPile = []

        self.max = 0
        self.min = 0

        self.opc = 0
        self.zoom = False
        self.num = 0

        baseSizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            self.opc = 1
            wx.Panel.__init__(self, parent, style=style, size=(-1, 35))
            self.makeTimeRuler(self.eeg.duration)
            self.Ogmax = self.eeg.duration
            self.Ogmin = 0
        else:
            self.opc = 2
            wx.Panel.__init__(self, parent, style=style, size=(30, self.height))
            self.makeAmpRuler(nCh, values)

        self.SetSizer(baseSizer)

    def zoomH(self, s, e , n):
        if n == 1:
            self.Ogmax = self.t_r * e
            self.Ogmin = self.t_r * s

        self.max = self.t_r*e
        self.min = self.t_r*s

        self.increment = (self.max - self.min) / self.width

        self.maxPile.append(self.max)
        self.minPile.append(self.min)
        self.zoom = True
        self.Refresh()

    def makeTimeRuler(self, values):
        h = 0
        self.font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.lapse = values
        self.place = (self.width / 10)

        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def ChangeRange(self, v, nx, nm):
        oldRange = (self.Size[0]-5) - 0
        newRange = nx - nm
        newV = (((v - 0) * newRange) / oldRange) + nm
        return newV

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.Clear()
        channel = self.getChecked()
        self.nCh = len(channel)
        dc.SetPen(wx.Pen('#000000'))
        dc.SetTextForeground('#000000')
        dc.SetFont(self.font)
        if self.opc == 1:
            max = round(self.Ogmax, 2)
            min = round(self.Ogmin, 2)
            if self.zoom:
                max = self.max
                min = self.min

            dc.DrawRectangle(0, 0, self.Size[0]-5, 30)
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen('#000000'))
            dc.SetTextForeground('#000000')
            RM = 1
            l = (self.Size[0]-5) / 90
            u = 0
            i = 0
            while i < (self.Size[0]-5):
                if (u % 10) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 10)
                    y = round(self.ChangeRange(i, max, min), 4)
                    st = "s"
                    if(y<2):
                        st = "ms"
                        y = y * 1000
                        y = int(y)
                    w, h = dc.GetTextExtent(str(y))
                    if(i==0): RM = w/2
                    dc.DrawText(str(y), i + RM - w / 2, 11)
                    dc.DrawText(st, i + RM + w / 2, 11)
                    RM = 1

                elif (u % 5) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 8)

                elif not (u % 1):

                    dc.DrawLine(i + RM, 0, i + RM, 4)

                u += 1
                i += l
            dc.DrawLine((self.Size[0]-5 - 2), 0, (self.Size[0]-5 - 2), 10)
            if(max<2):
                max = max * 1000
                max = int(max)
            w, h = dc.GetTextExtent(str(round(max,2)))
            dc.DrawText(str(round(max, 2)), (self.Size[0]-5 - 2) - w, 11)

        else:
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

    def makeAmpRuler(self, nCh, values):
        self.font = wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def zoomManager(self, num):
        self.zoom = True
        self.num = num
        self.Refresh()

    def update(self):
        self.maxPile = []
        self.minPile = []
        self.maxPile.append(self.Ogmax)
        self.minPile.append(self.Ogmin)
        self.max = self.maxPile[len(self.maxPile) - 1]
        self.min = self.minPile[len(self.maxPile) - 1]
        self.Refresh()

    def zoomOut(self):

        self.minPile.pop()
        self.maxPile.pop()
        self.max = self.maxPile[len(self.maxPile) - 1]
        self.min = self.minPile[len(self.maxPile) - 1]
        self.zoom = True
        self.Refresh()

    def redo(self):
        self.Refresh()

    def moveZom(self, s, e):
        self.maxPile[len(self.minPile) - 1] = self.t_r*e
        self.minPile[len(self.minPile) - 1] = self.t_r*s
        self.max = self.maxPile[len(self.minPile) - 1]
        self.min = self.minPile[len(self.minPile) - 1]
        self.zoom = True
        self.Refresh()


    def moveZoom(self, dis):
        d = 0
        if dis < 0:
            d = (dis * -1) * self.increment
            if (self.minPile[len(self.minPile) - 1] - d) > 0:
                self.minPile[len(self.minPile) - 1] -= d
                self.maxPile[len(self.minPile) - 1] -= d
            else:
                self.minPile[len(self.minPile) - 1] -= self.minPile[len(self.minPile) - 1]
                self.maxPile[len(self.minPile) - 1] -= self.minPile[len(self.minPile) - 1]
        else:
            d = dis * self.increment
            if (self.maxPile[len(self.minPile) - 1] + d) < self.Ogmax:
                self.minPile[len(self.minPile) - 1] += d
                self.maxPile[len(self.minPile) - 1] += d
            else:
                r = self.Ogmax - self.maxPile[len(self.minPile) - 1]
                self.minPile[len(self.minPile) - 1] += r
                self.maxPile[len(self.minPile) - 1] = self.Ogmax

        self.max = self.maxPile[len(self.minPile) - 1]
        self.min = self.minPile[len(self.minPile) - 1]
        self.zoom = True
        self.Refresh()

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix-len(self.eeg.channels)])
        return channels



