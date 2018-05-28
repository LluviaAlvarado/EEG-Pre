
from BaseWindow import *

app = wx.App()

mainW = BaseWindow(None, title='EEG Processing')
mainW.Show()

app.MainLoop()
