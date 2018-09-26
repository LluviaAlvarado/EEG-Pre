import wx
from FilesWindow import FilesWindow
from ArtifactEliminationWindow import ArtifactEliminationWindow
from BandpassFilter import PreBPFW
from WindowAttributes import WindowAttributes
from KMeansWindow import KMeansWindow
from DecisionTreeWindow import DecisionTreeWindow


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

    def __init__(self, parent, module, eegs, lv=0, p=None):
        if module == 0:
            bmp = wx.Bitmap("Images/ArchivoIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 1:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 2:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 3:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 4:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 5:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 6:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        elif module == 7:
            bmp = wx.Bitmap("Images/CaracteristicasIMG.png", wx.BITMAP_TYPE_PNG)
        else:
            bmp = None
        wx.BitmapButton.__init__(self, parent, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp, size=(bmp.GetWidth(), bmp.GetHeight()))
        self.parent = p
        self.lv = lv
        self.children = []
        self.eegs = eegs
        self.actions = []
        self.windowDB = None
        self.windowSelec = None
        self.module = module
        self.window = None
        self.Bind(wx.EVT_BUTTON, self.OpenModule)
        self.Bind(wx.EVT_ENTER_WINDOW, self.Hover)

    def Hover(self, e):
        # TODO mostrar opciones de modulos
        pass

    def OpenModule(self, e):
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
                self.window = KMeansWindow(self.GetParent(), self.windowDB, self.actions, self)
            elif self.module == 5:
                self.window = DecisionTreeWindow(self.GetParent(), self.windowDB, self.windowSelec, self.actions, self)
            elif self.module == 6:
                self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
            elif self.module == 7:
                self.window = PreBPFW(self.GetParent(), self.eegs, self.actions, self)
            else:
                pass
        self.window.Show()

    def onCloseModule(self):
        self.window = None

    def updateEEGS(self, eegs):
        self.eegs = eegs
        if self.module == 0:
            self.window = FilesWindow(self.GetParent(), self)
        elif self.module == 1:
            self.window = PreBPFW(self.GetParent(), self.eegs, self)
        elif self.module == 2:
            self.window = ArtifactEliminationWindow(self.GetParent(), self.eegs, self)
        elif self.module == 3:
            self.window = WindowAttributes(self.GetParent(), self.eegs, self)
        elif self.module == 4:
            self.window = KMeansWindow(self.GetParent(), self.windowDB, self)
        elif self.module == 5:
            self.window = DecisionTreeWindow(self.GetParent(), self.windowDB, self.windowSelec, self)
        elif self.module == 6:
            self.window = PreBPFW(self.GetParent(), self.eegs, self)
        elif self.module == 7:
            self.window = PreBPFW(self.GetParent(), self.eegs, self)
        else:
            pass
        self.window.ReDo(self.actions)


class ModuleTree():

    def __init__(self, parent, eegs):
        self.parent = parent
        self.levels = []
        self.root = ModuleButton(parent, 0, eegs)
        parent.sizer.Add(self.root, 0, wx.CENTER|wx.ALL, 2)

    def closeW(self, r):
        for c in r.children:
            self.closeW(c)
        if r.window is not None:
            r.window.Close()

    def closeAll(self):
        self.closeW(self.root)

    def AddModule(self, p, module):
        if p.lv == len(self.levels):
            # create new level for children
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.levels.append(sizer)
            self.parent.sizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 0)
        else:
            sizer = self.levels[p.lv]
        new = ModuleButton(self.parent, module, p.eegs, p.lv+1, p)
        p.children.append(new)
        sizer.Add(new, 0, wx.CENTER | wx.ALL, 2)

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