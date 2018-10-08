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
from copy import deepcopy


class Module:
    '''windows:
    0 = File
    1 = Filter
    2 = Artifact
    3 = Attributes
    4 = K-means
    5 = D Tree
    6 = Silhouette
    7 = Randindex'''
    def __init__(self, w, p=None, eegs=[], ch=[], db=None, sel=None):
        self.eegs = eegs
        self.parent = p
        self.children = ch
        self.window = w
        self.windowDB = db
        self.windowSelec = sel


class ModuleButton:

    def __init__(self, id, parent, module, eegs, p=None):
        self.ID = id
        self.module = module
        self.km = None
        self.parent = p
        self.parentWindow = parent
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

    def GetParent(self):
        return self.parentWindow

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

    def GetPossible(self):
        posible = []
        if self.module == 0:
            # file can add filter and artifact and attributes.
            # check if they're already in children
            if not self.isChildren(1):
                posible.append(1)
            if not self.isChildren(2):
                posible.append(2)
            if not self.isChildren(3):
                posible.append(3)
        elif self.module == 1:
            # filter can add artifact and attributes.
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

    def OpenModule(self):
        self.GetParent().HidePossible()
        if self.window is not None:
            self.window.Hide()
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
        self.window.Raise()

    def onCloseModule(self):
        self.window = None

    def updateEEGS(self, eegs):
        tmp = None
        if len(eegs) > 0:
            tmp = deepcopy(eegs[0])
        self.eegs = eegs_copy(eegs, tmp)
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
                self.window = DecisionTreeWindow(self.GetParent(), self.parent.windowDB, self.parent.windowSelec, self.actions, self)
            elif self.module == 6:
                self.window = SilhouetteWindow(self.GetParent(), self.parent.parent.km, self.parent.parent.windowDB, self.parent.parent.windowSelec, self.parent.parent)
            elif self.module == 7:
                self.window = RandIndexWindow(self.GetParent(),  self.parent.parent, self.parent.parent.windowDB)
            else:
                pass
        self.window.ReDo(self.actions, eegs)


class ModuleTree:

    def __init__(self, parent, eegs):
        self.idCount = 0
        self.parent = parent
        self.root = ModuleButton(self.idCount, parent, 0, eegs)

    def closeW(self, r):
        for c in r.children:
            self.closeW(c)
        if r.window is not None:
            r.window.Close()

    def closeAll(self):
        self.closeW(self.root)

    def AddModule(self, module):
        self.idCount += 1
        module.ID = self.idCount
        module.parent.children.append(module)

    def searchTree(self, r, id):
        if len(r.children) > 0:
            for c in r.children:
                 return self.searchTree(c, id)
        if r.ID == id:
            return r

    def GetModule(self, id):
        m = self.searchTree(self.root, id)
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
        ch.append(Module(r.module, r.parent, r.eegs, chr, r.windowDB, r.windowSelec))

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
        button = ModuleButton(self.idCount, self.parent, r.module, r.eegs, r.parent)
        self.idCount += 1
        button.windowDB = r.windowDB
        button.windowSelec = r.windowSelec
        button.children = chr
        ch.append(button)

    def LoadTree(self, tree):
        ch = []
        self.createTree(tree, ch)
        self.root.children = ch