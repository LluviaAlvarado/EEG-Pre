# Imports
import wx


class WindowDialog(wx.Dialog):

    def __init__(self, parent, l, tbe):
        wx.Dialog.__init__(self, parent, title="Parametros para Ventaneo:",
                  size=(400, 120))
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        lenLabel = wx.StaticText(self, label="Longitud (ms):")
        tbeLabel = wx.StaticText(self, label="TAE (ms):")
        self.length = wx.TextCtrl(self, value=str(l))
        self.tbe = wx.TextCtrl(self, value=str(tbe))
        close = wx.Button(self, label="Aceptar")
        close.Bind(wx.EVT_BUTTON, self.close)
        sizer.Add(lenLabel, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(self.length, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(tbeLabel, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(self.tbe, 0, wx.CENTER | wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddSpacer(self.Size[0]/1.5)
        btnSizer.Add(close, 1, wx.RIGHT, 5)
        baseSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(btnSizer, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(baseSizer)
        self.Center()

    def close(self, event):
        self.Close(True)
