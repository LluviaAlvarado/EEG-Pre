import wx


class ConsolePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(300, parent.Size[1]))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.message = "##-----EEG Log-----##\n"
        self.process = False
        self.logconsole = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.logconsole.SetBackgroundColour(wx.LIGHT_GREY)
        sizer.Add(self.logconsole, -1, wx.EXPAND | wx.ALL)
        self.SetSizer(sizer)

    def append_txt(self, txt):
        self.logconsole.AppendText(txt)

    def ProcessLogOff(self):
        self.process = False
        tam = 0
        for j in range(self.logconsole.GetNumberOfLines()):
            tam += len(self.logconsole.GetLineText(j)) + 2
        tam -= 2
        self.logconsole.Remove(tam - 2, tam)
        self.append_txt("\n")

    def ProcessLogOn(self):
        self.process = True

    def AddToLog(self, s):
        self.message = s
