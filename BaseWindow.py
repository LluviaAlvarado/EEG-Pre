import os
import wx
import _pickle

# Local Imports
from CircleManager import *
from Project import *
# from BandpassFilter import *
from pathlib import Path

wildcard = "EEG Pre Processing Project (*.eppp)|*.eppp"


class BaseWindow(wx.Frame):

    def __init__(self, *args, **kw):
        super(BaseWindow, self).__init__(*args, **kw)
        self.Maximize(True)
        width, height = self.GetSize()
        self.currentDirectory = os.getcwd()
        self.workArea = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN)
        self.circleMngr = CircleManager(self.workArea, width, height, self)
        self.project = Project()
        # to just open 1 files window
        self.filesWindow = None
        # create the menu bar that we don't need yet
        self.makeMenuBar()
        # create the status bar
        self.CreateStatusBar()
        self.SetStatusText("")

    def onFWClose(self):
        # so we can create another
        self.filesWindow = None

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
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)
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
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

        # self.Bind(wx.EVT_MENU, self.OnTest, testItem)

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
                      wx.OK|wx.ICON_INFORMATION)

    def OnSave(self, event):
        """Save  project session"""
        dlg = wx.FileDialog(self, "Guardar como", self.currentDirectory, "", wildcard, \
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        result = dlg.ShowModal()
        path = dlg.GetPath()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.setStatus("Guardando...", 1)
            # Saving the new name for the project
            name = str(path).split("\\")
            name = name[len(name) - 1].split(".")[0]
            self.project.name = name
            with open(path, 'wb') as output:
                _pickle.dump(self.project, output, protocol=4)
            self.setStatus("", 0)
            return True
        elif result == wx.ID_CANCEL:
            return False

    def OnLoad(self, event):
        """Load project session"""
        dlg = wx.FileDialog(
            self, message="Cargar",
            defaultDir=self.currentDirectory,
            defaultFile="", wildcard=wildcard, style=wx.FD_OPEN
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.setStatus("Cargando...", 1)
            path = dlg.GetPath()
            with open(path, 'rb') as input:
                self.project = _pickle.load(input)
        # update the file window if opened
        if self.filesWindow is not None:
            self.filesWindow.Destroy()
            self.filesWindow = FilesWindow(self)
            self.filesWindow.Show()
        dlg.Destroy()
        self.setStatus("", 0)


