import wx

'''a transparent panel over the eegraph to draw other elements
    like the zoom rectangle and windows'''


class zoomPanel(wx.Panel):

    def __init__(self, parent, over):
        wx.Panel.__init__(self, parent, size=(over.Size[0], over.Size[1]), pos=(60, 0))
        # vars for zoom
        self.zoom = False
        self.zStart = None
        self.zEnd = None
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
            # refresh the windows
            self.GetParent().windowP.Refresh()
            self.zStart = None
            self.zEnd = None

    def onEraseBackground(self, event):
        # Overridden to do nothing to prevent flicker
        pass

    # needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self):
        # self.GetParent().graph.paint = True
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
            self.GetParent().Refresh()


class windowPanel(wx.Panel):
    '''a transparent panel over the eegraph to draw windows'''
    def __init__(self, parent, over):
        wx.Panel.__init__(self, parent, size=(over.Size[0], over.Size[1]), pos=(60, 0))
        # vars for windows
        # at the beginning we show all windows
        self.windowState = 2
        # var for the creation of the new window
        # The reason for using static text instead of onPaint to test the speed in difference
        self.windowTBE = 0
        self.windowLength = 0
        self.est = wx.StaticText(self, 0, " ", style=wx.ALIGN_CENTER, pos=(-3, -1), size=(1, 2000))
        self.fill = False
        self.fillPos = 0
        self.fillw = 0
        self.mirror = wx.EmptyBitmap

        # Set the Color
        self.est.SetBackgroundColour((255, 0, 0))

        # pointer to tab manager
        self.windows = parent.GetParent().GetParent().tabManager
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def update(self):
        self.GetParent().graph.paint = True
        self.GetParent().Refresh()
        self.Refresh()

    def setWindowState(self, state):
        ''' state 0 = no windows will show
            state 1 = only selected window shows
            state 2 = all windows are showed'''
        self.windowState = state
        #self.update()
        self.GetParent().Refresh()
        self.Refresh()

    def onEraseBackground(self, event):
        # Overridden to do nothing to prevent flicker
        pass

    # checks if a window should be painted on screen
    def toShow(self, msS, s, e, msE):
        # checking from beginning to end of the window
        ms = s
        while ms <= e:
            if msS <= ms <= msE:
                return True
            ms += 1
        return False

    def msToPixel(self, ms, msE):
        length = self.GetParent().graph.msShowing
        return ((length - (msE - ms)) * self.GetParent().graph.incx) / self.GetParent().graph.timeLapse

    def drawWindow(self, window, gc, path, color, pen):
        # gc is graphic context, color is wx.Colour and pen a wx.Pen
        gc.SetBrush(wx.Brush(color, style=wx.BRUSHSTYLE_SOLID))
        gc.SetPen(pen)
        # let's check if we need to show them because of the zoom
        s = window.stimulus - window.TBE
        msS = self.GetParent().graph.strMs
        msE = msS + self.GetParent().graph.msShowing
        e = window.stimulus + (window.length - window.TBE)
        if self.toShow(msS, s, e, msE):
            path = gc.CreatePath()
            start = self.msToPixel(s, msE)
            if start < 0:
                start = 0
            end = self.msToPixel(e, msE)
            if end > self.GetParent().graph.w:
                end = self.GetParent().graph.w
            w = end - start
            h = self.Size[1]
            path.AddRectangle(start, 0, w, h)
            #drawing stimulus
            sx = self.msToPixel(window.stimulus, msE)
            gc.StrokeLine(sx, 0, sx, h)
            gc.DrawPath(path)

    def drawNewWindow(self, gc, color, pen):
        # gc is graphic context, color is wx.Colour and pen a wx.Pen
        gc.SetBrush(wx.Brush(color, style=wx.BRUSHSTYLE_SOLID))
        gc.SetPen(pen)
        # let's check if we need to show them because of the zoom
        path = gc.CreatePath()
        path.AddRectangle(self.fillPos, 0, self.fillw, 2000)
        gc.DrawPath(path)

    def drawWindows(self, gc):
        path = None
        # state 0 is ignored since we wont show any windows
        if self.windowState == 1:
            # the selected window will be showed in blue
            window = self.GetParent().eeg.windows[self.windows.GetSelection()]
            if gc and window is not None:
                self.drawWindow(window, gc, path, wx.Colour(0, 0, 255, 10), wx.BLUE_PEN)

        elif self.windowState == 2:
            # all windows will show, it might get messy
            # windows will show in gray and selected one in blue
            windows = self.GetParent().eeg.windows
            selected = self.windows.GetSelection()
            if gc:
                i = 0
                for window in windows:
                    if i == selected and not self.GetParent().v:
                        self.drawWindow(window, gc, path, wx.Colour(0, 0, 255, 10), wx.BLUE_PEN)
                    else:
                        self.drawWindow(window, gc, path, wx.Colour(150, 150, 150, 40), wx.GREY_PEN)
                    i += 1

    def MovingMouse(self, pos):
        pos = (pos[0], 0)
        self.est.SetPosition(pos)
        msS = self.GetParent().graph.strMs
        msE = msS + self.GetParent().graph.msShowing
        posMs = self.pixelToMs(pos[0])
        beforeEst = self.msToPixel(msS + posMs - self.windowTBE, msE)
        afterEst = self.msToPixel(msS + posMs + (self.windowLength - self.windowTBE), msE)
        self.fillPos = beforeEst
        self.fillw = afterEst - beforeEst
        self.GetParent().Refresh()
        self.Refresh()

    def OnClickReleased(self, pos):
        msS = self.GetParent().graph.strMs
        ms = int(self.pixelToMs(self.est.GetPosition()[0]) + msS)
        self.GetParent().GetParent().GetParent().createNewWindow(ms, self.windowTBE)
        l = len(self.GetParent().GetParent().GetParent().tabManager.GetChildren())-4
        self.GetParent().GetParent().GetParent().tabManager.SetSelection(l)

    def pixelToMs(self, apx):
        ms = ((apx * self.GetParent().graph.timeLapse) / self.GetParent().graph.incx)
        return int(ms)

    # shows the preview lines
    def show(self):
        self.est.Show()

    # hides the preview lines
    def hide(self):
        self.est.Hide()

    # needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self, event=None):
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        self.drawWindows(gc)
        if self.fill:
            self.drawNewWindow(gc, wx.Colour(255, 0, 0, 20), wx.RED_PEN)

