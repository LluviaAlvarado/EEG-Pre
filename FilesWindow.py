# Imports
import wx.lib.dialogs as DL
import csv

# local imports
from FileReader import *
from WindowEditor import *
from WindowDialog import *


class FilesWindow(wx.Frame):
    """
    window that contains the list of EEG files and let's you
    open the window editor
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Editor de EEGs", )
        self.SetSize(500, 500)
        self.Centre()
        # window editor instance so only 1 is opened
        self.windowEditor = None
        # create base panel in the frame
        self.pnl = wx.Panel(self,
                   style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        # list for loaded files
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Archivos EEG cargados:")
        self.filesList = wx.ListBox(self.pnl, choices=[], style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
        # filling with files already in project
        for eeg in self.GetParent().project.EEGS:
            self.filesList.Append(eeg.name)
        self.filesList.Bind(wx.EVT_LISTBOX_DCLICK, self.openWindowEditor)
        self.leftSizer.Add(infoLabel, 0, wx.CENTER, 5)
        self.leftSizer.Add(self.filesList, 1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.leftSizer, -1, wx.EXPAND | wx.ALL, 5)
        # vbox for buttons
        self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
        addButton = wx.Button(self.pnl, label="Agregar")
        addButton.Bind(wx.EVT_BUTTON, self.loadFiles)
        removeButton = wx.Button(self.pnl, label="Eliminar")
        windowInfo = wx.StaticText(self.pnl, label="Matriz de Tiempos para Ventanas:")
        self.windowCSV = wx.StaticText(self.pnl, label="No se ha cargado un archivo .csv")
        self.windowButton = wx.Button(self.pnl, label="Cargar")
        self.windowButton.Bind(wx.EVT_BUTTON, self.loadCSVFile)
        if len(self.GetParent().project.EEGS) == 0:
            self.windowButton.Disable()
        if self.GetParent().project.windowCSV is not None:
            name = str(self.GetParent().project.windowCSV[1]).split("\\")
            name = name[len(name) - 1].split(".")[0]
            self.windowCSV.SetLabel(name)
        removeButton.Bind(wx.EVT_BUTTON, self.removeFile)
        self.buttonSizer.Add(addButton, 0, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(removeButton, 0, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.AddSpacer(10)
        self.buttonSizer.Add(windowInfo, 0, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(self.windowCSV, 0, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(self.windowButton, 0, wx.EXPAND | wx.ALL, 5)
        helpLabel = wx.StaticText(self.pnl, label="De doble clic sobre un archivo\npara abrir el 'Editor de Ventanas'.")
        self.buttonSizer.AddSpacer(100)
        self.buttonSizer.Add(helpLabel, 0, wx.EXPAND | wx.ALL, 5)
        # button to save modified eegs
        self.saveButton = wx.Button(self.pnl, label="Exportar")
        self.saveButton.Bind(wx.EVT_BUTTON, self.exportar)
        if len(self.GetParent().project.EEGS) == 0:
            self.saveButton.Disable()
        self.buttonSizer.AddSpacer(50)
        self.buttonSizer.Add(self.saveButton, 0, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        # todo cambiar la direccion default
        self.filePicker = wx.FileDialog(self.pnl, message="Elige los archivos de EEG",
           defaultDir="D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
           wildcard="Todos (*.*)|*.*|(*.edf)|*.edf|(*.gdf)|*.gdf|(*.acq)|*.acq", style=wx.FD_OPEN | wx.FD_MULTIPLE)

    def exportar(self, event):
        pathPicker = wx.DirDialog(None, "Exportar en:", "D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if pathPicker.ShowModal() != wx.ID_CANCEL:
            writer = FileReader()
            for eeg in self.GetParent().project.EEGS:
                writer.writeFile(eeg, self.GetParent().project.name, pathPicker.GetPath())

    def onClose(self, event):
        self.GetParent().onFWClose()
        self.Destroy()

    def loadFiles(self, event):
        if self.filePicker.ShowModal() == wx.ID_CANCEL:
            return  # the user changed their mind
        # send the files to load eegs and update list
        self.updateList(self.filePicker.Paths)

    def repeatedEeg(self, name):
        for file in self.filesList.GetItems():
            if name == file:
                return True
        return False

    def loadCSVFile(self, event):
        # check if there's a file already loaded
        if self.windowCSV.GetLabel() != "No se ha cargado un archivo .csv":
            alerta = wx.MessageDialog(self, "Al cargar un nuevo archivo se eliminarán todas "
                                            "las ventanas actuales.\n¿Desea continuar?", caption="¡Alerta!",
                          style=wx.YES_NO)
            if alerta.ShowModal() == wx.ID_NO:
                # do nothing
                return
            else:
                # let's delete the windows
                for eeg in self.GetParent().project.EEGS:
                    eeg.windows = []
        picker = wx.FileDialog(self.pnl, message="Elige el archivo de Tiempos",
                                  defaultDir="D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
                                  wildcard="CSV (*.csv)|*.csv",
                                  style=wx.FD_OPEN)
        if picker.ShowModal() == wx.ID_CANCEL:
            return  # the user changed their mind
        # fill the windows with the file
        self.loadWindows(picker.Path)

    def readCSV(self, path):
        matrix = []
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                matrix.append(row)
            if (len(matrix) != len(self.GetParent().project.EEGS)):
                # this csv does not match with the loaded files
                return []
        return matrix

    def getCorrectWindowInfo(self, name, csv):
        for row in csv:
            if row[0] == name:
                # we remove the name of file
                return row[1:]
        return None

    def loadWindows(self, path):
        # setting cursor to wait to inform user
        myCursor = wx.Cursor(wx.CURSOR_WAIT)
        self.SetCursor(myCursor)
        self.GetParent().SetStatusText("Cargando Ventanas...")
        # let's read and verify the csv
        name = str(path).split("\\")
        name = name[len(name) - 1].split(".")[0]
        csv = self.readCSV(path)
        if len(csv) != 0:
            # let's ask for the length and tbe of the windows
            l, tbe = self.getWindowData()
            self.GetParent().project.windowLength = l
            self.GetParent().project.windowTBE = tbe
            self.GetParent().project.windowCSV = [csv, path]
            for eeg in self.GetParent().project.EEGS:
                windows = self.getCorrectWindowInfo(eeg.name, csv)
                if windows is not None:
                    eeg.addMultipleWindows(windows, l, tbe)
                else:
                    self.showErrorFiles([[name, 5]])
                    break
            self.windowCSV.SetLabel(name)
        else:
            self.showErrorFiles([[name, 5]])
        # returning normal cursor
        myCursor = wx.Cursor(wx.CURSOR_ARROW)
        self.SetCursor(myCursor)
        self.GetParent().SetStatusText("")

    def getWindowData(self):
        # giving a default value in ms to avoid user errors
        l = 50
        tbe = 10
        with WindowDialog(self, l, tbe) as dlg:
            dlg.ShowModal()
            # handle dialog being cancelled or ended by some other button
            if dlg.length.GetValue() != "":
                try:
                    l = int(dlg.length.GetValue())
                except:
                    # it was not an integer
                    dlg.length.SetValue(str(l))
            if dlg.tbe.GetValue() != "":
                try:
                    tbe = int(dlg.tbe.GetValue())
                except:
                    # it was not an integer
                    dlg.tbe.SetValue(str(tbe))
        return l, tbe

    def updateList(self, filePaths):
        # setting cursor to wait to inform user
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
                    # show error with file
                    errorFiles.append([name, 0])
            else:
                # show error with repeated file
                errorFiles.append([name, 1])
        # check if eegs of same project
        if len(self.GetParent().project.EEGS) != 0:
            self.checkProjectEEGs(errorFiles)
        # update listbox
        if len(self.GetParent().project.EEGS) > currentAmount:
            while currentAmount < len(self.GetParent().project.EEGS):
                self.filesList.Append(self.GetParent().project.EEGS[currentAmount].name)
                if self.windowEditor is not None:
                    # add the new tab
                    self.windowEditor.addTab(self.GetParent().project.EEGS[currentAmount])
                currentAmount += 1
        # showing errors that ocurred
        self.showErrorFiles(errorFiles)
        # returning normal cursor
        myCursor = wx.Cursor(wx.CURSOR_ARROW)
        self.SetCursor(myCursor)
        if len(self.GetParent().project.EEGS) < 1:
            self.GetParent().SetStatusText("Esperando por Archivos de EEG...")
        else:
            self.windowButton.Enable()
            self.saveButton.Enable()
            self.GetParent().SetStatusText("")

    def checkProjectEEGs(self, errorFiles):
        EEGS = self.GetParent().project.EEGS
        if self.GetParent().project.frequency is None:
            # getting the global data of the project
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
            # check which eeg got more matches
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
        # check if files match with the project
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
            elif error[1] == 4:
                message += "no contiene los mismos canales del Proyecto.\n"
            else:
                message += "no concuerda con los EEG cargados.\n"
                self.windowCSV.SetLabel("No se ha cargado un archivo .csv")
        if message != "":
            DL.alertDialog(parent=None, message=message, title='Se encontraron los siguientes Errores:')

    def removeFile(self, event):
        index = self.filesList.GetSelection()
        # remove from the egg list
        self.GetParent().project.EEGS.remove(self.GetParent().project.EEGS[index])
        # update listbox
        self.filesList.Delete(index)
        # if no more files left
        if len(self.GetParent().project.EEGS) == 0:
            self.GetParent().project.reset()
            self.windowButton.Disable()
            self.saveButton.Disable()
            self.windowCSV.SetLabel("No se ha cargado un archivo .csv")

    def openWindowEditor(self, event):
        index = event.GetEventObject().Selection
        eeg = self.GetParent().project.EEGS[index]
        if self.windowEditor is None:
            self.windowEditor = WindowEditor(self)
        self.windowEditor.setEEG(eeg)

    def onWEClose(self):
        # so we can create another
        self.windowEditor = None