# local imports
from BPFWindow import *
from WindowDialog import EEGSelection, WindowAutoAE
from ComponentViewer import *
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
        self.eegs = self.GetParent().project.EEGS
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

    def contaminate(self, event):
        self.GetParent().setStatus("Contaminando el EEG...", 1)
        # saving the current state of EEGs
        for eeg in self.GetParent().project.EEGS:
            eeg.SaveState()
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 2 - muscular, 3- cardiac
        if apply:
            cont = []
            for sel in artifactSelected:
                if sel != 1:
                    for eeg in self.GetParent().project.EEGS:
                        cont.append(contaminateEEG(eeg, sel))
            self.GetParent().project.EEGS.extend(cont)
            self.eegs = self.GetParent().project.EEGS
            self.GetParent().moduleManager.modules.root.updateEEGS(self.eegs)
            self.GetParent().moduleManager.ForwardChanges(self.GetParent().moduleManager.modules.root)
        self.GetParent().setStatus("", 0)

    def getSelectedA(self):
        artifactSelected = []
        with WindowAutoAE(self, artifactSelected) as dlg:
            dlg.ShowModal()
            artifactSelected = dlg.artifactList.GetCheckedItems()
            use = dlg.applied
        return artifactSelected, use

    def correlate(self, event):
        self.icas = []
        eegsi, apply = self.getSelectedEEGS()
        eeg1 = self.GetParent().project.EEGS[eegsi[0]]
        eeg2 = self.GetParent().project.EEGS[eegsi[1]]
        # 0 - Eye movement, 2 - muscular, 3- cardiac
        if apply:
            # setting cursor to wait to inform user
            self.GetParent().setStatus("Correlacionando...", 1)
            correlations = (correlate(eeg1, eeg2))
            # abrir dialogo con correlación
            CorrelationFrame(eeg1, eeg2, correlations, self, title='Resultados de Correlación').Show()
            self.GetParent().setStatus("", 0)

    def getSelectedEEGS(self):
        eegs = []
        names = []
        for eeg in self.GetParent().project.EEGS:
            names.append(eeg.name)
        with EEGSelection(self, names) as dlg:
            dlg.ShowModal()
            eegs.append(dlg.eeg1.GetSelection())
            eegs.append(dlg.eeg2.GetSelection())
            use = dlg.applied
        return eegs, use

    def openView(self, event):
        if self.BPFwindow is not None:
            self.BPFwindow.Hide()
        self.BPFwindow = BFPWindow(self)

class CorrelationFrame(wx.Frame):

    def __init__(self, eeg1, eeg2, corr, *args, **kw):
        super(CorrelationFrame, self).__init__(*args, **kw)
        self.SetMinSize((300, 150))
        self.SetTitle("Coeficiente de correlación:")
        # tabla que muestra los tiempos finales de cada proceso
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.table = wx.ListCtrl(self, size=self.GetSize(), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.table.InsertColumn(0, eeg1.name)
        self.table.InsertColumn(1, eeg2.name)
        self.table.Append([str(corr[0]), str(corr[1])])
        sizer.Add(self.table, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer)
