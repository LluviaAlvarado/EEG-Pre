import wx
from ModuleTree import ModuleTree, ModuleButton
from Project import Project

'''This class manages the module tree from the main menu'''
class ModuleManager(wx.Panel):

    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.modules = ModuleTree(self, project.EEGS)
        # this class contains the whole project data
        self.project = project
        # solo filtrado, artefactos y caracterizacion tienen EEGs
        self.SetSizer(self.sizer)

    def GetTree(self):
        return self.modules.SaveTree()

    def closeWindows(self):
        self.modules.closeAll()
