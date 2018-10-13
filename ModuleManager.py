import threading
import time
import wx
from ModuleTree import ModuleTree, ModuleButton
from WindowDialog import ModuleHint
from os import getcwd

'''This class manages the module tree from the main menu'''


class ModuleManager(wx.Panel):

    def __init__(self, parent, project, log):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.treeView = wx.TreeCtrl(self, size=self.GetParent().GetSize(), style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS)
        self.modules = ModuleTree(self, project.EEGS)
        self.log = log
        # 110x110px size of button images
        image_list = wx.ImageList(110, 110)
        image_list.Add(wx.Image(getcwd() + "/Images/ArchivoIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/FiltradoIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gFiltradoIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/EliminacionAIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gEliminacionAIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gCaracteristicasIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/KmeansIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gKmeansIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/ArbolDIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gArbolDIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/SilhouetteIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gSilhouetteIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/RandindexIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        image_list.Add(wx.Image(getcwd() + "/Images/gRandindexIMG.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.treeView.AssignImageList(image_list)
        # adding the root to tree view
        self.root = self.treeView.AddRoot("")
        id = self.treeView.AppendItem(self.root, "", 0)
        self.treeView.SetItemData(id, self.modules.root)
        self.pModules = []
        # this class contains the whole project data
        self.project = project
        self.sizer.Add(self.treeView, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(self.sizer)
        self.treeView.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OpenModule)
        self.treeView.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.ShowPossibleModules)
        self.treeView.Bind(wx.EVT_TREE_SEL_CHANGED, self.ModuleSelected)
        self.Bind(wx.EVT_RIGHT_DOWN, self.HidePossible)
        self.Bind(wx.EVT_LEFT_DOWN, self.HidePossible)

    def ForwardChanges(self, r):
        self.modules.ForwardChanges(r)

    def setStatus(self, text, mouse):
        self.GetParent().GetParent().setStatus(text, mouse)

    def OpenModule(self, e):
        self.HidePossible()
        # this is needed to se focus on new frame
        wx.CallAfter(self.openM, e.GetItem())

    def openM(self, item):
        self.treeView.GetItemData(item).OpenModule()

    def ModuleSelected(self, e):
        idm = self.treeView.GetItemData(e.GetItem()).ID
        self.GetParent().GetParent().hintPnl.changeModule(idm)
        for m in self.pModules:
            if m.ID == idm:
                self.treeView.SetItemImage(e.GetItem(), self.getImage(m.module, False))
                self.AddModule(idm)
                return
        self.HidePossible()
        # self.log.AddToLog("Modulo Archivo seleccionado.\n")
        # TODO poner informacion en la ventana del log

    def getItem(self, module):
        return self.searchTree(self.treeView.RootItem, module)

    def searchTree(self, item, module):
        childr = self.treeView.GetChildrenCount(item, False)
        itm = None
        if childr > 0:
            (child, cookie) = self.treeView.GetFirstChild(item)
            while child.IsOk():
                if self.treeView.GetItemData(child) == module:
                    itm = child
                if itm is None:
                    itm = self.searchTree(child, module)
                (child, cookie) = self.treeView.GetNextChild(item, cookie)
        return itm

    def getImage(self, p, g):
        image = 0
        if g:
            if p == 1:
                image = 2
            elif p == 2:
                image = 4
            elif p == 3:
                image = 6
            elif p == 4:
                image = 8
            elif p == 5:
                image = 10
            elif p == 6:
                image = 12
            elif p == 7:
                image = 14
        else:
            if p == 1:
                image = 1
            elif p == 2:
                image = 3
            elif p == 3:
                image = 5
            elif p == 4:
                image = 7
            elif p == 5:
                image = 9
            elif p == 6:
                image = 11
            elif p == 7:
                image = 13
        return image

    def HidePossible(self, e=None):
        for m in self.pModules:
            self.treeView.Delete(self.getItem(m))
        self.pModules.clear()

    def ShowPossibleModules(self, e):
        # first hiding the actual possibles
        self.HidePossible()
        parent = self.treeView.GetItemData(e.GetItem())
        if parent is not None:
            possible = parent.GetPossible()
            self.pModules = []
            i = 1
            for p in possible:
                image = self.getImage(p, True)
                idx = self.treeView.AppendItem(e.GetItem(), "", image)
                module = ModuleButton(self.modules.idCount + i, self, p, [], parent)
                self.treeView.SetItemData(idx, module)
                self.pModules.append(module)
                i += 1
            self.treeView.Expand(e.GetItem())

    def AddModule(self, idm):
        self.setStatus("Agregando Módulo...", 1)
        i = 0
        for m in self.pModules:
            if m.ID == idm:
                break
            i += 1
        module = self.pModules.pop(i)
        if module.parent.module == 0:
            # file window needs to concatenate eegs
            module.parent.CreateConcatenated()
        module.setEEGS(module.parent.eegs)
        self.HidePossible()
        self.modules.AddModule(module)
        self.setStatus("", 0)

    def GetTree(self):
        return self.modules.SaveTree()

    def addLoaded(self, r, ri):
        image = self.getImage(r.module, True)
        idx = self.treeView.AppendItem(ri, "", image)
        self.treeView.SetItemData(idx, r)
        for ch in r.children:
            self.addLoaded(ch, idx)
        self.treeView.Expand(idx)

    def CreateTree(self, tree):
        self.modules.LoadTree(tree)
        self.treeView.DeleteAllItems()
        self.addLoaded(self.modules.root, self.treeView.RootItem)

    def closeWindows(self):
        self.HidePossible()
        self.modules.closeAll()
