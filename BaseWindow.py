import _pickle
import gzip
import os

from ModuleManager import *
from Project import *
from copy import deepcopy
from WindowDialog import WindowSaveOnExit
from CorrelationWindow import CorrelationWindow
wildcard = "EEG Pre Processing Project (*.eppp)|*.eppp"


class BaseWindow(wx.Frame):

    def __init__(self, *args, **kw):
        super(BaseWindow, self).__init__(*args, **kw)
        self.Maximize(True)
        self.currentDirectory = os.getcwd()
        self.project = Project()
        self.moduleManager = ModuleManager(self, self.project)
        self.aux = Project()
        # create the menu bar that we don't need yet
        self.makeMenuBar()
        # create the status bar
        self.CreateStatusBar()
        self.SetStatusText("")

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def HidePossible(self, event):
        self.moduleManager.HidePossible()
        event.Skip()

    def OnClose(self, event):
        if self.__eq__() == False:
            opc = 0
            with WindowSaveOnExit(self, opc) as dlg:
                dlg.ShowModal()
                if dlg.opc == 1:
                    self.OnSave(0)
                    self.Destroy()
                elif dlg.opc == 2:
                    self.Destroy()
        else:
            self.Destroy()

    def setAux(self, p):
        self.aux = deepcopy(p)

    def __eq__(self):

        firstCheck = True
        key = self.project.__dict__.keys()
        for i in key:
            if i != 'EEGS':
                if self.project.__dict__[i] != self.aux.__dict__[i]:
                    firstCheck = False
        secondCheck = True
        len1 = len(self.project.EEGS)
        len2 = len(self.aux.EEGS)
        if len1 != len2:
            secondCheck = False
        else:
            u = 0
            while u < len1:
                if self.project.EEGS[u].system10_20.__dict__ != self.project.EEGS[u].system10_20.__dict__:
                    secondCheck = False
                ch1 = len(self.project.EEGS[u].channels)
                ch2 = len(self.aux.EEGS[u].channels)
                if ch1 != ch2:
                    secondCheck = False
                else:
                    p = 0
                    while p < ch1:
                        if self.project.EEGS[u].channels[p].__dict__ != self.project.EEGS[u].channels[p].__dict__:
                            secondCheck = False
                        p += 1
                wn1 = len(self.project.EEGS[u].windows)
                wn2 = len(self.aux.EEGS[u].windows)
                if wn1 != wn2:
                    secondCheck = False
                else:
                    p = 0
                    while p < wn1:
                        if self.project.EEGS[u].windows[p].__dict__ != self.project.EEGS[u].windows[p].__dict__:
                            secondCheck = False
                        p += 1
                keys = self.project.EEGS[u].__dict__.keys()
                # print(self.project.EEGS[u].__dict__)
                # print(self.aux.EEGS[u].__dict__)
                for k in keys:
                    if k != 'system10_20' and k != 'channels' and k != 'windows' and k != 'channelMatrix':

                        if self.project.EEGS[u].__dict__[k] != self.aux.EEGS[u].__dict__[k]:
                            secondCheck = False
                u += 1
        if secondCheck and firstCheck:
            return True
        else:
            return False

    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        loadSessionItem = fileMenu.Append(-1, "&Cargar Proyecto...\tCtrl-A",
                                          "Carga un Proyecto anterior.")
        saveSessionItem = fileMenu.Append(-1, "&Guardar Proyecto...\tCtrl-S",
                                          "Guarda el Proyecto actual.")
        fileMenu.AppendSeparator()

        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(-1, "&Salir", "Cerrar el programa.")

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(-1, "&Ayuda")
        #TODO quitar correlacion
        corrItem = helpMenu.Append(-1, "&Correlación")
        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&Proyecto")
        menuBar.Append(helpMenu, "&Ayuda")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnSave, saveSessionItem)
        self.Bind(wx.EVT_MENU, self.OnLoad, loadSessionItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.correlacionar, corrItem)

    def correlacionar(self, e):
        CorrelationWindow(self).Show()

    def setStatus(self, st, mouse):
        self.SetStatusText(st)
        if mouse == 0:
            myCursor = wx.Cursor(wx.CURSOR_ARROW)
            self.SetCursor(myCursor)
        elif mouse == 1:
            myCursor = wx.Cursor(wx.CURSOR_WAIT)
            self.SetCursor(myCursor)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnAbout(self, event):
        """Display an About Dialog"""
        self.SetStatusText("")
        wx.MessageBox("Abre el editor de archivos con doble clic en 'Archivo'.\n"
                      "Para añadir Procesos a los archivos de clic sobre 'Archivo'.\n"
                      "Dentro del Editor de archivos puedes abrir el Editor de Ventanas.",
                      "Como usar el Programa.",
                      wx.OK | wx.ICON_INFORMATION)

    def OnSave(self, event):
        """Save  project session"""
        dlg = wx.FileDialog(self, "Guardar como", self.currentDirectory, "", wildcard, \
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.setStatus("Guardando...", 1)
            self.project.setTree(self.moduleManager.GetTree())
            # Saving the new name for the project
            name = str(path).split("\\")
            name = name[len(name) - 1].split(".")[0]
            self.project.name = name
            f = gzip.open(path, 'wb')
            _pickle.dump(len(self.project.EEGS), f, protocol=4)
            for i in range(len(self.project.EEGS)):
                _pickle.dump(self.project.EEGS[i], f, protocol=4)
            self.project.EEGS = []
            t = self.moduleManager.GetTree()
            _pickle.dump(t, f, protocol=4)
            self.project.moduleTree = []
            _pickle.dump(self.project, f, protocol=4)
            f.close()
            self.setStatus("", 0)
            self.setAux(self.project)
            return True
        elif result == wx.ID_CANCEL:
            self.setAux(self.project)
            return False

    def OnLoad(self, event):
        """Load project session"""
        dlg = wx.FileDialog(
            self, message="Cargar",
            defaultDir=self.currentDirectory,
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_MULTIPLE
        )
        if dlg.ShowModal() == wx.ID_OK:
            if len(self.project.EEGS) > 0:
                opc = 0
                with WindowSaveOnExit(self, opc) as dl:
                    dl.ShowModal()
                    if dl.opc == 1:
                        self.OnSave(0)
                    elif dl.opc == 3:
                        return
            else:
                self.setStatus("Cargando...", 1)
                path = dlg.GetPath()
                f = gzip.open(path, 'rb')
                lent = _pickle.load(f)
                EEGS = []
                for i in range(lent):
                    EEGS.append(_pickle.load(f))
                self.project = _pickle.load(f)
                self.project.EEGS = EEGS
                f.close()
                self.setAux(self.project)
            self.setStatus("Cargando...", 1)
            path = dlg.GetPath()
            f = gzip.open(path, 'rb')
            EEg = _pickle.load(f)
            EEG2 = _pickle.load(f)
            f.close()
        # close all open windows
        self.moduleManager.closeWindows()
        #self.setAux(self.project)
        dlg.Destroy()
        self.setStatus("", 0)
