#imports

import wx
import wx.lib.agw.rulerctrl as RC
import wx.lib.scrolledpanel as SP

class EEGraph(wx.Panel):
    '''this is a panel that displays
    an EEG for visual examination'''


    def __init__(self, parent, eeg, selected):
        h = parent.GetParent().GetParent().Size[1]
        h = h - 180
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w/5)
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.selected = selected
        self.toolbar = None
        #baseSizer
        baseSizer = wx.FlexGridSizer(2, 3, gap=(0, 0))

        #and to the right the eeg graph
        self.graph = graphPanel(self)
        self.transparent = transparentPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, self.eeg.duration]
        self.timeRuler = RC.RulerCtrl(self, -1, orient=wx.HORIZONTAL, style=wx.SUNKEN_BORDER)
        self.timeRuler.SetFormat(2)
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
        channelList = customList(self, wx.VERTICAL, wx.SUNKEN_BORDER, self.eeg.channels)
        baseSizer.Add(channelList, 0, wx.EXPAND, 0)
        baseSizer.Add(ampRuler, 0, wx.EXPAND, 0)
        baseSizer.Add(self.graph, 0, wx.EXPAND, 0)

        baseSizer.AddSpacer(30)
        baseSizer.AddSpacer(30)
        baseSizer.Add(self.timeRuler, 0, wx.EXPAND, 0)
        self.SetSizer(baseSizer)

    def setToolbar(self, toolbar):
        self.toolbar = toolbar

    #method to redraw EEG graph after changing the selected electrodes
    def changeElectrodes(self):
        self.graph.Refresh()

class customList(wx.Panel):
    def __init__(self, parent, orientation, style, channels):
        h = parent.graph.Size[1]
        self.eeg = parent.eeg
        wx.Panel.__init__(self, parent, style=style, size=(30, h))
        baseSizer = wx.BoxSizer(orientation)
        h = (self.Size[1]) / len(channels)
        i = 0
        posy = 0
        while i < len(channels):
            rule = wx.StaticText(self, -1, channels[i].label, style=wx.ALIGN_CENTER, pos=(0, posy), size=(30, h))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.BOLD))

            posy += h
            i += 1
        self.SetSizer(baseSizer)

    def redo(self):
        self.DestroyChildren()
        channels = self.getChecked()
        h = (self.Size[1]) / len(channels)
        i = 0
        posy = 0
        while i < len(channels):
            rule = wx.StaticText(self, i, channels[i].label, style=wx.ALIGN_CENTER, pos=(0, posy), size=(30, h))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            # baseSizer.Add(rule, 0, wx.EXPAND, 0)
            posy += h
            i += 1

    def getChecked(self):
        print(self.GetParent())
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            channels.append(self.eeg.channels[ix])
        return channels

class customRuler(wx.Panel):
    '''this is a custom ruler where you can send the values
    you want to show instead of a normal count
    it also will add the zooming future for the eeg
    values are sent in as minAmp and maxAmp'''
    def __init__(self, parent, orientation, style, values, nCh):
        h = parent.graph.Size[1]
        self.values = values
        wx.Panel.__init__(self, parent, style=style, size=(30, h))
        self.eeg = parent.eeg
        baseSizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            self.makeTimeRuler(values)
        else:
            self.makeAmpRuler(nCh, values)

        self.SetSizer(baseSizer)

    def makeTimeRuler(self, values):
        h = 0

    def makeAmpRuler(self, nCh, values):
        h = (self.Size[1]) / nCh
        i = 0
        posy = 0
        while i < nCh:
            rule = wx.StaticText(self, -1, str(values[0]), style=wx.ALIGN_CENTER, pos=(0, posy), size=(30, h))
            ruler = wx.StaticText(self, -1, str(values[2]), style=wx.ALIGN_CENTER, pos=(0, posy + 9), size=(30, h))
            ruler.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            posy += h
            i += 1

    def redo(self):
        self.DestroyChildren()
        channels = self.getChecked()
        h = (self.Size[1]) / len(channels)
        i = 0
        posy = 0
        while i < len(channels):

            rule = wx.StaticText(self, -1, str(self.values[0]), style=wx.ALIGN_CENTER, pos=(0, posy), size=(30, h))
            if h > 20  :
                ruler = wx.StaticText(self, -1, str(self.values[2]), style=wx.ALIGN_CENTER, pos=(0, posy + 9), size=(30, h))
                ruler.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            # baseSizer.Add(rule, 0, wx.EXPAND, 0)
            posy += h
            i += 1

    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            channels.append(self.eeg.channels[ix])
        return channels

'''a transparent panel over the eegraph to draw other elements
    like the zoom rectangle'''
class transparentPanel(wx.Panel):

    def __init__(self, parent, over):
        wx.Panel.__init__(self, parent, size=(over.Size[0], over.Size[1]), pos=(60, 0))
        # vars for zoom
        self.zoom = False
        self.zStart = None
        self.zEnd = None
        self.dc = None
        self.gc = None
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)

    def OnClickDown(self, pos):
        self.zStart = pos

    def MovingMouse(self, pos):
        self.zEnd = pos
        if self.zoom and self.zStart is not None:
            self.OnPaint()

    def OnClickReleased(self, pos):
        self.zEnd = pos
        if self.zoom:
            self.OnPaint()
            self.zStart = None
            self.zEnd = None

    def onEraseBackground(self, event):
        """
        Overridden to do nothing to prevent flicker
        """
        pass
    #needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self):
        self.GetParent().graph.Refresh()
        dc = wx.ClientDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if self.zoom:
            if gc:
                color = wx.Colour(255, 0, 0, 60)
                gc.SetBrush(wx.Brush(color, style=wx.BRUSHSTYLE_SOLID))
                gc.SetPen(wx.RED_PEN)
                path = gc.CreatePath()
                if self.zEnd is None:
                    w = 0
                    h = 0
                else:
                    w = self.zEnd[0] - self.zStart[0]
                    h = self.zEnd[1] - self.zStart[1]
                path.AddRectangle(self.zStart[0], self.zStart[1], w, h)
                gc.FillPath(path)
                gc.StrokePath(path)


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
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClickDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickReleased)
        self.Bind(wx.EVT_MOTION, self.MovingMouse)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnClickDown(self, event):
        self.GetParent().transparent.OnClickDown(event.GetPosition())

    def MovingMouse(self, event):
        self.GetParent().transparent.MovingMouse(event.GetPosition())

    def OnClickReleased(self, event):
        self.GetParent().transparent.OnClickReleased(event.GetPosition())


    '''sets the how many readings will we skip
     is set as a value from 0 to 100 represents 
     the % of the readings to use'''
    def setSamplingRate(self, r):
        self.subSampling = int(self.nSamp/round((r * self.nSamp) / 100))

    #gets the selected electrodes to graph
    def getChecked(self):
        print(self.GetParent())
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
        nSamp =self.nSamp
        amUnits = self.eeg.amUnits
        subSampling=self.subSampling
        #TODO if there is zoom hspace will change
        for channel in self.eeg.channels:
            x = 0
            while x < nSamp:
                ny = (((channel.readings[x] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                dc.DrawPoint(x, ny)
                x += subSampling
            y += hSpace


