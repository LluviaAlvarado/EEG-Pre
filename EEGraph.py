#imports

import wx
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
        w = self.Size[0] - 30
        h = self.Size[1]
        self.graph = graphPanel(self, eeg, w, h)
        self.transparent = transparentPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, self.eeg.duration]
        self.timeRuler =  customRuler(self, wx.HORIZONTAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels))

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
        self.graph.resetZoom()

class customList(wx.Panel):
    def __init__(self, parent, orientation, style, channels):
        h = parent.graph.Size[1]-3
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

    def zooMa(self, channels):
        self.DestroyChildren()
        h = (self.Size[1]) / len(channels)
        i = 0
        posy = 0
        while i < len(channels):
            rule = wx.StaticText(self, i, channels[i].label, style=wx.ALIGN_CENTER, pos=(0, posy+(h/3)), size=(30, h))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.BOLD))
            # baseSizer.Add(rule, 0, wx.EXPAND, 0)
            posy += h
            i += 1


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
        self.h = parent.graph.Size[1]-3
        self.w = parent.graph.Size[0]
        self.nCh = nCh
        self.values = values

        self.Ogmax = 0
        self.Ogmin = 0

        self.Lgmax = 0
        self.Lgmin = 0

        self.max=0
        self.min=0

        self.opc = 0
        self.zoom =False
        self.num=0

        wx.Panel.__init__(self, parent, style=style, size=(30, self.h))
        self.eeg = parent.eeg
        baseSizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            self.opc = 1
            self.makeTimeRuler(self.eeg.duration)
            self.Ogmax = self.eeg.duration
            self.Lgmax = self.Ogmax
        else:
            self.opc = 2
            self.makeAmpRuler(nCh, values)

        self.SetSizer(baseSizer)

    def zoomH(self, s, e):
        self.max = self.ChangeRange(e,self.Lgmax,self.Lgmin)
        self.min = self.ChangeRange(s,self.Lgmax,self.Lgmin)
        self.zoom=True
        self.Refresh()

    def makeTimeRuler(self, values):
        h = 0
        self.font = wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                            wx.FONTWEIGHT_BOLD, False, 'Courier 10 Pitch')
        self.lapse = values
        self.place = (self.w/10)


        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def ChangeRange(self, v, nx, nm):
        oldRange = (self.w-91) - 0
        newRange = nx - nm
        newV = round((((v - 0) * newRange) / oldRange) + nm, 2)
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
            max = self.Ogmax
            min = self.Ogmin
            if self.zoom:
                max = self.max
                min = self.min
                self.Lgmax =self.max
                self.Lgmin =self.min

            dc.DrawRectangle(0, 0, self.w - 91, 30)
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen('#000000'))
            dc.SetTextForeground('#000000')
            RM = 4
            l = (self.w-91)/100
            u=0
            i=0
            while i < (self.w-91):
                if (u % 10) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 10)
                    y = self.ChangeRange(i, max, min)
                    w, h = dc.GetTextExtent(str(y))
                    dc.DrawText(str(y), i + RM - w / 2, 11)

                elif (u % 5) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 8)

                elif not (u % 1):

                    dc.DrawLine(i + RM, 0, i + RM, 4)

                u+=1
                i+=l
            dc.DrawLine((self.w-93) , 0, (self.w-93), 10)
            w, h = dc.GetTextExtent(str(max))
            dc.DrawText(str(round(max,2)), (self.w-93) - w, 11)

        else:
            h = self.h / self.nCh
            if self.zoom:
                h = self.h /self.num
            i = 0
            posy = 0
            if h < 12:
                while i < self.nCh:
                    dc.DrawRectangle(0, posy, 30, posy+h)
                    dc.DrawText(str(self.values[0]), 0, posy + 1)
                    posy += h
                    i += 1
            elif 12 < h < 35:
                while i < self.nCh:
                    dc.DrawRectangle(0, posy, 30, posy+h)
                    dc.DrawText(str(self.values[0]), 0, posy + 1)
                    dc.DrawText(str(self.values[2]), 0, (posy+h) - 8)

                    posy += h
                    i += 1
            elif h >= 35:
                while i < self.nCh:
                    dc.DrawRectangle(0, posy, 30, posy+h)
                    dc.DrawText(str(self.values[0]), 0, posy + 1)
                    dc.DrawLine(15, posy + 2, 30, posy + 2)
                    dc.DrawText(str(self.values[1]), 0, posy + (h/2))
                    dc.DrawLine(15, posy + (h/2), 30, posy + (h/2))
                    dc.DrawText(str(self.values[2]), 0, posy + (h-8))
                    dc.DrawLine(15, posy + (h-3), 30, posy + (h-3))

                    posy += h
                    i += 1
        self.zoom=False




    def makeAmpRuler(self, nCh, values):
        self.font = wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

        h = (self.Size[1]) / nCh
        i = 0
        posy = 0
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        '''while i < nCh:

            rule = wx.StaticText(self, -1, str(values[0]), style=wx.ALIGN_CENTER, pos=(0, posy), size=(30, h))
            ruler = wx.StaticText(self, -1, str(values[2]), style=wx.ALIGN_CENTER, pos=(0, posy + 9), size=(30, h))
            ruler.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            rule.SetFont(wx.Font(5, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            posy += h
            i += 1'''

    def zooMa(self, num):
        self.zoom = True
        self.num = num
        self.Refresh()

    def update(self):
        self.Lgmax = self.Ogmax
        self.Lgmin = self.Ogmin
        self.Refresh()

    def redo(self):
        self.Refresh()

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
        if self.zoom:
            self.zStart = pos

    def MovingMouse(self, pos):
        self.zEnd = pos
        if self.zoom and self.zStart is not None:
            self.OnPaint()

    def OnClickReleased(self, pos):
        self.zEnd = pos
        if self.zoom:
            self.GetParent().graph.setZoom(self.zStart, self.zEnd)
            self.OnPaint()
            self.GetParent().GetChildren()[2].zoomH(self.zStart[0], self.zEnd[0])
            self.zStart = None
            self.zEnd = None

    def onEraseBackground(self, event):
        #Overridden to do nothing to prevent flicker
        pass

    #needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self):
        self.GetParent().graph.Refresh()
        dc = wx.ClientDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if self.zoom:
            if gc:
                color = wx.Colour(255, 0, 0, 10)
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


class graphPanel(wx.Panel):

    def __init__(self, parent, eeg, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
            style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.subSampling = 0
        self.incx = 1
        #list of channels in screen and start position
        self.chanPosition = []
        #vars for zooming
        self.zoom = False
        self.strCh = 0
        self.endCh = len(eeg.channels)
        self.strRead = 0
        self.zoomPile = []
        #var for moving graph
        self.move = False
        self.strMove = None
        self.endMove = None
        self.nSamp = self.eeg.frequency * self.eeg.duration
        self.setSamplingRate(self.nSamp)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClickDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnClickReleased)
        self.Bind(wx.EVT_MOTION, self.MovingMouse)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnClickDown(self, event):
        if self.move:
            self.strMove = event.GetPosition()
        else:
            self.GetParent().transparent.OnClickDown(event.GetPosition())

    def MovingMouse(self, event):
        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
        else:
            self.GetParent().transparent.MovingMouse(event.GetPosition())

    def OnClickReleased(self, event):
        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = None
                self.endMove = None
        else:
            self.GetParent().transparent.OnClickReleased(event.GetPosition())

    #moves the eeg when it is zoomed
    def moveGraph(self):
        if self.zoom:
            pos = self.chanPosition
            start = self.strMove
            end = self.endMove
            if len(pos) < 2:
                chanH = self.Size[1]
            else:
                c = pos[0]
                cx = pos[1]
                chanH = cx[1] - c[1]
            height = abs(end[1] - start[1])
            chansMoved = int(height / chanH)
            chansShowing = self.endCh - self.strCh
            if end[1] < start[1]:
                self.strCh += chansMoved
            else:
                self.strCh -= chansMoved
            self.endCh = self.strCh + chansShowing
            #making sure it is a valid index
            if self.strCh < 0 or self.endCh < 0:
                self.strCh = 0
                self.endCh = chansShowing
            if self.strCh > len(self.eeg.channels) - 1 or self.endCh > len(self.eeg.channels) - 1:
                self.strCh = len(self.eeg.channels) - chansShowing
                self.endCh = len(self.eeg.channels)

            lenght = abs(end[0] - start[0])
            # getting the readings to show
            if end[0] < start[0]:
                self.strRead += (lenght * self.subSampling) / self.incx
                #make sure it is not longer than the actual readings
                if (self.strRead + (self.Size[0]*self.incx*self.subSampling)) > self.nSamp:
                    self.strRead = self.nSamp - 1 - self.Size[0]*self.incx*self.subSampling
            else:
                self.strRead -= (lenght * self.subSampling) / self.incx
                # make sure it does not go to negative index
                if self.strRead < 0:
                    self.strRead = 0
            aux = self.endCh - self.strCh
            # repainting
            self.Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].zooMa(len(ch))
            chil[4].zooMa(ch)


    '''sets the how many readings will we skip
     is set as a value from 0 to 100 represents 
     the % of the readings to use'''
    def setSamplingRate(self, nSamp):
        if nSamp < self.Size[0]:
            self.incx = int(self.Size[0] / nSamp)
            self.subSampling = 1
        else:
            self.subSampling = round(nSamp / self.Size[0])
            self.incx = 1

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

    def resetZoom(self):
        self.zoom = False
        self.strRead = 0
        self.strCh = 0
        self.endCh = len(self.eeg.channels)
        self.setSamplingRate(self.nSamp)
        self.zoomPile = []
        self.Refresh()

    def returnZoom(self):
        if len(self.zoomPile) > 0:
            zoom = self.zoomPile.pop(len(self.zoomPile)-1)
            self.strRead = zoom[0]
            self.subSampling = zoom[1]
            self.incx = zoom[2]
            self.strCh = zoom[3]
            self.endCh = zoom[4]
            # repainting
            self.Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].zooMa(len(ch))
            chil[4].zooMa(ch)
        else:
            self.resetZoom()

    def setZoom(self, start, end):
        # adding this zoom to the pile
        self.zoomPile.append([self.strRead, self.subSampling, self.incx, self.strCh, self.endCh])
        self.zoom = True
        i = 0
        pos = self.chanPosition
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i+1]
            if c[1] < start[1] < cx[1]:
                break
            i += 1
        self.strCh = i
        i = 0
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i+1]
            if c[1] < end[1] < cx[1]:
                break
            i += 1
        self.endCh = i + 1
        if self.endCh <= self.strCh:
            self.endCh = self.strCh + 1
        lenght = end[0] - start[0]
        #getting the readings to show
        startr = self.strRead
        self.strRead += (start[0] * self.subSampling) / self.incx
        endRead = startr + (end[0] * self.subSampling) / self.incx
        nsamp = endRead - self.strRead
        if nsamp < 10:
            nsamp = 10
        self.setSamplingRate(nsamp)
        #repainting
        self.Refresh()
        #changing channel labels
        chil = self.GetParent().GetChildren()
        ch = self.getViewChannels()
        chil[3].zooMa(len(ch))
        chil[4].zooMa(ch)

    def getViewChannels(self):
        checked = self.getChecked()
        channels = []
        #if there is zoom
        if self.zoom:
            i = self.strCh
            while i < self.endCh:
                channels.append(checked[i])
                i += 1
        else:
            channels = checked
        return channels


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
        channels = self.getViewChannels()
        hSpace = (self.Size[1] - 5) / len(channels)
        w = self.Size[0]
        dc.SetPen(wx.Pen(wx.BLACK, 1))
        #the reading to start with
        start = int(self.strRead)
        for channel in channels:
            x = 0
            i = start
            self.chanPosition.append([channel.label, y])
            while x < w - incx:
                ny = (((channel.readings[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                ny2 = (((channel.readings[i+subSampling] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                if abs(ny - ny2) > 3 or (x + incx) > 3:
                    dc.DrawLine(x, ny, x + incx, ny2)
                else:
                    dc.DrawPoint(x, ny)
                i += subSampling
                x += incx
            y += hSpace


