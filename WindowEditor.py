#Import
import wx


class WindowEditor (wx.Frame):

    def __init__(self, p, *args, **kw):
        # ensure the parent's __init__ is called
        super(WindowEditor, self).__init__(*args, **kw)
        # create base panel in the frame
        self.pnl = wx.Panel(self, size=(800, 600),
                            style=wx.TAB_TRAVERSAL | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN)
        self.path = p
