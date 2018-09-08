# Imports
import wx


class WindowDialog(wx.Dialog):

    def __init__(self, parent, l, tbe):
        wx.Dialog.__init__(self, parent, title="Parametros para Ventaneo:",
                           size=(400, 120))
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        lenLabel = wx.StaticText(self, label="Longitud (ms):")
        tbeLabel = wx.StaticText(self, label="TAE (ms):")
        self.length = wx.TextCtrl(self, value=str(l))
        self.tbe = wx.TextCtrl(self, value=str(tbe))
        close = wx.Button(self, label="Aceptar")
        close.Bind(wx.EVT_BUTTON, self.close)
        sizer.Add(lenLabel, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(self.length, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(tbeLabel, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(self.tbe, 0, wx.CENTER | wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddSpacer(self.Size[0] / 1.5)
        btnSizer.Add(close, 1, wx.RIGHT, 5)
        baseSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(btnSizer, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(baseSizer)
        self.Center()

    def close(self, event):
        self.Close(True)


class WindowSaveOnExit(wx.Dialog):
    def __init__(self, parent, opc):
        wx.Dialog.__init__(self, parent, title="EEG Processing:",
                           size=(350, 120))
        self.opc = 0
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        lenLabel = wx.StaticText(self, label="Se han realizado cambios en el proyecto. \n¿Desea guardar los cambios?")
        si = wx.Button(self, label="Si")
        no = wx.Button(self, label="No")
        can = wx.Button(self, label="Cancelar")
        si.Bind(wx.EVT_BUTTON, self.save)
        no.Bind(wx.EVT_BUTTON, self.close)
        can.Bind(wx.EVT_BUTTON, self.back)
        sizer.AddSpacer(20)
        sizer.Add(lenLabel, 0, wx.CENTER | wx.ALL, 5)
        btnSizer.AddSpacer(20)
        btnSizer.Add(si, 0, wx.CENTER | wx.ALL, 5)
        btnSizer.Add(no, 0, wx.CENTER | wx.ALL, 5)
        btnSizer.Add(can, 0, wx.CENTER | wx.ALL, 5)
        baseSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(btnSizer, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(baseSizer)
        self.Center()

    def close(self, event):
        self.opc = 2
        self.Close(True)

    def back(self, event):
        self.opc = 3
        self.Close(True)

    def save(self, event):
        self.opc = 1
        self.Close(True)


class WindowCustomWave(wx.Dialog):
    def __init__(self, parent, name, lowF, higF):
        wx.Dialog.__init__(self, parent, title="Parametros del canal:",
                           size=(270, 190))
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        lowSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        nameLabel = wx.StaticText(self, label="Nombre de la banda:")
        lowLabel = wx.StaticText(self, label="Frecuencia baja (Hz):")
        higLabel = wx.StaticText(self, label="Frecuencia alta (Hz): ")
        self.name = wx.TextCtrl(self, value=str(name))
        self.lowF = wx.TextCtrl(self, value=str(lowF))
        self.higF = wx.TextCtrl(self, value=str(higF))
        self.flag = False
        close = wx.Button(self, label="Aceptar")
        close.Bind(wx.EVT_BUTTON, self.apply)
        nameSizer.Add(nameLabel, 0, wx.CENTER | wx.ALL, 5)
        nameSizer.Add(self.name, 0, wx.CENTER | wx.ALL, 5)
        lowSizer.Add(lowLabel, 0, wx.CENTER | wx.ALL, 5)
        lowSizer.Add(self.lowF, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(higLabel, 0, wx.CENTER | wx.ALL, 5)
        sizer.Add(self.higF, 0, wx.CENTER | wx.ALL, 5)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.AddSpacer(self.Size[0] / 2.2)
        btnSizer.Add(close, 1, wx.RIGHT, 15)
        baseSizer.Add(nameSizer, 0, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(lowSizer, 0, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 2)
        baseSizer.Add(btnSizer, 1, wx.EXPAND | wx.ALL, 2)
        if name != "Nuevo":
            self.name.Disable()
        self.SetSizer(baseSizer)
        self.Center()

    def close(self, event):
        self.flag = False
        self.Close(True)

    def apply(self, event):
        self.flag = True
        self.Close(True)


class WindowAutoAE(wx.Dialog):
    def __init__(self, parent, list):
        wx.Dialog.__init__(self, parent, title="Seleccione los artefactos a eliminar:",
                           size=(200, 170))
        type = "Movimiento Ocular", "Parpadeo", "Muscular", "Cardíaco"
        self.applied = False
        baseSizer = wx.BoxSizer(wx.VERTICAL)
        self.artifactList = wx.CheckListBox(self, choices=type)
        apply = wx.Button(self, label="Aplicar")
        apply.Bind(wx.EVT_BUTTON, self.apply)
        baseSizer.Add(self.artifactList, 0, wx.EXPAND | wx.ALL, 5)
        baseSizer.Add(apply, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(baseSizer)
        self.Center()

    def close(self, event):
        self.Close(True)

    def apply(self, event):
        self.applied = True
        self.Close(True)
