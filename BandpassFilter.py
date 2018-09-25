# Imports
# local imports
from FilesWindow import *
from Channel import *
from BPFWindow import *
from WindowDialog import WindowCustomWave
from Utils import exportEEGS


class frequencyBand:
    def __init__(self, name, lowFrequency, hiFrequency):
        self.name = name
        self.hiFrequency = hiFrequency
        self.lowFrequency = lowFrequency

    def getFormat(self):
        blank = ""
        i = len(self.name)
        while i < 10:
            blank = blank + " "
            i += 1
        s = self.name + blank + " Baja:  " + str(self.lowFrequency) + "Hz    Alta:  " + str(self.hiFrequency) + "Hz"
        return s


class PreBPFW(wx.Frame):
    """
        window that contains the Bandpass Filter configuration and
        open visualisation window
        """

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Pre configuración del filtrado", )
        self.SetSize(500, 500)
        self.Centre()
        self.BPFwindow = None
        self.waves = self.defaultWaves()

        self.customWaves = []
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Listado de Bandas:")
        extraCannels = wx.StaticText(self.pnl, label="Bandas personalizadas:")
        info = wx.StaticText(self.pnl, label="De doble clic sobre una Banda\npara editar las Frecuencias")
        self.waveList = wx.CheckListBox(self.pnl, choices=self.wavestoString(self.waves))
        self.extraList = wx.CheckListBox(self.pnl, choices=self.wavestoString(self.customWaves),
                                         style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
        self.waveList.Bind(wx.EVT_LISTBOX_DCLICK, lambda event: self.onEdit(self.waves, self.waveList))
        self.extraList.Bind(wx.EVT_LISTBOX_DCLICK, lambda event: self.onEdit(self.customWaves, self.extraList))

        self.leftSizer.Add(infoLabel, 0, wx.CENTER, 5)
        self.leftSizer.Add(self.waveList, 1, wx.EXPAND | wx.ALL, 5)
        self.leftSizer.Add(extraCannels, 0, wx.CENTER, 5)
        self.leftSizer.Add(self.extraList, 1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.leftSizer, -1, wx.EXPAND | wx.ALL, 5)
        # vbox for buttons
        self.buttonSizer = wx.BoxSizer(wx.VERTICAL)
        self.buttonSizer.AddSpacer(15)
        self.buttonSizer.Add(info, -1, wx.EXPAND | wx.ALL, 5)
        addButton = wx.Button(self.pnl, label="Agregar")
        addButton.Bind(wx.EVT_BUTTON, self.addCustom)
        delButton = wx.Button(self.pnl, label="Eliminar")
        delButton.Bind(wx.EVT_BUTTON, self.delCustom)

        self.buttonSizer.AddSpacer(180)
        self.buttonSizer.Add(addButton, -1, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(delButton, -1, wx.EXPAND | wx.ALL, 5)

        self.buttonSizer.AddSpacer(30)
        applyButton = wx.Button(self.pnl, label="Aplicar Filtrado")
        applyButton.Bind(wx.EVT_BUTTON, self.applyFilter)
        self.viewButton = wx.Button(self.pnl, label="Visualizar")
        self.viewButton.Bind(wx.EVT_BUTTON, self.openView)
        self.viewButton.Disable()
        self.exportButton = wx.Button(self.pnl, label="Exportar")
        self.exportButton.Bind(wx.EVT_BUTTON, self.export)
        self.exportButton.Disable()
        self.buttonSizer.Add(applyButton, -1, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(self.exportButton, -1, wx.EXPAND | wx.ALL, 5)

        self.baseSizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onBPClose()
        self.Destroy()

    def GetSelected(self):
        bands = []
        for i in self.waveList.GetCheckedItems():
            bands.append(self.waves[i])
        for i in self.extraList.GetCheckedItems():
            bands.append(self.customWaves[i])
        return bands

    def defaultWaves(self):
        w = [frequencyBand("Gamma", 40, 100), frequencyBand("Beta", 12, 40), frequencyBand("Alpha", 8, 12),
             frequencyBand("Theta", 4, 8), frequencyBand("Delta", 0, 4)]
        return w

    def wavestoString(self, w):
        str = []
        for wave in w:
            str.append(wave.getFormat())
        return str

    def addCustom(self, event):
        name, lowF, higF, flag = self.getWaveData()
        if flag:
            w = frequencyBand(name, lowF, higF)
            self.customWaves.append(w)
            self.extraList.Append(w.getFormat())
            self.extraList.Check(self.extraList.GetCount() - 1, True)

    def delCustom(self, event):
        index = self.extraList.GetSelection()
        if self.extraList.GetCount() > 0 and index > -1:
            self.extraList.Delete(index)
            self.customWaves.pop(index)

    def onEdit(self, waves, waveList):
        index = waveList.GetSelection()
        name, lowF, higF, flag = self.getWaveData(waves[index].name, waves[index].lowFrequency,
                                                  waves[index].hiFrequency)
        if flag:
            waves[index].name = name
            waves[index].lowFrequency = lowF
            waves[index].hiFrequency = higF
            waveList.Delete(index)
            waveList.InsertItems([waves[index].getFormat()], index)
            waveList.Check(index, True)

    def getWaveData(self, name="Nuevo", lowF=1, higF=10):
        # giving a default value in ms to avoid user errors
        flag = True
        with WindowCustomWave(self, name, lowF, higF) as dlg:
            dlg.ShowModal()
            if dlg.flag:
                # handle dialog being cancelled or ended by some other button
                if dlg.name.GetValue() != "":
                    name = str(dlg.name.GetValue())
                if dlg.lowF.GetValue() != "":
                    try:
                        lowF = int(dlg.lowF.GetValue())
                    except:
                        # it was not an integer
                        dlg.lowF.SetValue(str(lowF))
                if dlg.higF.GetValue() != "":
                    try:
                        higF = int(dlg.higF.GetValue())
                    except:
                        # it was not an integer
                        dlg.higF.SetValue(str(higF))
            else:
                flag = False
        return name, lowF, higF, flag

    def export(self, event):
        exportEEGS(self.GetParent().project)

    def applyFilter(self, event):
        self.GetParent().setStatus("Filtrando...", 1)
        eegs = self.GetParent().project.EEGS
        flag = False
        new = []
        for eeg in eegs:
            # applying for each band
            timestep = 1 / eeg.frequency
            bands = self.GetSelected()
            if len(bands) > 0:
                flag = True
            for band in bands:
                channels = eeg.channels
                neweeg = deepcopy(eeg)
                neweeg.channels = []
                for ch in channels:
                    fourier = np.fft.rfft(ch.readings, len(ch.readings))
                    for i in range(len(fourier)):
                        if i < band.lowFrequency or i > band.hiFrequency:
                            fourier[i] = 0.0
                    # adding new filtered channel
                    filtered = np.fft.irfft(fourier)
                    fl = Channel(ch.label, filtered)
                    neweeg.channels.append(fl)
                # adding band limits to name
                neweeg.name += "_" + str(band.lowFrequency) + "-" + str(band.hiFrequency)
                new.append(neweeg)
        self.GetParent().project.addMany(new)
        self.GetParent().setStatus("", 0)
        if flag:
            self.viewButton.Enable()
            self.exportButton.Enable()
        # refresh file window if it is opened
        if self.GetParent().filesWindow is not None:
            self.GetParent().filesWindow.Destroy()
            self.GetParent().filesWindow = FilesWindow(self.GetParent())
            self.GetParent().filesWindow.Show()

    def openView(self, event):
        if self.BPFwindow is not None:
            self.BPFwindow.Hide()
        self.BPFwindow = BFPWindow(self)
