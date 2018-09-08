import wx


class CgraphPanel(wx.Panel):

    def __init__(self, parent, ica, w, h):
        wx.Panel.__init__(self, parent, size=(w, h),
                          style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.paint = True
        # var for repaint
        self.mirror = wx.EmptyBitmap
        self.ica = ica
        self.timeLapse = 0
        self.incx = 1
        self.w = w
        # list of components in screen and start position
        self.comPosition = []
        # vars for create a window
        self.newWin = False
        # vars for zooming
        self.zoom = False
        self.strComp = 0
        self.endComp = len(ica.components)
        self.totalComp = len(ica.components)
        self.strMs = 0
        self.zoomPile = []
        # var for moving graph
        self.move = False
        self.strMove = None
        self.endMove = None
        self.nSamp = len(ica.components[0])
        self.msShowing = ica.duration * 1000
        self.setSamplingRate()
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
        if self.newWin:
            self.GetParent().windowP.MovingMouse(event.GetPosition())

    def OnClickReleased(self, event):

        if self.move:
            if self.strMove is not None:
                self.endMove = event.GetPosition()
                self.moveGraph()
                self.strMove = None
                self.endMove = None
        else:
            self.GetParent().zoomP.OnClickReleased(event.GetPosition())

        if self.newWin:
            self.GetParent().windowP.OnClickReleased(event.GetPosition())

    # moves the components when it is zoomed
    def moveGraph(self):
        if self.zoom:
            pos = self.comPosition
            start = self.strMove
            end = self.endMove

            if len(pos) < 2:
                compH = self.Size[1]
            else:
                c = pos[0]
                cx = pos[1]
                compH = cx[1] - c[1]
            height = abs(end[1] - start[1])
            compsMoved = int(height / compH)
            compsShowing = self.endComp - self.strComp

            if end[1] < start[1]:
                self.strComp += compsMoved
            else:
                self.strComp -= compsMoved
            self.endComp = self.strComp + compsShowing
            # making sure it is a valid index
            if self.strComp < 0 or self.endComp < 0:
                self.strComp = 0
                self.endComp = compsShowing
            if self.strComp > len(self.ica.components) - 1 or self.endComp > self.totalComp - 1:
                self.strComp = self.totalComp - compsShowing
                self.endComp = self.totalComp

            length = abs(end[0] - start[0])

            # getting the readings to show
            endMs = self.strMs + self.msShowing
            if end[0] < start[0]:
                self.strMs += (length * self.timeLapse) / self.incx
                # make sure it is not longer than the actual readings
                if (self.strMs + endMs) > self.ica.duration * 1000:
                    self.strMs = len(self.ica.components) - self.msShowing
            else:
                self.strMs -= (length * self.timeLapse) / self.incx
                # make sure it does not go to negative index
                if self.strMs < 0:
                    self.strMs = 0

            # repainting
            self.paint = True
            self.GetParent().Refresh()
            # changing channel labels
            ch, read = self.getViewChannels()
            self.GetParent().timeRuler.update()
            self.GetParent().ampRuler.zoomManager(len(ch))
            self.GetParent().componentList.adjustment(read)
            self.strMove = self.endMove

    def setSamplingRate(self):
        if self.msShowing < self.w:
            self.incx = self.w / self.msShowing
            self.timeLapse = 1
        else:
            self.incx = 1
            self.timeLapse = self.msShowing / self.w

    # gets the selected electrodes to graph
    def getChecked(self):
        checked = self.GetParent().selected.GetCheckedItems()
        channels = []
        for ix in checked:
            if ix < len(self.ica.components):
                channels.append(self.ica.components[ix])
        return channels

    # changes the value for printable purposes
    def ChangeRange(self, v, nu, nl):
        oldRange = self.ica.amUnits[0] - self.ica.amUnits[1]
        newRange = nu - nl
        newV = round((((v - self.ica.amUnits[1]) * newRange) / oldRange) + nl, 2)
        return newV

    def resetZoom(self):
        self.zoom = False
        self.strMs = 0
        self.strComp = 0
        self.endComp = len(self.getChecked())
        self.msShowing = self.ica.duration * 1000
        self.setSamplingRate()
        self.zoomPile = []
        # repainting
        self.paint = True
        self.GetParent().Refresh()

    def apply(self):
        # repainting
        self.paint = True
        self.GetParent().Refresh()

    def returnZoom(self):
        if len(self.zoomPile) > 0:
            zoom = self.zoomPile.pop(len(self.zoomPile) - 1)
            self.strMs = zoom[0]
            self.timeLapse = zoom[1]
            self.incx = zoom[2]
            self.strComp = zoom[3]
            self.endComp = zoom[4]
            self.msShowing = zoom[5]
            # repainting
            self.paint = True
            self.GetParent().Refresh()
            # changing channel labels
            ch, read = self.getViewChannels()
            self.GetParent().timeRuler.update()
            self.GetParent().ampRuler.zoomManager(len(ch))
            self.GetParent().componentList.adjustment(read)
        else:
            ch, read = self.getViewChannels()
            self.GetParent().timeRuler.update()
            self.GetParent().ampRuler.zoomManager(len(ch))
            self.GetParent().componentList.adjustment()
            self.resetZoom()

    def setZoom(self, start, end):
        # adding this zoom to the pile
        self.zoomPile.append([self.strMs, self.timeLapse, self.incx, self.strComp, self.endComp, self.msShowing])
        self.zoom = True
        tmpS = self.strComp

        i = 0
        pos = self.comPosition
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= start[1] <= cx[1]:
                break
            i += 1
        self.strComp = i
        i = 0
        while i < len(pos) - 1:
            c = pos[i]
            cx = pos[i + 1]
            if c[1] <= end[1] <= cx[1]:
                break
            i += 1
        self.endComp = i + 1
        if self.endComp <= self.strComp:
            self.endComp = self.strComp + 1
        tmpE = self.endComp - self.strComp
        self.strComp += tmpS
        self.endComp = self.strComp + tmpE
        # getting the readings to show
        startr = self.strMs
        self.strMs += (start[0] * self.timeLapse) / self.incx
        endMs = startr + (end[0] * self.timeLapse) / self.incx
        self.msShowing = endMs - self.strMs
        if self.msShowing < 10:
            self.msShowing = 10
        if self.strMs + self.msShowing > 1 * 1000:
            self.strMs = len(self.ica.components) - self.msShowing
        self.setSamplingRate()
        # repainting
        self.paint = True
        self.GetParent().Refresh()
        # changing channel labels
        ch, read = self.getViewChannels()
        self.GetParent().ampRuler.zoomManager(len(ch))
        self.GetParent().componentList.adjustment(read)
        # self.GetParent().componentList.adjustment(ch)

    def getViewChannels(self):
        checked = self.getChecked()
        dchecked = self.GetParent().selected.GetCheckedItems()
        channels = []
        read = []
        # if there is zoom
        if self.zoom:
            i = self.strComp
            r = self.endComp - i
            if self.endComp > len(checked):
                i -= (self.endComp - len(checked))
                self.endComp = len(checked)
            if r > len(checked):
                self.endComp = len(checked)
            if i < 0:
                i = 0
            self.strComp = i
            while i < self.endComp:
                channels.append(checked[i])
                read.append(dchecked[i])
                i += 1
        else:
            channels = checked
        return channels, read

    def msToReading(self, ms):
        return int((ms * self.nSamp) / (self.ica.duration * 1000))

    def OnPaint(self, event=None):
        # buffered so it doesn't paint channel per channel
        if self.paint:
            dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
            dc.Clear()
            dc.SetPen(wx.Pen(wx.BLACK, 4))
            y = 0
            amUnits = self.ica.amUnits
            timeLapse = self.timeLapse
            incx = self.incx
            self.comPosition = []
            # defining channels to plot
            channels, read = self.getViewChannels()
            if len(channels) > 0:
                hSpace = (self.Size[1] - 5) / len(channels)
                w = self.w
                dc.SetPen(wx.Pen(wx.BLACK, 1))
                c = 0
                for channel in channels:
                    x = 0
                    ms = self.strMs
                    i = self.msToReading(ms)
                    self.comPosition.append([c, y])
                    while i < self.nSamp:
                        inci = self.msToReading(ms + timeLapse)
                        ny = (((channel[i] - amUnits[1]) * ((y + hSpace) - y)) / (amUnits[0] - amUnits[1])) + y
                        if inci > self.nSamp - 1:
                            ny2 = ny
                        else:
                            ny2 = (((channel[inci] - amUnits[1]) * ((y + hSpace) - y)) / (
                                    amUnits[0] - amUnits[1])) + y
                        if abs(ny - ny2) > 3 or (x + incx) > 3:
                            dc.DrawLine(x, ny, x + incx, ny2)
                        else:
                            dc.DrawPoint(x, ny)
                        ms += timeLapse
                        i = self.msToReading(ms)
                        x += incx
                    y += hSpace
                    c += 1
            self.mirror = dc.GetAsBitmap()
            self.paint = False
        else:
            dc = wx.BufferedPaintDC(self, style=wx.BUFFER_CLIENT_AREA)
            dc.DrawBitmap(self.mirror, 0, 0)
