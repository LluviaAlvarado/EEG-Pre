# Imports
import numpy as np
import wx.grid

from WindowEditor import *
from WindowDialog import *
from WindowCharacterization import *


# Esta clase tiene cosas que debo arreglar ya porque esta feo lo que hice


class WindowAttributes(wx.Frame):
    """
    window that contains opciones para caratersar
    """

    def __init__(self, parent, eegs, p):
        wx.Frame.__init__(self, parent, -1, "Caracterizar")
        self.SetSize(1000, 600)
        self.Centre()
        self.parent = p
        self.project = parent.project
        self.parent.windowDB = []
        self.parent.windowSelec = []
        self.eegs = eegs

        # Variables a considerar
        self.amountHF = 1  # la cantidad de salidas que quieren del fft
        self.setofData = []  # La matriz que contiene el se de datos final
        self.opcAttributes = ["Espectro de magnitud", "Espectro de fase", "Area bajo la curva", "Voltaje máximo",
                              "Voltaje mínimo"]
        self.opcChannels = self.project.chLabels

        self.classRecord = []
        # Create visual components
        baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        checkSizerAT = wx.BoxSizer(wx.HORIZONTAL)
        opcSizerAT = wx.BoxSizer(wx.VERTICAL)
        checkSizerCH = wx.BoxSizer(wx.HORIZONTAL)
        opcSizerCH = wx.BoxSizer(wx.VERTICAL)

        leftPnl = wx.Panel(self, size=(300, 600))
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        opcATLabel = wx.StaticText(leftPnl, label="Opciones de atributos:")
        self.opcATList = wx.CheckListBox(leftPnl, choices=self.opcAttributes, size=(220, 90))
        self.opcATList.Bind(wx.EVT_LISTBOX_DCLICK, lambda event: self.confFFT(event, self.opcATList.GetSelection()))
        bmp = wx.Bitmap("src/check-all.png", wx.BITMAP_TYPE_PNG)
        ubmp = wx.Bitmap("src/uncheck.png", wx.BITMAP_TYPE_PNG)

        btnAT1 = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp,
                                 size=(bmp.GetWidth(), bmp.GetHeight()))
        btnAT2 = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=ubmp,
                                 size=(ubmp.GetWidth(), ubmp.GetHeight()))
        btnAT1.Bind(wx.EVT_BUTTON, self.allAT)
        btnAT2.Bind(wx.EVT_BUTTON, self.noAT)

        btnCH1 = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=bmp,
                                 size=(bmp.GetWidth(), bmp.GetHeight()))
        btnCH2 = wx.BitmapButton(leftPnl, id=wx.ID_ANY, style=wx.NO_BORDER, bitmap=ubmp,
                                 size=(ubmp.GetWidth(), ubmp.GetHeight()))
        btnCH1.Bind(wx.EVT_BUTTON, self.allCH)
        btnCH2.Bind(wx.EVT_BUTTON, self.noCH)

        opcCHLabel = wx.StaticText(leftPnl, label="Canales disponibles:")
        self.opcCHList = wx.CheckListBox(leftPnl, choices=self.opcChannels, size=(220, 90))
        applyButton = wx.Button(leftPnl, label="Aplicar")
        applyButton.Bind(wx.EVT_BUTTON, self.apply)
        expLabel = wx.StaticText(leftPnl, label="Seleccione la filas para etiquetar")
        selButton = wx.Button(leftPnl, label="Etiquetar seleccion")
        selButton.Bind(wx.EVT_BUTTON, self.etiquetar)

        coppyButton = wx.Button(leftPnl, label="Copy")
        coppyButton.Bind(wx.EVT_BUTTON, self.Copy)

        leftSizer.Add(opcATLabel, 0, wx.EXPAND | wx.ALL, 5)

        checkSizerAT.Add(self.opcATList, 0, wx.EXPAND | wx.ALL, 5)
        checkSizerAT.Add(opcSizerAT, 0, wx.EXPAND | wx.ALL, 5)
        opcSizerAT.Add(btnAT1, 0, wx.EXPAND | wx.ALL, 0)
        opcSizerAT.Add(btnAT2, 0, wx.EXPAND | wx.ALL, 0)
        leftSizer.Add(checkSizerAT, 0, wx.EXPAND | wx.ALL, 5)

        leftSizer.Add(opcCHLabel, 0, wx.EXPAND | wx.ALL, 5)

        checkSizerCH.Add(self.opcCHList, 0, wx.EXPAND | wx.ALL, 5)
        checkSizerCH.Add(opcSizerCH, 0, wx.EXPAND | wx.ALL, 5)
        opcSizerCH.Add(btnCH1, 0, wx.EXPAND | wx.ALL, 0)
        opcSizerCH.Add(btnCH2, 0, wx.EXPAND | wx.ALL, 0)
        leftSizer.Add(checkSizerCH, 0, wx.EXPAND | wx.ALL, 5)
        leftSizer.Add(applyButton, 0, wx.EXPAND | wx.ALL, 20)
        leftSizer.Add(coppyButton, 0, wx.EXPAND | wx.ALL, 20)

        leftSizer.AddSpacer(130)
        leftSizer.Add(expLabel, 0, wx.EXPAND | wx.BOTTOM, 20)
        leftSizer.Add(selButton, 0, wx.EXPAND | wx.BOTTOM, 20)
        leftPnl.SetSizer(leftSizer)
        rightPnl = wx.Panel(self, size=(700, 600))
        # table of sets
        self.table = GridTab(rightPnl, eegs)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.table, 0, wx.EXPAND | wx.ALL, 1)
        rightPnl.SetSizer(rightSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 3)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(baseContainer)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def Copy(self, event):
        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText("Dood")
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.dataObj)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")

    def allAT(self, event):
        a = []
        for i in range(len(self.opcAttributes)):
            a.append(i)
        self.opcATList.SetCheckedItems(a)

    def noAT(self, event):
        self.opcATList.SetCheckedItems([])

    def allCH(self, event):
        a = []
        for i in range(len(self.opcChannels)):
            a.append(i)
        self.opcCHList.SetCheckedItems(a)

    def noCH(self, event):
        self.opcCHList.SetCheckedItems([])

    def onClose(self, event):
        self.replaceDefault(event)
        self.check(event)
        self.parent.windowDB = self.setofData
        self.parent.windowSelec = self.table.columLabes
        self.GetParent().ForwardChanges(self.parent)
        self.parent.onCloseModule()
        self.Destroy()

    def replaceDefault(self, event):
        t = self.table.table
        for row in range(t.NumberRows):
            value = t.GetCellValue(row, t.NumberCols - 1)
            if value == "":
                t.SetCellValue(row, t.NumberCols - 1, "default")

    def check(self, event):
        t = self.table.table
        for row in range(t.NumberRows):
            tupla = []
            for col in range(t.NumberCols):
                tupla.append(t.GetCellValue(row, col))
            self.setofData.append(tupla)

    def etiquetar(self, event):
        eti = self.ask("Etiqueta para los seleccionados", "etiqueta")
        t = self.table.table
        s = t.GetSelectedRows()
        for row in s:
            t.SetCellValue(row, t.NumberCols - 1, eti)

    def ask(self, message='', default_value=''):
        dlg = wx.TextEntryDialog(self, message, caption="Etiqueta", value=default_value)
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def applyFFT(self, selectedCH):
        eegs = self.eegs
        # setting MV to the project
        self.GetParent().project.windowMagFase = WindowCharacterization().getMagFase(eegs, self.amountHF, selectedCH)

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

    def applyAUC(self, selectedCH):
        eegs = self.eegs
        # setting AUC to the project
        self.GetParent().project.windowAUC = WindowCharacterization().getAUC(eegs, selectedCH)

    def applyMV(self, selectedCH):
        eegs = self.eegs
        self.GetParent().project.windowMinMaxVolt = WindowCharacterization().getMV(eegs, selectedCH)

    def ReDo(self, actions, eegs):
        selectedAT = actions[0]
        selectedCH = actions[1]
        selecCH = actions[2]
        for opc in selectedAT:
            if opc == 0 or opc == 1:
                # Transformada rápida de Fourier(Magnitud y Fase)
                self.applyFFT(selectedCH)
            elif opc == 2:
                # Area bajo la curva
                self.applyAUC(selectedCH)
            elif opc == 3:
                # Voltaje maximo
                self.applyMV(selectedCH)
            elif opc == 4:
                # Voltaje maximo
                self.applyMV(selectedCH)
        self.table.setValues(self.project, selectedAT, selecCH, self.amountHF)

    def apply(self, event):
        selectedAT = self.opcATList.GetCheckedItems()
        selectedCH = self.opcCHList.GetCheckedItems()
        selecCH = self.opcCHList.GetCheckedStrings()
        self.parent.actions = [selectedAT, selectedCH, selecCH]
        for opc in selectedAT:
            if opc == 0 or opc == 1:
                # Transformada rápida de Fourier(Magnitud y Fase)
                self.applyFFT(selectedCH)
            elif opc == 2:
                # Area bajo la curva
                self.applyAUC(selectedCH)
            elif opc == 3:
                # Voltaje maximo
                self.applyMV(selectedCH)
            elif opc == 4:
                # Voltaje maximo
                self.applyMV(selectedCH)
        self.table.setValues(self.project, selectedAT, selecCH, self.amountHF)


class GridTab(wx.Panel):

    def __init__(self, p, eegs):
        wx.Panel.__init__(self, p, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN, size=p.Size)
        self.baseContainer = wx.BoxSizer(wx.HORIZONTAL)
        self.table = wx.grid.Grid(self, size=self.Size)
        self.table.CreateGrid(len(eegs), 8)
        self.project = []
        self.selecdAT = []
        self.columLabes = []
        self.selecdCH = []
        self.hf = []
        self.tam = []
        self.eegs = eegs

        i = 0
        for eeg in eegs:
            self.table.SetRowLabelValue(i, eeg.name)
            i += 1
        self.table.AlwaysShowScrollbars(True, False)
        self.baseContainer.Add(self.table, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.baseContainer)

    def setValues(self, project, selectedAT, selectedCh, amountHF):
        self.project = project
        self.selecdAT = selectedAT
        self.selecdCH = selectedCh
        self.hf = amountHF
        self.table.Show()
        self.update()
        self.fillTable()

    def update(self):
        self.table.DeleteRows(0, self.table.NumberRows)
        self.table.DeleteCols(0, self.table.NumberCols)
        self.Refresh()
        self.tam = [0, 0, 0, 0, 0]
        for i in self.selecdAT:
            self.tam[i] = 1
        num_of_col = len(self.selecdAT)
        l = len(self.selecdCH)
        num_of_col = num_of_col * l
        if 0 in self.selecdAT:
            num_of_col = num_of_col - (1 * l) + (self.hf * l)
            self.tam[0] = self.hf
        if 1 in self.selecdAT:
            num_of_col = num_of_col - (1 * l) + (self.hf * l)
            self.tam[1] = self.hf
        self.table.AppendRows(len(self.eegs))
        self.table.AppendCols(num_of_col + 1)

        labes = ["EM", "EF", "Area_bajo_la_curva", "Voltaje_máximo", "Voltaje_mínimo"]
        self.columLabes = []
        for i in self.selecdCH:
            for y in self.selecdAT:
                if y in self.selecdAT:
                    for x in range(self.tam[y]):
                        if self.tam[y] > 1:
                            self.columLabes.append(str(i) + "_" + labes[y] + str(x + 1))
                        else:
                            self.columLabes.append(str(i) + "_" + labes[y])
        i = 0
        for eeg in self.eegs:
            self.table.SetRowLabelValue(i, eeg.name)
            i += 1
        i = 0
        for la in self.columLabes:
            self.table.SetColLabelValue(i, la)
            i += 1
        self.table.SetColLabelValue(num_of_col, "Etiqueta")

        self.table.AutoSizeColumns()

    def fillTable(self):
        wMF = self.project.windowMagFase
        wAUC = self.project.windowAUC
        wMV = self.project.windowMinMaxVolt
        info = [wMF, wMF, wAUC, wMV, wMV]
        dataEEG = []
        for eeg in range(len(self.eegs)):
            data = []
            for i in range(len(self.selecdCH)):
                for y in self.selecdAT:
                    if y in self.selecdAT:
                        for x in range(self.tam[y]):
                            if y == 0:
                                data.append(info[y][eeg][x + (i * self.tam[y])][0])
                            elif y == 1:
                                data.append(info[y][eeg][x + (i * self.tam[y])][1])
                            elif y == 3:
                                data.append(info[y][eeg][x + i][1])
                            elif y == 4:
                                data.append(info[y][eeg][x + i][0])
                            else:
                                data.append(info[y][eeg][x + i])
            dataEEG.append(data)
        for row in range(len(self.eegs)):
            for col in range(self.table.NumberCols - 1):
                self.table.SetCellValue(row, col, str(dataEEG[row][col]))
                self.table.SetReadOnly(row, col, True)
        self.table.AutoSizeColumns()
