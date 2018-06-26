# imports

import wx
import wx.lib.scrolledpanel as SP


class EEGraph(wx.Panel):
    '''this is a panel that displays
    an EEG for visual examination'''

    def __init__(self, parent, eeg, selected):
        h = parent.GetParent().GetParent().Size[1]
        h = h - 177
        w = parent.GetParent().GetParent().Size[0]
        w = w - (w / 5)
        wx.Panel.__init__(self, parent, size=(w, h), style=wx.BORDER_SUNKEN)
        self.eeg = eeg
        self.selected = selected
        self.toolbar = None
        # baseSizer
        baseSizer = wx.FlexGridSizer(2, 3, gap=(0, 0))

        # and to the right the eeg graph
        w = self.Size[0] - 30
        h = self.Size[1]
        self.graph = graphPanel(self, eeg, w, h)
        self.transparent = transparentPanel(self, self.graph)
        # bottom is reserved just for the time ruler
        values = [0, self.eeg.duration]
        self.timeRuler = customRuler(self, wx.HORIZONTAL, wx.SUNKEN_BORDER, values, len(self.eeg.channels))

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
        self.adjustment(channels)
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

    def __init__(self, parent, orientation, style, values, nCh):
        self.height = parent.graph.Size[1] - 3
        self.width = parent.graph.Size[0]
        self.values = values
        self.nCh = nCh
        self.increment = 0
        self.maxPile = []
        self.minPile = []

        self.max = 0
        self.min = 0

        self.opc = 0
        self.zoom = False
        self.num = 0

        self.eeg = parent.eeg
        baseSizer = wx.BoxSizer(orientation)
        if orientation == wx.HORIZONTAL:
            self.opc = 1
            wx.Panel.__init__(self, parent, style=style, size=(-1, 35))
            self.makeTimeRuler(self.eeg.duration)
            self.Ogmax = self.eeg.duration
            self.Ogmin = 0
            self.maxPile.append(self.Ogmax + 0)
            self.minPile.append(0)

        else:
            self.opc = 2
            wx.Panel.__init__(self, parent, style=style, size=(30, self.height))
            self.makeAmpRuler(nCh, values)

        self.SetSizer(baseSizer)

    def zoomH(self, s, e):
        self.max = self.ChangeRange(e, self.maxPile[len(self.maxPile) - 1], self.minPile[len(self.minPile) - 1])
        self.min = self.ChangeRange(s, self.maxPile[len(self.maxPile) - 1], self.minPile[len(self.minPile) - 1])

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
        newV = round((((v - 0) * newRange) / oldRange) + nm, 5)
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
                max = round(self.max, 2)
                min = round(self.min, 2)

            dc.DrawRectangle(0, 0, self.Size[0]-5, 30)
            dc = wx.PaintDC(self)
            dc.SetPen(wx.Pen('#000000'))
            dc.SetTextForeground('#000000')
            RM = 4
            l = (self.Size[0]-5) / 100
            u = 0
            i = 0
            while i < (self.Size[0]-5):
                if (u % 10) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 10)
                    y = round(self.ChangeRange(i, max, min), 2)
                    w, h = dc.GetTextExtent(str(y))
                    dc.DrawText(str(y), i + RM - w / 2, 11)
                    dc.DrawText("s", i + RM + w / 2, 11)


                elif (u % 5) == 0:
                    dc.DrawLine(i + RM, 0, i + RM, 8)

                elif not (u % 1):

                    dc.DrawLine(i + RM, 0, i + RM, 4)

                u += 1
                i += l
            dc.DrawLine((self.Size[0]-5 - 2), 0, (self.Size[0]-5 - 2), 10)
            w, h = dc.GetTextExtent(str(max))
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

    def zoomManager(self, num):
        self.zoom = True
        self.num = num
        self.Refresh()

    def update(self):
        self.maxPile = []
        self.minPile = []
        self.maxPile.append(self.Ogmax)
        self.minPile.append(self.Ogmin)
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

    def moveZoom(self, dis):
        d = 0
        if dis < 0:
            d = round((dis * -1) * self.increment, 8)
            if (self.minPile[len(self.minPile) - 1] - d) > 0:
                self.minPile[len(self.minPile) - 1] -= d
                self.maxPile[len(self.minPile) - 1] -= d
            else:
                self.minPile[len(self.minPile) - 1] -= self.minPile[len(self.minPile) - 1]
                self.maxPile[len(self.minPile) - 1] -= self.minPile[len(self.minPile) - 1]
        else:
            d = round(dis * self.increment, 8)
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


'''a transparent panel over the eegraph to draw other elements
    like the zoom rectangle and windows'''
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
        # Overridden to do nothing to prevent flicker
        pass

    # needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self):
        self.GetParent().Refresh()
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
        # list of channels in screen and start position
        self.chanPosition = []
        # vars for zooming
        self.zoom = False
        self.strCh = 0
        self.endCh = len(eeg.channels)
        self.totalChan = len(eeg.channels) + len(eeg.additionalData)
        self.strRead = 0
        self.zoomPile = []
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
            self.GetParent().transparent.OnClickDown(event.GetPosition())

    def MovingMouse(self, event):
        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = self.endMove
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
            if end[0] < start[0]:
                self.strRead += (length * self.subSampling) / self.incx
                # make sure it is not longer than the actual readings
                if (self.strRead + (self.Size[0] * self.incx * self.subSampling)) > self.nSamp:
                    self.strRead = self.nSamp - 1 - self.Size[0] * self.incx * self.subSampling
            else:
                self.strRead -= (length * self.subSampling) / self.incx
                # make sure it does not go to negative index
                if self.strRead < 0:
                    self.strRead = 0
            aux = self.endCh - self.strCh
            # repainting
            self.Refresh()

            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[2].moveZoom(self.strMove[0] - self.endMove[0])
            chil[3].zoomManager(len(ch))
            chil[4].adjustment(ch)
            self.strMove = self.endMove

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


    def apply(self):
        self.Refresh()

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
            # changing channel labels
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[2].zoomOut()
            chil[3].zoomManager(len(ch))
            chil[4].adjustment(ch)
        else:
            chil = self.GetParent().GetChildren()
            ch = self.getViewChannels()
            chil[2].update()
            chil[3].zoomManager(len(ch))
            chil[4].adjustment()
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
        lenght = end[0] - start[0]

        # getting the readings to show
        startr = self.strRead
        self.strRead += (start[0] * self.subSampling) / self.incx
        endRead = startr + (end[0] * self.subSampling) / self.incx
        nsamp = endRead - self.strRead
        if nsamp < 10:
            nsamp = 10
        self.setSamplingRate(nsamp)
        # repainting
        #print("Ini: "+str(self.strCh)+"  End: "+str(self.endCh))
        self.Refresh()
        # changing channel labels
        chil = self.GetParent().GetChildren()
        ch = self.getViewChannels()
        chil[3].zoomManager(len(ch))
        chil[4].adjustment(ch)

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
        subSampling=int(self.subSampling)
        incx = self.incx
        self.chanPosition = []
        # defining channels to plot
        channels = self.getViewChannels()
        if len(channels) > 0:
            hSpace = (self.Size[1] - 5) / len(channels)
            w = self.Size[0]
            dc.SetPen(wx.Pen(wx.BLACK, 1))
            # the reading to start with
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


