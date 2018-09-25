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
        self.baseSizer.Add(manualButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(autoButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onCRRClose()
        self.Destroy()

    def contaminate(self, event):
        self.GetParent().setStatus("Contaminando el EEG...", 1)
        # saving the current state of EEGs
        for eeg in self.GetParent().project.EEGS:
            eeg.SaveState()
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 1 - blink, 2 - muscular, 3- cardiac
        if apply:
            cont = []
            for sel in artifactSelected:
                if sel != 1:
                    for eeg in self.GetParent().project.EEGS:
                        cont.append(contaminateEEG(eeg, sel))
            self.GetParent().project.EEGS.extend(cont)
        self.GetParent().setStatus("", 0)

    def correlate(self, event):
        self.icas = []
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 2 - muscular, 3- cardiac
        if apply:
            correlations = []
            # setting cursor to wait to inform user
            self.GetParent().setStatus("Correlacionando...", 1)
            for sel in artifactSelected:
                cr = []
                if sel != 1:
                    for eeg in self.GetParent().project.EEGS:
                        cr.append(correlate(eeg, sel))
                    correlations.append([sel, cr])
            # abrir dialogo con correlación
            CorrelationFrame(self.GetParent().project.EEGS, correlations, self, title='Resultados de Correlación').Show()
            self.GetParent().setStatus("", 0)

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



class CorrelationFrame(wx.Frame):

    def __init__(self, eeg, corr, *args, **kw):
        super(CorrelationFrame, self).__init__(*args, **kw)
        self.SetMinSize((600, 600))
        # tabla que muestra los tiempos finales de cada proceso
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.table = wx.ListCtrl(self, size=self.GetSize(), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.table.InsertColumn(0, "EEG")
        for i in range(len(corr)):
            if corr[0] == 0:
                sel = 'EOG'
            elif corr[0] == 1:
                sel = 'EMG'
            else:
                sel = 'ECG'
            self.table.InsertColumn(i+1, "Correlation with " + sel)
        self.FillTable(eeg, corr)
        sizer.Add(self.table, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)

    def FillTable(self, eegs, corr):
        for i in range(len(eegs)):
            if len(corr) == 1:
                self.table.Append([str(eegs[i].name), str(corr[0][1][i])])
            elif len(corr) == 2:
                self.table.Append([str(eegs[i].name), str(corr[0][1][i]), str(corr[1][1][i])])
            else:
                self.table.Append([str(eegs[i].name), str(corr[0][1][i]), str(corr[1][1][i]), str(corr[2][1][i])])
