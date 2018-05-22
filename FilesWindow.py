#local imports
from FileReader import *
from WindowEditor import *


class FilesWindow(wx.Frame):
    """
    window that contains the list of EEG files and let's you
    open the window editor
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Editor de EEGs", )
        self.SetSize(500, 500)
        self.Centre()
        #global length of windows
        self.WindowLength = None
        #list of EEGs
        self.EEGS = []
        # create base panel in the frame
        self.pnl = wx.Panel(self,
                   style=wx.TAB_TRAVERSAL|wx.VSCROLL|wx.HSCROLL|wx.BORDER_SUNKEN)
        #base vbox
        self.baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        #list fo loaded files
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Archivos EEG cargados:")
        self.filesList = wx.ListBox(self.pnl, choices=[], style=wx.LB_SINGLE)
        self.filesList.Bind(wx.EVT_LISTBOX_DCLICK, self.openWindowEditor)
        self.leftSizer.Add(infoLabel, 0, wx.CENTER, 5)
        self.leftSizer.Add(self.filesList, 1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.leftSizer, -1, wx.EXPAND | wx.ALL, 5)
        #vbox for buttons
        self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
        addButton = wx.Button(self.pnl, label="Agregar")
        addButton.Bind(wx.EVT_BUTTON, self.loadFiles)
        removeButton = wx.Button(self.pnl, label="Eliminar")
        removeButton.Bind(wx.EVT_BUTTON, self.removeFile)
        self.buttonSizer.Add(addButton, 0, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(removeButton, 0, wx.EXPAND | wx.ALL, 5)
        helpLabel = wx.StaticText(self.pnl, label="De doble clic sobre un archivo\npara abrir el 'Editor de Ventanas'.")
        self.buttonSizer.AddSpacer(100)
        self.buttonSizer.Add(helpLabel, 0, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        #todo cambiar la direccion default
        self.filePicker = wx.FileDialog(self.pnl, message="Elige los archivos de EEG",
           defaultDir="D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
           wildcard="Todos (*.*)|*.*|(*.edf)|*.edf|(*.gdf)|*.gdf|(*.acq)|*.acq", style=wx.FD_OPEN | wx.FD_MULTIPLE)


    def loadFiles(self, event):
        self.filePicker.ShowModal()
        #send the files to load eegs and update list
        self.updateList(self.filePicker.Paths)

    def updateList(self, filePaths):
        reader = FileReader()
        files = []
        for path in filePaths:
            eeg = reader.readFile(path)
            name = str(path).split("\\")
            name = name[len(name) - 1].split(".")[0]
            if not reader.hasError():
                print("File Read Successfully!")
                # adding eeg to list
                self.EEGS.append(eeg)
                #adding name to files
                files.append(name)
        #update listbox
        self.filesList.InsertItems(files, self.filesList.GetCount())

    def removeFile(self, event):
        index = self.filesList.GetSelection()
        #remove from the egg list
        self.EEGS.remove(self.EEGS[index])
        #update listbox
        self.filesList.Delete(index)

    def openWindowEditor(self, event):
        index = event.GetEventObject().Selection
        eeg = self.EEGS[index]
        windowEditor = WindowEditor(eeg, self)
        windowEditor.Show()

