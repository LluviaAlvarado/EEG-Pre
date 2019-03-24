import wx


class RandIndexWindow(wx.Frame):

    def __init__(self, modulemanager, kmeans, features):
        wx.Frame.__init__(self, modulemanager, -1, "RandIndex", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(300, 300)
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(300, 300))
        self.pbutton = kmeans

        self.km_labels = kmeans.km.labels   #ndarray
        self.user_labels = [] #list
        for i in range(len(features)):
            self.user_labels.append(features[i][len(features[i]) - 1])

       #TODO aqui el randindex

        baseContainer = wx.BoxSizer(wx.VERTICAL)
        self.pnl.SetSizer(baseContainer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Hide()

    def ReDo(self, d, e):
        pass