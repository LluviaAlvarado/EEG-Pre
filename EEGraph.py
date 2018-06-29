# imports

import wx
from TransparentPanel import *


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
        # creating a ruler for each channel
        values = []
        values.append(self.eeg.amUnits[0])
        half = (self.eeg.amUnits[0] - self.eeg.amUnits[1]) / 2
        values.append(self.eeg.amUnits[0] - half)
        values.append(self.eeg.amUnits[1])
        ampRuler = customRuler(self, wx.VERTICAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels), num)
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

        self.increment = (self.max - self.min) / (self.width)

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


class graphPanel(wx.Panel):

    def __init__(self, parent, eeg, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.subSampling = 0
        self.incx = 1
        self.first = True
        self.w = self.Size[0]
        # list of channels in screen and start position
        self.chanPosition = []
        # vars for zooming
        self.zoom = False
        self.strCh = 0
        self.endCh = len(eeg.channels)
        self.totalChan = len(eeg.channels) + len(eeg.additionalData)
        self.strRead = 0
        self.zoomPile = []
        self.endRead = 0
        # var for moving graph
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
            self.GetParent().zoomP.OnClickDown(event.GetPosition())

    def MovingMouse(self, event):
        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = self.endMove
        else:
            self.GetParent().zoomP.MovingMouse(event.GetPosition())

    def OnClickReleased(self, event):

        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = None
                self.endMove = None
        else:
            self.GetParent().zoomP.OnClickReleased(event.GetPosition())

    # moves the eeg when it is zoomed
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
            # making sure it is a valid index
            if self.strCh < 0 or self.endCh < 0:
                self.strCh = 0
                self.endCh = chansShowing
            if self.strCh > len(self.eeg.channels) - 1 or self.endCh > self.totalChan - 1:
                self.strCh = self.totalChan - chansShowing
                self.endCh = self.totalChan

            length = abs(end[0] - start[0])

            # getting the readings to show
            res = abs(self.endRead - self.strRead)
            if end[0] < start[0]:
                self.strRead += (length * self.subSampling) / self.incx
                # make sure it is not longer than the actual readings
                if (self.strRead + res) > self.nSamp:
                    self.strRead = (self.nSamp - 1) - res
            else:
                self.strRead -= (length * self.subSampling) / self.incx
                # make sure it does not go to negative index
                if self.strRead < 0:
                    self.strRead = 0

            # repainting
            self.Refresh()
            # refresh the window panel
            self.GetParent().windowP.Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].moveZom(self.strRead, self.endRead)
            chil[4].zoomManager(len(ch))
            chil[5].adjustment(ch)
            self.strMove = self.endMove

    '''sets the how many readings will we skip
     is set as a value from 0 to 100 represents 
     the % of the readings to use'''

    def setSamplingRate(self, nSamp):
        if nSamp < self.Size[0]:
            self.incx = int(self.Size[0] / nSamp)
            self.subSampling = 1
        else:
            self.subSampling = (nSamp / self.Size[0])
            self.incx = 1

    # gets the selected electrodes to graph
    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.eeg.channels):
                channels.append(self.eeg.channels[ix])
            else:
                channels.append(self.eeg.additionalData[ix-len(self.eeg.channels)])
        return channels

    # changes the value for printable purposes
    def ChangeRange(self, v, nu, nl):
        oldRange = self.eeg.amUnits[0] - self.eeg.amUnits[1]
        newRange = nu - nl
        newV = round((((v - self.eeg.amUnits[1]) * newRange) / oldRange) + nl, 2)
        return newV

    def resetZoom(self):
        self.zoom = False
        self.strRead = 0
        self.strCh = 0
        self.endCh = len(self.getChecked())
        self.setSamplingRate(self.nSamp)
        self.zoomPile = []
        self.Refresh()
        # refresh the window panel
        self.GetParent().windowP.Refresh()

    def apply(self):
        self.Refresh()
        # refresh the window panel
        self.GetParent().windowP.Refresh()

    def returnZoom(self):
        if len(self.zoomPile) > 0:
            zoom = self.zoomPile.pop(len(self.zoomPile) - 1)
            self.strRead = zoom[0]
            self.subSampling = zoom[1]
            self.incx = zoom[2]
            self.strCh = zoom[3]
            self.endCh = zoom[4]
            # repainting
            self.Refresh()
            # refresh the window panel
            self.GetParent().windowP.Refresh()
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].zoomOut()
            chil[4].zoomManager(len(ch))
            chil[5].adjustment(ch)
        else:
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[3].update()
            chil[4].zoomManager(len(ch))
            chil[5].adjustment()
            self.resetZoom()

    def setZoom(self, start, end):
        # adding this zoom to the pile
        self.zoomPile.append([self.strRead, self.subSampling, self.incx, self.strCh, self.endCh])
        self.zoom = True
        tmpS = self.strCh

        i = 0
        pos = self.chanPosition
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= start[1] <= cx[1]:
                break
            i += 1
        self.strCh = i
        i = 0
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= end[1] <= cx[1]:
                break
            i += 1
        self.endCh = i + 1
        if self.endCh <= self.strCh:
            self.endCh = self.strCh + 1
        tmpE= self.endCh - self.strCh
        self.strCh+=tmpS
        self.endCh = self.strCh +tmpE
        # getting the readings to show
        startr = self.strRead
        self.strRead += (start[0] * self.subSampling) / self.incx
        endRead = startr + (end[0] * self.subSampling) / self.incx
        nsamp = endRead - self.strRead
        if nsamp < 10:
            nsamp = 10
        self.setSamplingRate(nsamp)
        # repainting
        self.Refresh()
        # refresh the window panel
        self.GetParent().windowP.Refresh()
        # changing channel labels
        chil = self.GetParent().GetChildren()
        ch = self.getViewChannels()
        chil[4].zoomManager(len(ch))
        chil[5].adjustment(ch)

    def getViewChannels(self):
        checked = self.getChecked()
        #print(len(checked))
        channels = []
        # if there is zoom
        if self.zoom:
            i = self.strCh
            r = self.endCh - i
            #print("I: "+str(i)+" R: "+str(r) + " E: "+str(self.endCh))

            if self.endCh > len(checked):
                i -= (self.endCh - len(checked))
                self.endCh = len(checked)
            if r > len(checked):
                self.endCh=len(checked)
            #print(i)
            #print(self.endCh)
            if i < 0:
                i=0
            self.strCh = i
            while i < self.endCh:
                channels.append(checked[i])
                i += 1
        else:
            channels = checked
        return channels

    def OnPaint(self, event=None):
        # buffered so it doesn't paint channel per channel
        dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
        dc.Clear()
        dc.SetPen(wx.Pen(wx.BLACK, 4))
        y = 0

        amUnits = self.eeg.amUnits
        sub = self.subSampling - int(self.subSampling)
        asub=0
        subSampling= int(self.subSampling)
        incx = self.incx
        self.chanPosition = []
        # defining channels to plot
        channels = self.getViewChannels()
        if len(channels) > 0:
            hSpace = (self.Size[1] - 5) / len(channels)
            w = self.w
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            # the reading to start with
            start = int(self.strRead)
            for channel in channels:
                x = 0
                i = start
                self.chanPosition.append([channel.label, y])
                u=0
                while x < w - incx:
                    asub += sub
                    r = i+subSampling # +int(asub)
                    if r >= self.nSamp: r = int(self.nSamp)-1
                    if i >= self.nSamp: i = int(self.nSamp)-1
                    ny = (((channel.readings[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                    ny2 = (((channel.readings[r] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                    if abs(ny - ny2) > 3 or (x + incx) > 3:
                        dc.DrawLine(x, ny, x + incx, ny2)
                    else:
                        dc.DrawPoint(x, ny)
                    i += subSampling # + int(asub)
                    if asub > 1: asub = asub - 1
                    x += incx
                    u+=1
                y += hSpace
                self.endRead=i
            chil = self.GetParent().GetChildren()
            if self.zoom:
                chil[3].zoomH(self.strRead, self.endRead, 0)
            if self.first:
                chil[3].zoomH(self.strRead, self.endRead, 1)
                self.first = False
