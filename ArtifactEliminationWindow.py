# local imports
from FilesWindow import *
from BPFWindow import *
from WindowDialog import *
from ComponentViewer import *
from FastICA import *
import numpy as np
from scipy import signal

class ArtifactEliminationWindow(wx.Frame):
    """
        window that contains the artifact elimination configuration and
        opens a visualisation window
        """

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Eliminación de Artefactos", )
        self.SetSize(250, 250)
        self.Centre()
        self.viewer = None
        self.icas = []
        self.BPFwindow = None
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Opciónes:")
        self.baseSizer.Add(infoLabel, -1, wx.EXPAND | wx.ALL, 5)
        # vbox for buttons
        manualButton = wx.Button(self.pnl, label="Manualmente")
        autoButton = wx.Button(self.pnl, label="Automáticamente")
        manualButton.Bind(wx.EVT_BUTTON, self.applyFastICA)
        autoButton.Bind(wx.EVT_BUTTON, self.applyAutomatically)
        self.viewButton = wx.Button(self.pnl, label="Visualizar")
        self.viewButton.Bind(wx.EVT_BUTTON, self.openView)
        self.exportButton = wx.Button(self.pnl, label="Exportar")
        self.exportButton.Bind(wx.EVT_BUTTON, self.exportar)
        self.exportButton.Disable()
        self.baseSizer.Add(manualButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(autoButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.exportButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onARClose()
        self.Destroy()

    def exportar(self, event):
        pathPicker = wx.DirDialog(None, "Exportar en:", "D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
                                  wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if pathPicker.ShowModal() != wx.ID_CANCEL:
            writer = FileReader()
            windows = []
            windowsExist = False
            for eeg in self.GetParent().project.EEGS:
                writer.writeFile(eeg, self.GetParent().project.name, pathPicker.GetPath())
                if len(eeg.windows) > 0:
                    windowsExist = True
                windows.append([eeg.name, eeg.windows])
            # exporting csv with window information and a txt with the TBE and length in ms
            if windowsExist:
                self.writeWindowFiles(windows, pathPicker.GetPath())

    def writeWindowFiles(self, windows, path):
        # setting cursor to wait to inform user
        self.GetParent().setStatus("Exportando...", 1)
        file = path + "\\" + self.GetParent().project.name + "_windows.csv"
        txt = path + "\\" + self.GetParent().project.name + "_windows.txt"
        if os.path.isfile(file):
            # it already exists
            f = self.GetParent().project.name + "_windows.csv"
            msg = wx.MessageDialog(None, "El archivo '" + f + "' ya existe. "
                                                              "\n¿Desea reemplazar el archivo?", caption="¡Alerta!",
                                   style=wx.YES_NO | wx.CENTRE)
            if msg.ShowModal() == wx.ID_NO:
                return  # we don't to anything
            else:
                # deleting the prev file and txt
                os.remove(file)
                os.remove(txt)
        with open(file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
            matrix = []
            for row in windows:
                s = [row[0]]
                for w in row[1]:
                    s.append(w.stimulus)
                matrix.append(s)
            writer.writerows(matrix)
        # writing the txt
        with open(txt, 'w', newline='') as txtfile:
            txtfile.write("Longitud: " + str(self.GetParent().project.windowLength) +
                          " TAE: " + str(self.GetParent().project.windowTBE))
        self.GetParent().setStatus("", 0)

    def applyFastICA(self, event):
        self.GetParent().setStatus("Eliminando Artefactos...", 1)
        eegs = self.GetParent().project.EEGS
        matrix = []
        self.icas = []
        for eeg in eegs:
            for channel in eeg.channels:
                matrix.append(channel.readings)
            for extra in eeg.additionalData:
                matrix.append(extra.readings)
            # fast ICA uses transposed matrix
            fastICA = FastICA(np.matrix.transpose(np.array(matrix)), eeg.duration, False)
            self.icas.append(fastICA)

        self.viewButton.Enable()
        self.exportButton.Enable()
        # refresh file window if it is opened
        if self.GetParent().filesWindow is not None:
            self.GetParent().filesWindow.Destroy()
            self.GetParent().filesWindow = FilesWindow(self.GetParent())
            self.GetParent().filesWindow.Show()
        self.openCompView(event)
        self.GetParent().setStatus("", 0)

    def applyAutomatically(self, event):
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 1 - blink, 2 - muscular, 3- cardiac
        if apply:
            # TODO aqui el metodo automático, artifactSelected = (0,1,2) tiene el listado de los artefactos
            pass

    def getSelectedA(self):
        artifactSelected = []
        with WindowAutoAE(self, artifactSelected) as dlg:
            dlg.ShowModal()
            artifactSelected = dlg.artifactList.GetCheckedItems()
            use = dlg.applied
        return artifactSelected, use

    def openCompView(self, event):
        if self.viewer is not None:
            self.viewer.Hide()
        self.viewer = ComponentViewer(self, self.icas)

    def openView(self, event):
        if self.BPFwindow is not None:
            self.BPFwindow.Hide()
        self.BPFwindow = BFPWindow(self)
