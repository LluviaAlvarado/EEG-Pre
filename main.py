#Imports
import wx.lib.agw.aquabutton as AB
#local imports
from FileReader import *
from WindowEditor import *

class MainWindow(wx.Frame):
    """
    mainWindow for EEG processing
    """


    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainWindow, self).__init__(*args, **kw)
        self.SetSize(800, 600)
        self.Centre()
        # create base panel in the frame
        self.pnl = wx.Panel(self,
                   style=wx.TAB_TRAVERSAL|wx.VSCROLL|wx.HSCROLL|wx.BORDER_SUNKEN)
        #vbox to place buttons
        self.buttonContainer = wx.BoxSizer(wx.VERTICAL)
        btnCTitle = wx.StaticText(self.pnl, label="EEG Files Loaded:",
                                  style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.buttonContainer.Add(btnCTitle, 0, wx.EXPAND | wx.ALIGN_CENTER)
        self.pnl.SetSizer(self.buttonContainer)
        # and put some text with a larger bold font on it
        #fileLabel = wx.Label
        self.filePicker = wx.FileDialog(self.pnl, message="Choose the EEG files",
           defaultDir="D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
           wildcard="EEG files (*.edf)|*.edf|(*.gdf)|*.gdf|(*.acq)|*.acq", style= wx.FD_OPEN | wx.FD_MULTIPLE)

        # create the menu bar that we don't need yet
        self.makeMenuBar()

        #create the status bar
        self.CreateStatusBar()
        self.SetStatusText("Waiting for EEG file...")



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
        loadFileItem = fileMenu.Append(-1, "&Load EEG...\tCtrl-L",
                "Select EEG file to load.")
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
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")


        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnLoad, loadFileItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnLoad(self, event):
        """Load other files"""
        self.filePicker.ShowModal()
        files = self.filePicker.GetPaths()
        self.loadFiles(files)

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Load files in File->Load File or with Ctrl-L",
                      "How to use EEG Processing application.",
                      wx.OK|wx.ICON_INFORMATION)

    def loadFiles(self, filePaths):
        reader = FileReader()
        for path in filePaths:
            eeg = reader.readFile(path)
            name = str(path).split("\\")
            name = name[len(name)-1].split(".")[0]
            if not reader.hasError():
                print("File Read Successfully!")
                #adding a button for this file just because
                btn = AB.AquaButton(self.pnl, label=name)
                btn.SetForegroundColour("black")
                btn.SetPulseOnFocus(True)
                self.Bind(wx.EVT_BUTTON, lambda event: self.openWindowEditor(event, eeg), btn)
                self.buttonContainer.Add(btn, 0, wx.CENTER|wx.ALL, 5)
                self.buttonContainer.RecalcSizes()

    def openWindowEditor(self, event, eeg):
        windowEditor = WindowEditor(eeg)
        windowEditor.Show()



if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = MainWindow(None, title='EEG Processing')
    frm.Show()
    app.MainLoop()
