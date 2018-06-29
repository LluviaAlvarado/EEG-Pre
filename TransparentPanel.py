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
            self.GetParent().zoomP.Refresh()
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


class windowPanel(wx.Panel):
    '''a transparent panel over the eegraph to draw windows'''
    def __init__(self, parent, over):
        wx.Panel.__init__(self, parent, size=(over.Size[0], over.Size[1]), pos=(60, 0))
        # vars for windows
        # at the beginning we show all windows
        self.windowState = 2
        # pointer to tab manager
        self.windows = parent.GetParent().GetParent().tabManager
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def setWindowState(self, state):
        ''' state 0 = no windows will show
            state 1 = only selected window shows
            state 2 = all windows are showed'''
        self.windowState = state
        self.Refresh()

    def onEraseBackground(self, event):
        # Overridden to do nothing to prevent flicker
        pass

    def msToPixel(self, ms):
        freq = self.GetParent().eeg.frequency / 1000
        reading = ms * freq
        subS = int(self.GetParent().graph.subSampling)
        incx = self.GetParent().graph.incx
        return int((reading * incx) / subS)

    def drawWindow(self, window, gc, path, color, pen):
        # gc is graphic context, color is wx.Colour and pen a wx.Pen
        gc.SetBrush(wx.Brush(color, style=wx.BRUSHSTYLE_SOLID))
        gc.SetPen(pen)
        start = self.msToPixel(window.stimulus - window.TBE)
        e = window.stimulus + (window.length - window.TBE)
        end = self.msToPixel(e)
        w = end - start
        h = self.Size[1]
        path.AddRectangle(start, 0, w, h)

    def drawWindows(self, gc):
        path = gc.CreatePath()
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
            if gc:
                for window in windows:
                    self.drawWindow(window, gc, path, wx.Colour(0, 0, 255, 10), wx.BLUE_PEN)
        return path

    # needs to repaint the eegraph and adds the zoom rectangle
    def OnPaint(self, event=None):
        print("pinto ventanas")
        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        # draw the windows
        path = self.drawWindows(gc)
        gc.FillPath(path)
        gc.StrokePath(path)

