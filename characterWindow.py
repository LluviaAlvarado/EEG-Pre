# Imports

# local imports
from WindowEditor import *
from WindowDialog import *


class characterWindow(wx.Frame):
    """
    window that contains the list of
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Caracteristicas")
        self.SetSize(400, 200)
        self.Centre()
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        self.fftSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.fftButton = wx.Button(self.pnl, label="FFT", size=(330, 10))
        self.fftButton.Bind(wx.EVT_BUTTON, self.applyFFT)
        self.confftButton = wx.Button(self.pnl, label="...", size=(50, -1))
        self.confftButton.Bind(wx.EVT_BUTTON, self.confFFT)

        self.AUCButton = wx.Button(self.pnl, label="Area bajo la curva")
        self.AUCButton.Bind(wx.EVT_BUTTON, self.applyAUC)

        self.MaxVButton = wx.Button(self.pnl, label="Voltaje maximo")
        self.MaxVButton.Bind(wx.EVT_BUTTON, self.applyMV)

        self.fftSizer.Add(self.fftButton, 0, wx.EXPAND ,  7)
        self.fftSizer.Add(self.confftButton, 0, wx.Left , 7)

        self.baseSizer.AddSpacer(20)
        self.baseSizer.Add(self.fftSizer, 0, wx.EXPAND | wx.ALL, 7)
        self.baseSizer.Add(self.AUCButton, 0, wx.EXPAND | wx.ALL, 7)
        self.baseSizer.Add(self.MaxVButton, 0, wx.EXPAND | wx.ALL, 7)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onCHClose()
        self.Destroy()

    def applyFFT(self, event):
        pass

    def confFFT(self, event):
        pass

    def applyAUC(self, event):
        pass

    def applyMV(self, event):
        pass
