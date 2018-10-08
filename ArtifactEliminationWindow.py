# local imports
from FilesWindow import *
from BPFWindow import *
from WindowDialog import *
from ComponentViewer import *
from FastICA import *
import threading
from wx.adv import NotificationMessage
from ArtifactElimination import *
from Utils import exportEEGS, eeg_copy


class ArtifactEliminationWindow(wx.Frame):
    """
        window that contains the artifact elimination configuration and
        opens a visualisation window
        """

    def __init__(self, parent, eegs, p):

        wx.Frame.__init__(self, parent, -1, "Eliminación de Artefactos con FastICA")
        self.SetSize(250, 250)
        self.Centre()
        self.pbutton = p
        self.eegs = eegs
        self.viewer = None
        self.icas = []
        self.BPFwindow = None
        self.loading = None
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
        self.exportButton.Bind(wx.EVT_BUTTON, self.export)
        self.baseSizer.Add(manualButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(autoButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.exportButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.pbutton.onCloseModule()
        self.Destroy()

    def ReDo(self, actions, eegs):
        self.eegs = eegs
        # this redo's the automatic elimination after forward
        if len(actions) > 0 and len(self.eegs) > 0:
            # setting cursor to wait to inform user
            self.GetParent().setStatus("Buscando Artefactos...", 1)
            self.loading = WorkingAnimation(self.GetParent(), 'search')
            self.loading.Play()
            # saving the current state of EEGs
            for eeg in self.eegs:
                eeg.SaveState()
            threading.Thread(target=self.apply, args=[actions]).start()


    def export(self, event):
        # setting cursor to wait to inform user
        self.GetParent().setStatus("Exportando...", 1)
        exportEEGS(self.GetParent().project, self.eegs)
        self.GetParent().setStatus("", 0)

    def applyFastICA(self, event):
        self.GetParent().setStatus("Buscando Componentes...", 1)
        # saving the current state of EEGs
        if len(self.eegs) > 0:
            tmp = deepcopy(self.eegs[0])
        for eeg in self.eegs:
            save = eeg_copy(eeg, tmp)
            eeg.setSaveState(save)
        self.FastICA()
        self.viewButton.Enable()
        self.exportButton.Enable()
        self.openCompView(event)
        self.GetParent().setStatus("", 0)

    def apply(self, artifactSelected):
        if 0 in artifactSelected:
            self.removeEOG()
        if 1 in artifactSelected:
            self.removeBlink()
        if 2 in artifactSelected:
            self.removeMuscular()
        if 3 in artifactSelected:
            self.removeECG()
        self.EliminateComponents()
        wx.CallAfter(self.loading.Stop)

    def applyAutomatically(self, event):
        self.icas = []
        artifactSelected, apply = self.getSelectedA()
        # 0 - Eye movement, 1 - blink, 2 - muscular, 3- cardiac
        if apply:
            # setting cursor to wait to inform user
            self.GetParent().setStatus("Buscando Artefactos...", 1)
            self.loading = WorkingAnimation(self, 'search')
            self.loading.Play()
            # saving the current state of EEGs
            for eeg in self.eegs:
                eeg.SaveState()
            self.pbutton.actions = artifactSelected
            threading.Thread(target=self.apply, args=[artifactSelected]).start()

    def removeEOG(self):
        # first we apply FastICA to get IC
        if len(self.icas) == 0:
            self.FastICA()
        autoRemoveEOG(self.icas)

    def removeECG(self):
        # first we apply FastICA to get IC
        if len(self.icas) == 0:
            self.FastICA()
        autoRemoveECG(self.icas, self.GetParent().project.frequency, self.GetParent().project.duration)

    def FastICA(self):
        # to remove eye blink and muscular artifacts we
        # will use fastICA then wavelets
        eegs = self.eegs
        self.icas = []
        for eeg in eegs:
            matrix = []
            for channel in eeg.channels:
                matrix.append(channel.readings)
            for extra in eeg.additionalData:
                matrix.append(extra.readings)
            # fast ICA uses transposed matrix
            fastICA = FastICA(np.matrix.transpose(np.array(matrix)), eeg.duration, False)
            self.icas.append(fastICA)
        processes = [threading.Thread(target=ica.separateComponents) for ica in self.icas]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

    def removeBlink(self):
        if len(self.icas) == 0:
            self.FastICA()
        autoRemoveBlink(self.icas, self.GetParent().project.frequency, self.GetParent().project.duration)

    def removeMuscular(self):
        if len(self.icas) == 0:
            self.FastICA()
        autoRemoveMuscular(self.icas)

    def EliminateComponents(self):
        self.GetParent().setStatus("Eliminando Artefactos...", 1)
        eegs = self.eegs
        self.pbutton.eegs = eegs
        eliminateArtifacts(eegs, self.icas)
        self.GetParent().ForwardChanges(self.pbutton)
        self.GetParent().setStatus("", 0)
        NotificationMessage(title="¡Exito!", message="Se han eliminado los artefactos.").Show()

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
        self.BPFwindow = BFPWindow(self, True)


