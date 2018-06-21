#Imports
import wx.lib.dialogs as DL

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
        # create base panel in the frame
        self.pnl = wx.Panel(self,
                   style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        #base vbox
        self.baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        #list for loaded files
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        #TODO AQUI CARGA LOS NOMBRES DE LOS EEG QUE YA SE HABIAN GUARDADO EN EL PROYECTO PLOX
        infoLabel = wx.StaticText(self.pnl, label="Archivos EEG cargados:")
        self.filesList = wx.ListBox(self.pnl, choices=[], style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
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
        if self.filePicker.ShowModal() == wx.ID_CANCEL:
            return  # the user changed their mind
        #send the files to load eegs and update list
        self.updateList(self.filePicker.Paths)

    def repeatedEeg(self, name):
        for file in self.filesList.GetItems():
            if name == file:
                return True
        return False

    def updateList(self, filePaths):
        #setting cursos to wait to inform user
        myCursor = wx.Cursor(wx.CURSOR_WAIT)
        self.SetCursor(myCursor)
        self.GetParent().SetStatusText("Cargando Archivos...")
        reader = FileReader()
        errorFiles = []
        currentAmount = len(self.GetParent().project.EEGS)
        for path in filePaths:
            name = str(path).split("\\")
            name = name[len(name) - 1].split(".")[0]
            if not self.repeatedEeg(name):
                eeg = reader.readFile(path)
                if not reader.hasError():
                    # adding eeg to list
                    eeg.setName(name)
                    self.GetParent().project.EEGS.append(eeg)
                else:
                    #show error with file
                    errorFiles.append([name, 0])
            else:
                # show error with repeated file
                errorFiles.append([name, 1])
        #check if eegs of same project
        self.checkProjectEEGs(errorFiles)
        #update listbox
        if len(self.GetParent().project.EEGS) > currentAmount:
            while currentAmount < len(self.GetParent().project.EEGS):
                self.filesList.Append(self.GetParent().project.EEGS[currentAmount].name)
                currentAmount += 1
        #showing errors that ocurred
        self.showErrorFiles(errorFiles)
        #returning normal cursor
        myCursor = wx.Cursor(wx.CURSOR_ARROW)
        self.SetCursor(myCursor)
        if len(self.GetParent().project.EEGS) < 1:
            self.GetParent().SetStatusText("Esperando por Archivos de EEG...")
        else:
            self.GetParent().SetStatusText("")

    def checkProjectEEGs(self, errorFiles):
        EEGS = self.GetParent().project.EEGS
        if self.GetParent().project.frequency is None:
            #getting the global data of the project
            matching = []
            for e in EEGS:
                matching.append(0)
            i = 0
            for eeg in EEGS:
                for e in EEGS:
                    diference = e.sameProject(eeg)
                    if diference == "":
                        matching[i] += 1
                i += 1
            #check which eeg got more matches
            winner = [0, 0]
            i = 0
            for match in matching:
                if match > winner[1]:
                    winner = [i, match]
                i += 1
            self.GetParent().project.frequency = EEGS[winner[0]].frequency
            self.GetParent().project.duration = EEGS[winner[0]].duration
            self.GetParent().project.numCh = len(EEGS[winner[0]].channels)
            self.GetParent().project.chLabels = EEGS[winner[0]].getChannelLabels()
        #check if files match with the project
        i = 0
        toRemove = []
        for eeg in EEGS:
            if eeg.frequency != self.GetParent().project.frequency:
                errorFiles.append([eeg.name, 2])
                toRemove.append(i)
            elif eeg.duration != self.GetParent().project.duration:
                errorFiles.append([eeg.name, 3])
                toRemove.append(i)
            elif len(eeg.channels) != self.GetParent().project.numCh:
                errorFiles.append([eeg.name, 4])
                toRemove.append(i)
            elif not eeg.sameLabelsCh(self.GetParent().project.chLabels):
                errorFiles.append([eeg.name, 4])
                toRemove.append(i)
            i += 1
        for index in reversed(toRemove):
            self.GetParent().project.EEGS.remove(self.GetParent().project.EEGS[index])

    def showErrorFiles(self, files):
        message = ""
        for error in files:
            message += "El archivo: " + error[0] + ", "
            if error[1] == 0:
                message += "no es soportado.\n"
            elif error[1] == 1:
                message += "esta repetido.\n"
            elif error[1] == 2:
                message += "no tiene la misma frequencia de muestreo del Proyecto.\n"
            elif error[1] == 3:
                message += "no tiene la misma duración del Proyecto.\n"
            else:
                message += "no contiene los mismos canales del Proyecto.\n"
        if message != "":
            DL.alertDialog(parent=None, message=message, title='Se encontraron los siguientes Errores:')

    def removeFile(self, event):
        index = self.filesList.GetSelection()
        #remove from the egg list
        self.GetParent().project.EEGS.remove(self.GetParent().project.EEGS[index])
        #update listbox
        self.filesList.Delete(index)
        #if no more files left
        if len(self.GetParent().project.EEGS) == 0:
            self.GetParent().project.frequency = None
            self.GetParent().project.duration = None
            self.GetParent().project.numCh = None
            self.GetParent().project.chLabels = []

    def openWindowEditor(self, event):
        index = event.GetEventObject().Selection
        eeg = self.GetParent().project.EEGS[index]
        windowEditor = WindowEditor(eeg, self)
        windowEditor.Show()

