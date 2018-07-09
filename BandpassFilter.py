# Imports
from WindowDialog import *
from WindowEditor import *
# local imports

class brainWave:
    def __init__(self, name,lowFrequency,  hiFrequency ):
        self.name = name
        self.hiFrequency = hiFrequency
        self.lowFrequency = lowFrequency

    def getFormat(self):
        blank =""
        i = len(self.name)
        while i < 10:
            blank =  blank + " "
            i+=1
        s = self.name +blank+" Low:  "+str(self.lowFrequency)+"Hz    High:  "+str(self.hiFrequency)+"Hz"
        return s


class PreBPFW (wx.Frame):
    """
        window that contains the Bandpass Filter configuration and
        open visualisation window
        """
    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Pre configuración del filtrado", )
        self.SetSize(500, 500)
        self.Centre()

        self.waves = self.defaultWaves()
        self.customWaves = []
        # create base panel in the frame
        self.pnl = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.BORDER_SUNKEN)
        # base vbox
        self.baseSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        infoLabel = wx.StaticText(self.pnl, label="Listado de canales:")
        extraCannels = wx.StaticText(self.pnl, label="Canales personalizados:")
        info = wx.StaticText(self.pnl, label="De doble clic sobre un canal\npara editar la frecuencias")
        self.waveList = wx.CheckListBox(self.pnl, choices=self.wavestoString(self.waves))
        self.extraList = wx.CheckListBox(self.pnl,choices=self.wavestoString(self.customWaves), style=wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_NEEDED_SB)
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

        self.buttonSizer.AddSpacer(70)
        appliyButton = wx.Button(self.pnl, label="Aplicar Filtrado")
        viewButton = wx.Button(self.pnl, label="Visualizar")
        self.buttonSizer.Add(appliyButton, -1, wx.EXPAND | wx.ALL, 5)
        self.buttonSizer.Add(viewButton, -1, wx.EXPAND | wx.ALL, 5)

        self.baseSizer.Add(self.buttonSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)

    def defaultWaves(self):
        w = [brainWave("Gamma", 40, 100), brainWave("Beta", 12, 40), brainWave("Alpha", 8, 12),
             brainWave("Theta", 4, 8), brainWave("Delta", 0, 4)]
        return w

    def wavestoString(self, w):
        str = []
        for wave in w:
            str.append(wave.getFormat())
        return str

    def addCustom(self, event):
        name, lowF, higF, flag = self.getWaveData()
        if flag:
            w = brainWave(name, lowF, higF)
            self.customWaves.append(w)
            self.extraList.Append(w.getFormat())


    def delCustom(self, event):
        index = self.extraList.GetSelection()
        if self.extraList.GetCount() > 0 and index > -1:
            self.extraList.Delete(index)
            self.customWaves.pop(index)


    def onEdit(self, waves, waveList):
        index = waveList.GetSelection()
        name, lowF, higF, flag = self.getWaveData(waves[index].name, waves[index].lowFrequency, waves[index].hiFrequency)
        if flag:
            waves[index].name = name
            waves[index].lowFrequency = lowF
            waves[index].hiFrequency = higF
            waveList.Clear()
            waveList.Append(self.wavestoString(waves))



    def getWaveData(self,name="Nuevo", lowF = 1, higF = 10):
        # giving a default value in ms to avoid user errors
        falg = True
        with WindowCustomWave(self, name, lowF, higF) as dlg:
            dlg.ShowModal()
            if dlg.flag:
            # handle dialog being cancelled or ended by some other button
                if dlg.name.GetValue() !="":
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
                falg = False
        return name, lowF, higF, falg








