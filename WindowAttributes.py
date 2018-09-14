# Imports
import numpy as np
import wx.grid

from WindowEditor import *
from WindowDialog import *
from WindowCharacterization import *


# Esta clase tiene cosas que debo arreglar ya porque esta feo lo que hice


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
        self.windowLabel = []
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        leftPnl = wx.Panel(self, size=(300, 600))
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        opcLabel = wx.StaticText(leftPnl, label="Opciones: ")
        self.choices = ["Espectro de magnitud", "Espectro de fase", "Area bajo la curva", "Voltaje máximo",
                        "Voltaje mínimo"]
        checkSizer = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.Bitmap("src/config.png", wx.BITMAP_TYPE_PNG)

        self.optionsList = wx.CheckListBox(leftPnl, choices=self.choices, size=(270, 90))
        applyButton = wx.Button(leftPnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.apply)

        leftSizer.Add(opcLabel, 0, wx.EXPAND | wx.ALL, 5)
        checkSizer.Add(self.optionsList, 0, wx.EXPAND | wx.ALL, 5)
        self.optionsList.Bind(wx.EVT_LISTBOX_DCLICK, lambda event: self.confFFT(event, self.optionsList.GetSelection()))
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
        configButton = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp,
                                       size=(bmp.GetWidth(), bmp.GetHeight()))
        configButton.Hide()
        configButton.Bind(wx.EVT_BUTTON, lambda event: self.confFFT(event, 1))
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, event):
        self.GetParent().onCHClose()
        self.Destroy()

    def applyFFT(self):
        eegs = self.GetParent().project.EEGS
        # setting MV to the project
        self.GetParent().project.windowMagFase = WindowCharacterization().getMagFase(eegs)

    def confFFT(self, event, opc):
        if opc == 1 or opc == 0:
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
        eegs = self.GetParent().project.EEGS
        # setting AUC to the project
        self.GetParent().project.windowAUC = WindowCharacterization().getAUC(eegs)

    def applyMV(self):
        eegs = self.GetParent().project.EEGS
        self.GetParent().project.windowMinMaxVolt = WindowCharacterization().getMV(eegs)

    def apply(self, event):
        selected = self.optionsList.GetCheckedItems()
        for opc in selected:
            if opc == 0 or opc == 1:
                # Transformada rápida de Fourier(Magnitud y Fase)
                self.applyFFT()
            elif opc == 2:
                # Area bajo la curva
                self.applyAUC()
            elif opc == 3:
                # Voltaje maximo
                self.applyMV()
            elif opc == 4:
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
        hf = self.GetParent().GetParent().GetParent().amountHF
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        table = wx.grid.Grid(self, size=(600, 600))
        num_of_col = len(selected)
        if 0 in selected:
            num_of_col = num_of_col - 1 + hf
        if 1 in selected:
            num_of_col = num_of_col - 1 + hf
        table.CreateGrid(len(self.eeg.windows), num_of_col + 1)
        ch = ["", "", "Area bajo la curva", "Voltaje máximo", "Voltaje mínimo"]
        table.SetColLabelValue(num_of_col, "Etiqueta")
        windowSize = []
        add = 0
        eegs = project.EEGS
        for eeg in eegs:
            windowSize.append(add)
            add += len(eeg.windows)
        numero = 0
        col = 0
        sum = 0
        if 0 in selected:
            numero += 1
            sum += hf
            for i in range(hf):
                table.SetColLabelValue(col, "EM" + str(i + 1))
                col += 1
            da = project.windowMagFase
            data = [x[0] for x in da]
            u = 0
            row = 0
            while row < len(self.eeg.windows):
                table.SetRowLabelValue(row, str(row + 1))
                col = 0
                while col < hf:
                    table.SetCellValue(row, col, str(data[u + (windowSize[num] * hf)]))
                    table.SetReadOnly(row, col, True)
                    col += 1
                    u += 1
                row += 1

        if 1 in selected:
            sum += hf
            col = hf * numero
            for i in range(hf):
                table.SetColLabelValue(col, "EF" + str(i + 1))
                col += 1
            da = project.windowMagFase
            data = [x[1] for x in da]
            u = 0
            row = 0
            while row < len(self.eeg.windows):
                table.SetRowLabelValue(row, str(row + 1))
                col = 0
                while col < hf:
                    table.SetCellValue(row, col + (hf * numero), str(data[u + windowSize[num]]))
                    table.SetReadOnly(row, col + (hf * numero), True)

                    col += 1
                    u += 1
                row += 1
            numero += 1

        if 2 or 3 or 4 in selected:
            col = sum
            row = 0
            u = 0
            while col < num_of_col:
                table.SetColLabelValue(col, ch[selected[u + numero]])
                col += 1
                u += 1
            data = []
            while row < len(self.eeg.windows):
                table.SetRowLabelValue(row, str(row + 1))
                col = sum
                u = 0
                while col < num_of_col:
                    if selected[u + numero] == 2:
                        data = project.windowAUC
                    if selected[u + numero] == 3:
                        da = project.windowMinMaxVolt
                        data = [x[1] for x in da]
                    if selected[u + numero] == 4:
                        da = project.windowMinMaxVolt
                        data = [x[0] for x in da]
                    table.SetCellValue(row, col, str(data[row + windowSize[num]]))
                    table.SetReadOnly(row, col, True)
                    col += 1
                    u += 1
                row += 1
        table.AutoSize()
        baseContainer.Add(table, 0, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(baseContainer)
