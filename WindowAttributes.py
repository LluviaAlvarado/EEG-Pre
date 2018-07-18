# Imports
import numpy as np
import wx.grid

from WindowEditor import *
from WindowDialog import *


class WindowAttributes(wx.Frame):
    """
    window that contains the list of
    """
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Caracterizar")
        self.SetSize(900, 600)
        self.Centre()
        # for FFT
        self.amountHF = 1
        # create base panel in the frame
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        leftPnl = wx.Panel(self, size=(300, 600))
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        opcLabel = wx.StaticText(leftPnl, label="Opciones: ")
        self.choices = ["Transformada rápida de Fourier", "Area bajo la curva", "Voltaje má ximo"]
        checkSizer = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.Bitmap("src/config.png", wx.BITMAP_TYPE_PNG)
        configButton = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp,
                                       size=(bmp.GetWidth(), bmp.GetHeight()))
        configButton.Bind(wx.EVT_BUTTON, self.confFFT)

        self.optionsList = wx.CheckListBox(leftPnl, choices=self.choices)
        applyButton = wx.Button(leftPnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.apply)

        leftSizer.Add(opcLabel, 0, wx.EXPAND | wx.ALL, 5)
        checkSizer.Add(self.optionsList, 0, wx.EXPAND | wx.ALL, 5)
        checkSizer.Add(configButton, 0, wx.ALL, 5)
        leftSizer.Add(checkSizer, 0, wx.EXPAND | wx.ALL, 5)
        leftSizer.Add(applyButton, 0, wx.EXPAND | wx.ALL, 20)
        leftPnl.SetSizer(leftSizer)
        rightPnl = wx.Panel(self, size=(600, 600))
        # EEG tabs
        self.eegTabs = aui.AuiNotebook(rightPnl, size=(rightPnl.Size),
                                              style=aui.AUI_NB_DEFAULT_STYLE ^ (
                                                          aui.AUI_NB_TAB_SPLIT | aui.AUI_NB_TAB_MOVE)
                                                    | aui.AUI_NB_WINDOWLIST_BUTTON)
        # filling the tabs
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.eegTabs, 0, wx.EXPAND | wx.ALL, 1)
        rightPnl.SetSizer(rightSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 3)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(baseContainer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onCHClose()
        self.Destroy()

    def applyFFT(self):
        FFT = []
        eegs = self.GetParent().project.EEGS
        for eeg in eegs:
            for w in eeg.windows:
                ffts = []
                for ch in w.readings:
                    fourier = np.fft.rfft(ch, len(ch))
                    index = int((len(ch)/2) - self.amountHF)
                    group = []
                    for i in range(index, int(len(ch)/2)):
                        group.append(fourier[i])
                    ffts.append(group)
                # getting the average frequency for the selected group per window
                group = []
                for i in range(self.amountHF):
                    aux = []
                    for fft in ffts:
                        aux.append(fft[i])
                    fft = np.average(aux)
                    group.append(fft)
                FFT.append(group)
        # setting MV to the project
        self.GetParent().project.windowFFT = FFT

    def confFFT(self, event):
        dlg = wx.TextEntryDialog(self, 'Numero de salidas: ', 'Configuración FFT')
        dlg.SetValue(str(self.amountHF))
        if dlg.ShowModal() == wx.ID_OK:
            l = dlg.GetValue()
        dlg.Destroy()
        try:
            self.amountHF = int(l)
        except:
            pass

    def applyAUC(self):
        AUC = []
        eegs = self.GetParent().project.EEGS
        for eeg in eegs:
            for w in eeg.windows:
                areas = []
                for ch in w.readings:
                    dx = 1
                    area = np.trapz(ch, dx=dx)
                    areas.append(area)
                # getting the average area per window
                area = np.average(areas)
                AUC.append(area)
    # setting AUC to the project
        self.GetParent().project.windowAUC = AUC

    def applyMV(self):
        MV = []
        eegs = self.GetParent().project.EEGS
        for eeg in eegs:
            for w in eeg.windows:
                mvs = []
                for ch in w.readings:
                    mv = np.amax(ch)
                    mvs.append(mv)
                # getting the average max voltage per window
                mv = np.average(mvs)
                MV.append(mv)
        # setting MV to the project
        self.GetParent().project.windowMaxVolt = MV

    def apply(self, event):
        selected = self.optionsList.GetCheckedItems()
        for opc in selected:
            if opc == 0:
                # Transformada rápida de Fourier
                self.applyFFT()
            elif opc == 1:
                # Area bajo la curva
                self.applyAUC()
            elif opc == 2:
                # Voltaje maximo
                self.applyMV()
        self.fillEEGTabs(selected)

    def fillEEGTabs(self, selected):
        self.eegTabs.DeleteAllPages()
        eegs = self.GetParent().project.EEGS
        num = 0
        for eeg in eegs:
            self.addTab(eeg, selected, num)
            num += 1

    def addTab(self, e, selected, num):
        page = GridTab(self.eegTabs, e, selected, num)
        self.eegTabs.AddPage(page, e.name)


class GridTab(wx.Panel):

    def __init__(self, p, e, selected, num):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=(p.Size))
        self.eeg = e
        project = self.GetParent().GetParent().GetParent().GetParent().project
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        table = wx.grid.Grid(self, size=(600,600))
        table.EnableEditing(False)
        table.CreateGrid(len(self.eeg.windows), len(selected))
        ch = ["Transformada rápida de Fourier", "Area bajo la curva", "Voltaje máximo"]
        windowSize = []
        add = 0
        eegs = project.EEGS
        for eeg in eegs:
            windowSize.append(add)
            add += len(eeg.windows)
        col = 0
        row = 0
        while col < len(selected):
            table.SetColLabelValue(col, ch[selected[col]])
            col += 1
        data = []
        while row < len(self.eeg.windows):
            table.SetRowLabelValue(row, str(row+1))
            col=0
            while col < len(selected):
                if selected[col] == 0:
                    data = project.windowFFT
                if selected[col] == 1:
                    data = project.windowAUC
                if selected[col] == 2:
                    data = project.windowMaxVolt
                table.SetCellValue(row, col, str(data[row + windowSize[num]]))
                col += 1
            row += 1
        table.AutoSize()
        baseContainer.Add(table, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(baseContainer)

