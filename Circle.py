from FilesWindow import *

class AddCircle:

    imgCtrl = None

    def __init__(self, diameter):
        self.diameter = diameter / 4
        self.offset = diameter
        self.separation = diameter + 50
        self.img = wx.Image('./Images/ps.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter / 4, diameter / 4)

    def addImg(self, panel, parent):
        if self.imgCtrl is not None:
            self.removeImg()
        self.parent = parent
        self.x = parent.x + self.offset
        self.y = parent.y
        self.imgCtrl = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(self.img), pos=[self.x, self.y])
        self.imgCtrl.Bind(wx.EVT_LEFT_DOWN, self.onClick)

    def removeImg(self):
        self.imgCtrl.Hide()
        panel = self.imgCtrl.GetParent()
        panel.Update()

    def onClick(self, event):
        self.removeImg()
        menu = wx.Menu()
        for (id, nombre) in Circle.menu_options:
            menu.Append(id, nombre)
            wx.EVT_MENU(menu, id, self.seleccionMenu)
        panel = self.imgCtrl.GetParent()
        panel.PopupMenu(menu, [self.x, self.y])
        menu.Destroy()

    def seleccionMenu(self, event):
        res = 'Nada'
        for i in Circle.menu_options:
            if(i[0]==event.GetId()):
                res = i[1]
        new = None
        #Todo: Hacer un diccionario con las funciones
        if res == 'Filtrado':
            new = FilterCircle([self.parent.x + self.separation, self.parent.y], self.parent.diameter, self.parent.mainW)
            new.addImg(self.parent.imgCtrl.GetParent())
        elif res == 'Artefacto':
            new = ArtifactCircle([self.parent.x + self.separation, self.parent.y], self.parent.diameter, self.parent.mainW)
            new.addImg(self.parent.imgCtrl.GetParent())
        if new is not None:
            self.parent.hijos.append(new)
        print(res)

class Circle:

    def __init__(self, pos, diameter, mainW):
        self.x, self.y = pos
        self.mainW = mainW
        self.diameter = diameter
        self.img = wx.Image(diameter, diameter)
        if Circle.plus is None:
            Circle.plus = AddCircle(diameter)

    #Todo: Convertir esto en un diccionario
    menu_options = [
        #[wx.NewId(),'Coherencia'],
        #[wx.NewId(),'PDC/DTF'],
        [wx.NewId(), 'Filtrado'],
        [wx.NewId(), 'Artefacto']
    ]
    childs = []
    plus = None

    def addImg(self, panel):
        self.imgCtrl = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(self.img), pos=[self.x, self.y])
        self.imgCtrl.Bind(wx.EVT_LEFT_DOWN, self.onClick)
        self.imgCtrl.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)

    def removeImg(self):
        self.imgCtrl.Hide()
        panel = self.imgCtrl.GetParent()
        panel.Update()

    def onClick(self, event):
        panel = self.imgCtrl.GetParent()
        Circle.plus.addImg(panel, self)
        panel.Refresh()

    def onDoubleClick(self, event):
        Circle.plus.removeImg()
        if self.mainW.filesWindow is None:
            self.mainW.filesWindow = FilesWindow(self.mainW)
        self.mainW.filesWindow.Show()


class FileCircle(Circle):

    def __init__(self, pos, diameter, mainW):
        super().__init__(pos, diameter, mainW)
        self.img = wx.Image('./Images/ArchivoIMG.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter, diameter)

class FilterCircle(Circle):

    def __init__(self, pos, diameter, mainW):
        super().__init__(pos, diameter, mainW)
        # TODO get another image
        self.img = wx.Image('./Images/ArchivoIMG.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter, diameter)

    # TODO open the correct frame
    def onDoubleClick(self, event):
        Circle.plus.removeImg()
        if self.mainW.filesWindow is None:
            self.mainW.filesWindow = FilesWindow(self.mainW)
        self.mainW.filesWindow.Show()

class CoherenceCircle(Circle):

    def __init__(self, pos, diameter):
        super().__init__(pos, diameter)
        self.img = wx.Image('./Images/CohIMG.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter, diameter)


class PDC_DTFCircle(Circle):

    def __init__(self, pos, diameter):
        super().__init__(pos, diameter)
        self.img = wx.Image('./Images/PDCDTF.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter, diameter)



class ArtifactCircle(Circle):

    def __init__(self, pos, diameter, mainW):
        super().__init__(pos, diameter, mainW)
        self.img = wx.Image('./Images/Grafica.png', wx.BITMAP_TYPE_ANY)
        self.img = self.img.Scale(diameter, diameter)
