# local imports
from FilesWindow import *
from BPFWindow import *
from WindowDialog import *
from ComponentViewer import *
from FastICA import *
import numpy as np
import scipy.signal as signal
from artifactCorrelation import *


class CorrelationWindow(wx.Frame):
    """
        window that contains the artifact elimination configuration and
        opens a visualisation window
        """

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Cálculo de Correlación de un EEG con Artefactos")
        self.SetSize(250, 250)
        self.Centre()
        self.viewer = None
        self.BPFwindow = None
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Opciónes:")
        self.baseSizer.Add(infoLabel, -1, wx.EXPAND | wx.ALL, 5)
        # vbox for buttons
        manualButton = wx.Button(self.pnl, label="Contaminar EEG")
        autoButton = wx.Button(self.pnl, label="Correlacionar")
        manualButton.Bind(wx.EVT_BUTTON, self.contaminate)
        autoButton.Bind(wx.EVT_BUTTON, self.correlate)
        self.viewButton = wx.Button(self.pnl, label="Visualizar")
        self.viewButton.Bind(wx.EVT_BUTTON, self.openView)
        self.exportButton = wx.Button(self.pnl, label="Exportar")
        self.exportButton.Bind(wx.EVT_BUTTON, self.exportar)
        self.baseSizer.Add(manualButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(autoButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.exportButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        # making ECG template
        # The "Daubechies" wavelet is a rough approximation to a real,
        # single, heart beat ("pqrst") signal
        pqrst = signal.wavelets.daub(10)
        # Add the gap after the pqrst when the heart is resting.
        samples_rest = 10
        zero_array = np.zeros(samples_rest, dtype=float)
        self.pqrst_full = np.concatenate([pqrst, zero_array])

    def onClose(self, event):
        self.GetParent().onCRRClose()
        self.Destroy()

    def exportar(self, event):
        pathPicker = wx.DirDialog(None, "Exportar en:", "D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
                                  wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if pathPicker.ShowModal() != wx.ID_CANCEL:
            writer = FileReaderWriter()
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
            # writing windowFiles
            FileReaderWriter().writeWindowFiles(windows, file, txt, self.GetParent().project.windowLength,
                    self.GetParent().project.windowTBE)
        self.GetParent().setStatus("", 0)

    def contaminate(self, event):
        self.GetParent().setStatus("Contaminando el EEG...", 1)
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 1 - blink, 2 - muscular, 3- cardiac
        if apply:
            for sel in artifactSelected:
                if sel != 1:
                    for eeg in self.GetParent().project.EEGS:
                        contamineteEEG(eeg, sel)
        self.GetParent().setStatus("", 0)

    def correlate(self, event):
        self.icas = []
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 1 - blink, 2 - muscular, 3- cardiac
        if apply:
            # setting cursor to wait to inform user
            self.GetParent().setStatus("Correlacionando...", 1)
            for sel in artifactSelected:
                if sel != 1:
                    for eeg in self.GetParent().Project.EEGS:
                        correlate(eeg, sel)

    def getSelectedA(self):
        artifactSelected = []
        with WindowAutoAE(self, artifactSelected) as dlg:
            dlg.ShowModal()
            artifactSelected = dlg.artifactList.GetCheckedItems()
            use = dlg.applied
        return artifactSelected, use

    def openView(self, event):
        if self.BPFwindow is not None:
            self.BPFwindow.Hide()
        self.BPFwindow = BFPWindow(self)