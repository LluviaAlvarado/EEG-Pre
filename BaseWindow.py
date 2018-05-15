import wx

from CircleManager import *


class BaseWindow(wx.Frame):

    def __init__(self, *args, **kw):
        super(BaseWindow, self).__init__(*args, **kw)
        self.Maximize(True)
        width, height = self.GetSize()
        print("width " + str(width))
        print("height " + str(height))
        self.workArea = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.VSCROLL | wx.HSCROLL | wx.BORDER_SUNKEN)
        self.circleMngr = CircleManager(self.workArea, width, height, self)
        #making it decent
        # create the menu bar that we don't need yet
        self.makeMenuBar()
        # create the status bar
        self.CreateStatusBar()
        self.SetStatusText("Esperando por archivo de EEG...")

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
        menuBar.Append(fileMenu, "&Archivo")
        menuBar.Append(helpMenu, "&Ayuda")


        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

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