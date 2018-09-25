import wx


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
    def __init__(self, w, p=None, eegs=[], ch=[]):
        self.eegs = eegs
        self.parent = p
        self.children = ch
        self.window = w


class ModuleButton(wx.BitmapButton):

    def __init__(self, parent, module, eegs, p):
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
        self.children = []
        self.eegs = eegs
        self.module = module



class ModuleTree():

    def __init__(self):
        self.root =

    def AddModule(self, p, new):
        new.parent = p
        p.children.append(new)

    def SaveTree(self):
        tree = None

        return tree

    def LoadTree(self, tree):
        pass