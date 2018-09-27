import wx
from ModuleTree import ModuleTree, ModuleButton
'''This class manages the module tree from the main menu'''
class Level():

    def __init__(self, sizer, n):
        self.sizer = sizer
        self.childs = []
        for i in range(n):
            self.AddChild()

    def AddChild(self):
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.childs.append(s)
        self.sizer.AddSpacer(10)
        self.sizer.Add(s, 0, wx.EXPAND | wx.ALL, 5)

    def GetLevelModules(self):
        m = 0
        for ch in self.childs:
            m += ch.GetItemCount()
        return m

    def GetMIdx(self, p):
        i = 0
        for ch in self.childs:
            for child in ch.GetChildren():
                if child.Window == p:
                    return i
            i += 1
        return -1

class ModuleManager(wx.Panel):

    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.levels = []
        self.modules = ModuleTree(self, project.EEGS)
        # this class contains the whole project data
        self.project = project
        # solo filtrado, artefactos y caracterizacion tienen EEGs
        self.SetSizer(self.sizer)

    def SetStatusText(self, text):
        self.GetParent().SetStatusText(text)

    def setStatus(self, text, mouse):
        self.GetParent().setStatus(text, mouse)

    def ShowPossibleModules(self, p, modules):
        if p.lv == len(self.levels):
            # create new level for children
            s = wx.BoxSizer(wx.HORIZONTAL)
            if p.lv == 0:
                n = 1
                i = 0
            else:
                n = self.levels[p.lv-1].GetLevelModules()
                i = self.levels[p.lv-1].GetMIdx(p)
            self.levels.append(Level(s, n))
            sizer = self.levels[len(self.levels)-1].childs[i]
            self.sizer.Add(s, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        else:
            if p.parent is None:
                sizer = self.levels[p.lv].childs[0]
            else:
                i = self.levels[p.lv].GetMIdx(p)
                sizer = self.levels[p.lv].childs[i]
        # first lets clean the current ones
        l = 0
        for child in sizer.GetChildren():
            if child.Window.bw:
                sizer.Hide(child.Window)
                sizer.Remove(l)
            else:
                l += 1
        for m in modules:
            btn = ModuleButton(self, m, p.eegs, p.lv+1, p, True)
            sizer.Add(btn, 0, wx.EXPAND | wx.ALL, 5)
        self.sizer.Layout()


    def AddModule(self, m):
        if m.parent.lv == 0:
            sizer = self.levels[m.parent.lv].childs[0]
        else:
            i = self.levels[m.parent.lv].GetMIdx(m.parent)
            sizer = self.levels[m.parent.lv].childs[i]
        m.bw = False
        l = 0
        for child in sizer.GetChildren():
            if child.Window.bw:
                sizer.Hide(child.Window)
                sizer.Remove(l)
            else:
                l += 1
        if m.parent.lv < len(self.levels) - 1:
            # add childs to next level
            self.levels[m.lv].AddChild()
        self.sizer.Layout()
        self.modules.AddModule(m)

    def GetTree(self):
        return self.modules.SaveTree()

    def closeWindows(self):
        self.modules.closeAll()
