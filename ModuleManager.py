import wx

'''This class manages the module tree from the main menu'''
class ModuleManager(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        #TODO dibujar el árbol
        # solo filtrado, artefactos y caracterizacion tienen EEGs
        self.SetSizer(sizer)
