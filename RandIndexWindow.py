import wx
from sklearn.metrics.cluster import adjusted_rand_score


class RandIndexWindow(wx.Frame):

    def __init__(self, pa, p, db):
        wx.Frame.__init__(self, pa, -1, "RandIndex", style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        self.SetSize(600, 600)
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(600, 600))
        self.pbutton = p
        self.labels = p.km.labels
        labes = self.labels.tolist()
        length = len(db)
        self.label_k =[]
        for i in range(length):
            self.label_k.append(db[i][len(db[i])-1])

        set_l = set(self.label_k)
        set_l = list(set_l)
        set_n =[i for i in range(len(set_l))]
        class_ = []
        for i in range(len(self.label_k)):
            for u in range(len(set_n)):
                if set_l[u] == self.label_k[i]:
                   class_.append(set_n[u])

        baseContainer = wx.BoxSizer(wx.VERTICAL)

        comp = wx.ListCtrl(self.pnl, style= wx.LC_ICON, name="Elemento")
        print(adjusted_rand_score(class_, labes))

        baseContainer.Add(comp)



        self.pnl.SetSizer(baseContainer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Hide()

    def ReDo(self, d, e):
        pass