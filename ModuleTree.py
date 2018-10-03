import wx
from FilesWindow import FilesWindow
from ArtifactEliminationWindow import ArtifactEliminationWindow
from BandpassFilter import PreBPFW
from WindowAttributes import WindowAttributes
from KMeansWindow import KMeansWindow
from DecisionTreeWindow import DecisionTreeWindow
from WindowDialog import ModuleHint
from SilhouetteWindow import SilhouetteWindow
from RandIndexWindow import RandIndexWindow
from Utils import eegs_copy
from copy import copy, deepcopy


class Module():
    '''windows:
    0 = File
    1 = Filter
    2 = Artifact
    3 = Attributes
    4 = K-means
    5 = D Tree
    6 = Silhouette
    7 = Randindex'''
    def __init__(self, w, lv, p=None, eegs=[], ch=[]):
        self.eegs = eegs
        self.parent = p
        self.children = ch
        self.window = w
        self.lv = lv


class ModuleButton(wx.BitmapButton):

    def __init__(self, parent, module, eegs, lv=0, p=None, bw=False):
        self.module = module
        self.bw = bw
        self.km = None
        bmp = self.GetBMP(bw)
        wx.BitmapButton.__init__(self, parent, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp, size=(bmp.GetWidth(), bmp.GetHeight()))
        self.parent = p
        self.lv = lv
        self.children = []
        tmp = None
        if len(eegs) > 0:
            tmp = deepcopy(eegs[0])
        self.eegs = eegs_copy(eegs, tmp)
        self.actions = []
        self.windowDB = None
        self.windowSelec = None
        self.hint = None
        self.window = None
        self.Bind(wx.EVT_BUTTON, self.OpenModule)
        self.Bind(wx.EVT_ENTER_WINDOW, self.Hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.UnHover)
        self.Bind(wx.EVT_RIGHT_DOWN, self.ShowModules)

    def GetBMP(self, bw):
        if bw:
            #TODO agregar imagenes grises
            if self.module == 1:
                bmp = wx.Bitmap("Images/gFiltradoIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 2:
                bmp = wx.Bitmap("Images/gEliminacionAIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 3:
                bmp = wx.Bitmap("Images/gCaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 4:
                bmp = wx.Bitmap("Images/gKmeansIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 5:
                bmp = wx.Bitmap("Images/gArbolDIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 6:
                bmp = wx.Bitmap("Images/gSilhouetteIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 7:
                bmp = wx.Bitmap("Images/gRandindexIMG.png", wx.BITMAP_TYPE_PNG)
        else:
            if self.module == 0:
                bmp = wx.Bitmap("Images/ArchivoIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 1:
                bmp = wx.Bitmap("Images/FiltradoIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 2:
                bmp = wx.Bitmap("Images/EliminacionAIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 3:
                bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 4:
                bmp = wx.Bitmap("Images/KmeansIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 5:
                bmp = wx.Bitmap("Images/ArbolDIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 6:
                bmp = wx.Bitmap("Images/SilhouetteIMG.png", wx.BITMAP_TYPE_PNG)
            elif self.module == 7:
                bmp = wx.Bitmap("Images/RandindexIMG.png", wx.BITMAP_TYPE_PNG)
        return bmp

    def Hover(self, e):
        if self.bw:
            # when a possible is hovered it shows colored img
            bmp = self.GetBMP(False)
            self.SetBitmap(bmp)
        x = self.Position.x + self.Size[0]
        y = self.Position.y + self.Size[1] / 2
        self.hint = ModuleHint(self, self.module, wx.Point(x, y))
        self.hint.Show()

    def UnHover(self, e):
        if self.bw:
            # when a possible is un-hovered it shows gray img
            bmp = self.GetBMP(True)
            self.SetBitmap(bmp)
        self.hint.Close()

    def ShowModules(self, e):
        self.GetParent().HidePossible()
        self.GetParent().ShowPossibleModules(self, self.GetPosible())

    def isChildren(self, m):
        for ch in self.children:
            if ch.module == m:
                return True
        return False

    def GetChIdx(self, m):
        i = 0
        for ch in self.children:
            if m == ch:
                return i
            i += 1
        return -1

    def GetPosible(self):
        posible = []
        if self.module == 0:
            # file can add filter and artifact and attributes
            # check if they're already in children
            if not self.isChildren(1):
                posible.append(1)
            if not self.isChildren(2):
                posible.append(2)
            if not self.isChildren(3):
                posible.append(3)
        elif self.module == 1:
            # filter can add artifact and attributes
            if not self.isChildren(2):
                posible.append(2)
            if not self.isChildren(3):
                posible.append(3)
        elif self.module == 2:
            # artifact can add filter and attributes
            if not self.isChildren(1):
                posible.append(1)
            if not self.isChildren(3):
                posible.append(3)
        elif self.module == 3:
            # attributes can add k-means and decision tree
            if not self.isChildren(4):
                posible.append(4)
            if not self.isChildren(5):
                posible.append(5)
        elif self.module == 4:
            # k-means can add silhouette and randindex
            if not self.isChildren(6):
                posible.append(6)
            if not self.isChildren(7):
                posible.append(7)
        return posible

    def OpenModule(self, e):
        if self.bw:
            self.GetParent().AddModule(self)
        else:
            self.GetParent().HidePossible()
            if self.window is None:
                self.actions = []
                if self.module == 0:
                    self.window = FilesWindow(self.GetParent(), self)
                elif self.module == 1:
                    self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
                elif self.module == 2:
                    self.window = ArtifactEliminationWindow(self.GetParent(), self.eegs, self.actions, self)
                elif self.module == 3:
                    self.window = WindowAttributes(self.GetParent(), self.eegs, self, self.actions)
                elif self.module == 4:
                    self.window = KMeansWindow(self.GetParent(), self.parent, self.actions, self)
                elif self.module == 5:
                    self.window = DecisionTreeWindow(self.GetParent(), self.parent.windowDB, self.parent.windowSelec, self.actions, self)
                elif self.module == 6:
                    self.window = SilhouetteWindow(self.GetParent(), self.parent.parent.km, self.parent.parent.windowDB, self.parent.parent.windowSelec, self.parent.parent)
                elif self.module == 7:
                    self.window = RandIndexWindow(self.GetParent(),  self.parent.parent, self.parent.parent.windowDB)
                else:
                    pass
            self.window.Show()
        e.Skip()

    def onCloseModule(self):
        self.window = None

    def updateEEGS(self, eegs):
        self.eegs = eegs
        if self.window is None:
            if self.module == 0:
                self.window = FilesWindow(self.GetParent(), self)
            elif self.module == 1:
                self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
            elif self.module == 2:
                self.window = ArtifactEliminationWindow(self.GetParent(), self.eegs, self.actions, self)
            elif self.module == 3:
                self.window = WindowAttributes(self.GetParent(), self.eegs, self, self.actions)
            elif self.module == 4:
                self.window = KMeansWindow(self.GetParent(), self.windowDB, self.actions, self)
            elif self.module == 5:
                self.window = DecisionTreeWindow(self.GetParent(), self.windowDB, self.windowSelec, self.actions, self)
            elif self.module == 6:
                self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
            elif self.module == 7:
                self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
            else:
                pass
        self.window.ReDo(self.actions, eegs)


class ModuleTree():

    def __init__(self, parent, eegs):
        self.parent = parent
        self.root = ModuleButton(parent, 0, eegs)
        parent.sizer.Add(self.root, 0, wx.CENTER | wx.ALL, 2)

    def closeW(self, r):
        for c in r.children:
            self.closeW(c)
        if r.window is not None:
            r.window.Close()

    def closeAll(self):
        self.closeW(self.root)

    def AddModule(self, module):
        module.parent.children.append(module)

    def searchTree(self, r, mod, lv, l):
        if len(r.children) > 0:
            for c in r.children:
                 return self.searchTree(c, mod, lv, l+1)
        if r.module == mod and l == lv:
            return r

    def GetModule(self, module, lv):
        m = self.searchTree(self.root, module, lv, 0)
        return m

    def DeleteModule(self, p):
        # there's no readjustment it just deletes the module and its children
        del p

    def forward(self, ch):
        for c in ch:
            c.updateEEGS(c.parent.eegs)
            self.forward(c.children)

    def ForwardChanges(self, r):
        # this makes the eeg changes for all children modules of r
        self.forward(r.children)

    def convertTree(self, r, ch):
        chr = []
        for c in r.children:
            self.convertTree(c, chr)
        ch.append(Module(r.module, r.lv, r.parent, r.eegs, chr))

    def SaveTree(self):
        ch = []
        self.convertTree(self.root, ch)
        # for the root we don't save the eegs since they're already saved in project
        tree = Module(self.root.module, 0, ch=ch)
        return tree

    def createTree(self, r, ch):
        chr = []
        for c in r.children:
            self.createTree(c, chr)
        button = ModuleButton(self.parent, r.module, r.eegs, r.lv, r.parent)
        button.children = chr
        ch.append(button)

    def LoadTree(self, tree):
        ch = []
        self.createTree(tree, ch)
        self.root.children = ch