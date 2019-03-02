# Imports
import wx.grid

from Utils import exportCSV
from WindowCharacterization import *
from WindowDialog import *
from WindowEditor import *


class WindowAttributes(wx.Frame):
    """
    window that contains tools for window characterization
    """

    def __init__(self, parent, eegs, p):
        wx.Frame.__init__(self, parent, -1, "Caracterizar Ventanas")
        self.SetSize(1000, 600)
        self.Centre()
        self.parent = p
        self.project = parent.project
        self.eegs = eegs
        self.actions = p.actions
        # Variables a considerar
        self.amountHF = 1  # la cantidad de salidas que quieren del fft
        self.setofData = []  # La matriz que contiene el se de datos final
        self.opcAttributes = ["Espectro de Magnitud y Fase", "Area bajo la curva", "Voltaje máximo",
                              "Voltaje mínimo"]

        self.opcCh =[]
        self.opcChannels = []
        if eegs is not None and len(eegs)>0:
            self.opcCh = list(eegs[0].selectedCh)
            self.opcChannels = []
            for i in self.opcCh:
                self.opcChannels.append(eegs[0].channels[i].label)
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

        exportButton = wx.Button(leftPnl, label="Exportar como (.CSV)")
        exportButton.Bind(wx.EVT_BUTTON, self.Export)

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
        leftSizer.Add(exportButton, 0, wx.EXPAND | wx.ALL, 20)

        leftSizer.AddSpacer(60)
        leftSizer.Add(expLabel, 0, wx.EXPAND | wx.BOTTOM, 20)
        leftSizer.Add(selButton, 0, wx.EXPAND | wx.BOTTOM, 20)
        leftPnl.SetSizer(leftSizer)
        rightPnl = wx.Panel(self, size=(2500,2500))
        # table of sets
        self.table = GridTab(rightPnl, eegs)
        rightSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer.Add(self.table, 0, wx.EXPAND | wx.ALL, 1)
        rightPnl.SetSizer(rightSizer)
        baseContainer.Add(leftPnl, 0, wx.EXPAND | wx.ALL, 3)
        baseContainer.Add(rightPnl, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizer(baseContainer)
        if self.parent.windowDB is not None and len(self.parent.windowDB) > 1:
            self.ReFill(p)
        else:
            self.parent.windowDB = []
            self.parent.windowSelec = []
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def GetTableData(self):
        Row = self.table.table.NumberRows
        Col = self.table.table.NumberCols
        Clip = []
        for r in range(Row):
            re = ""
            for c in range(Col):
                re += str(self.table.table.GetCellValue(r, c)) + ", "
            re = re[:-2]
            Clip.append(re)
        return Clip

    def Export(self, event):
        data = self.GetTableData()
        f = "Name,"
        for fe in self.table.columLabes:
            f += fe + ","
        names = []
        for eeg in self.eegs:
            names.append(eeg.name + ",")
        exportCSV(self, data, names, f)

    def ReFill(self, p):
        self.table.refill(p.windowDB, p.windowSelec)

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

    def applyMagFase(self, selectedCH):
        eegs = self.eegs
        self.GetParent().project.windowMagFase = WindowCharacterization().getMagFase(eegs, self.amountHF, selectedCH)

    def confFFT(self, event, opc):
        if opc == 0:
            dlg = wx.TextEntryDialog(self, 'Cantidad de espectros a calcular: ', 'Configuración')
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
            if opc == 0:
                self.applyMagFase(selectedCH)
            elif opc == 1:
                self.applyAUC(selectedCH)
            elif opc == 2:
                # Voltaje máximo
                self.applyMV(selectedCH)
            elif opc == 3:
                # Voltaje mínimo
                self.applyMV(selectedCH)
        self.table.setValues(self.project, selectedAT, selecCH, self.amountHF)
        self.replaceDefault(0)
        self.check(0)
        self.parent.windowDB = self.setofData
        self.parent.windowSelec = self.table.columLabes
        self.parent.actions = self.actions

    def apply(self, event):
        selectedAT = self.opcATList.GetCheckedItems()
        selectedCH = self.opcCHList.GetCheckedItems()
        selecCH = self.opcCHList.GetCheckedStrings()
        self.actions = [selectedAT, selectedCH, selecCH]
        self.GetParent().setStatus("Calculando características...", 1)
        for opc in selectedAT:
            if opc == 0:
                self.applyMagFase(selectedCH)
            elif opc == 1:
                # Area bajo la curva
                self.applyAUC(selectedCH)
            elif opc == 2:
                # Voltaje máximo
                self.applyMV(selectedCH)
            elif opc == 3:
                # Voltaje mínimo
                self.applyMV(selectedCH)
        self.table.setValues(self.project, selectedAT, selecCH, self.amountHF)
        self.parent.actions = self.actions
        self.GetParent().setStatus("", 0)


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
        self.table.Bind(wx.EVT_KEY_DOWN, self.OnKey)

    def refill(self, data, coln):
        self.table.DeleteCols(0, self.table.NumberCols)
        self.Refresh()
        self.columLabes = coln
        self.table.AppendCols(len(coln) + 1)
        i = 0
        for label in coln:
            self.table.SetColLabelValue(i, label)
            i += 1
        self.table.SetColLabelValue(i, "Etiqueta")
        row = len(data)
        col = len(data[0])
        for i in range(row):
            for j in range(col):
                self.table.SetCellValue(i, j, str(data[i][j]))
                self.table.SetReadOnly(i, j, True)
        self.table.AutoSizeColumns()

    def OnKey(self, event):
        # If Ctrl+C is pressed
        if event.ControlDown() and event.GetKeyCode() == 67:
            top_left = self.table.GetSelectionBlockTopLeft()[0]
            bottom_right = self.table.GetSelectionBlockBottomRight()[0]
            clip = self.printSelectedCells(top_left, bottom_right)
            self.Copy(clip)

    def Copy(self, text):
        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText(text)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(self.dataObj)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard", "Error")

    def printSelectedCells(self, top_left, bottom_right):
        cells = []
        rows_start = top_left[0]
        rows_end = bottom_right[0]
        cols_start = top_left[1]
        cols_end = bottom_right[1]
        len = cols_end - cols_start
        rows = range(rows_start, rows_end + 1)
        cols = range(cols_start, cols_end + 1)

        cells.extend([(row, col)
                      for row in rows
                      for col in cols])

        ClippytheClip = ""
        i = 0
        for cell in cells:
            i += 1
            row, col = cell
            ClippytheClip += str(self.table.GetCellValue(row, col))
            if i > len:
                i = 0
                ClippytheClip += "\n"
            else:
                ClippytheClip += "\t"
        return ClippytheClip

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
        self.tam = [0, 0, 0, 0]
        for i in self.selecdAT:
            self.tam[i] = 1
        num_of_col = len(self.selecdAT)
        l = len(self.selecdCH)
        num_of_col = num_of_col * l
        if 0 in self.selecdAT:
            num_of_col = num_of_col - l + (self.hf * 3 * l)
            self.tam[0] = self.hf * 3
        if 2 in self.selecdAT:
            num_of_col = num_of_col - l + (l * 2)
            self.tam[2] = l*2
        if 3 in self.selecdAT:
            num_of_col = num_of_col - l + (l * 2)
            self.tam[3] = l*2
        self.table.AppendRows(len(self.eegs))
        self.table.AppendCols(num_of_col + 1)
        labes = [["EM ", "F EM ", "EF "], "Area bajo la curva", ["Voltaje máximo", "Ms VMax"],
                 ["Voltaje mínimo", "Ms VMin"]]
        self.columLabes = []
        for y in self.selecdAT:
            if y == 1:
                for i in self.selecdCH:
                    self.columLabes.append(str(i) + " " + labes[y])
            if y == 2 or y == 3:
                for i in self.selecdCH:
                    self.columLabes.append(str(i) + " " + labes[y][0])
                    self.columLabes.append(str(i) + " " + labes[y][1])
            if y == 0:
                for ch in self.selecdCH:
                    u = 0
                    cont = 1
                    for x in range(self.tam[y]):
                        if u == 3:
                            u = 0
                            cont += 1
                        if self.tam[y] > 1:
                            add = ""
                            if y == 0 or y == 1:
                                add = str(cont)
                            self.columLabes.append(ch + " " +labes[y][u] + add)
                            u += 1
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
        info = [wMF, wAUC, wMV, wMV]
        dataEEG = []
        for eeg in range(len(self.eegs)):
            data = []
            for y in self.selecdAT:
                if y == 1:
                    for i in range(len(self.selecdCH)):
                        for x in range(self.tam[y]):
                            data.append(info[y][eeg][x + i])
                if y == 2 or y == 3:
                    for canal in range(len(self.selecdCH)):
                        for cont in range(2):
                            if y == 2:
                                data.append(info[y][eeg][canal][1][cont])
                            elif y == 3:
                                data.append(info[y][eeg][canal][0][cont])
                if y == 0:
                    for canal in range(len(self.selecdCH)):
                        u = 0
                        num = 0
                        for x in range(self.tam[y]):
                            if u == 3:
                                u = 0
                                num += 1
                            if y == 0:
                                data.append(info[y][eeg][u] [canal] [num])
                                u += 1
                            elif y == 1:
                                data.append(info[y][eeg][canal][u][num])
                                u += 1
            dataEEG.append(data)
        for row in range(len(self.eegs)):
            for col in range(self.table.NumberCols - 1):
                self.table.SetCellValue(row, col, str(dataEEG[row][col]))
                self.table.SetReadOnly(row, col, True)
        self.table.AutoSizeColumns()
