import wx


class HintPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(300, parent.Size[1] / 4))

        self.SetBackgroundColour(wx.Colour(230, 230, 250, 50))
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.tt = wx.StaticText(self, label="", style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.tt.SetFont(wx.Font(12, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.it = wx.StaticText(self, label="", style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.it.SetFont(wx.Font(10, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        sizer.AddSpacer(5)
        sizer.Add(self.tt, 0, wx.EXPAND | wx.ALL, 10)
        sizer.AddSpacer(2)
        sizer.Add(self.it, 0, wx.EXPAND | wx.ALL, 20)
        self.SetSizer(sizer)

    def changeModule(self, module):
        if module == 0:
            self.tt.SetLabelText("Módulo de Archivos.")
            self.it.SetLabelText("Carga y Visualiza EEG.\n Edita Ventanas.")
        elif module == 1:
            self.tt.SetLabelText("Módulo de Filtrado\npor Bandas.")
            self.it.SetLabelText("Filtra EEGs por las\n bandas que necesites.")
        elif module == 2:
            self.tt.SetLabelText("Módulo de Eliminación\n de Artefactos.")
            self.it.SetLabelText("Elimina artefactos de manera \nautomática o manual.")
        elif module == 3:
            self.tt.SetLabelText("Módulo de Caracterización\n de Ventanas.")
            self.it.SetLabelText("Obtén características importantes \nde las ventanas de los EEG\npara su análisis.")
        elif module == 4:
            self.tt.SetLabelText("Módulo de K-Means.")
            self.it.SetLabelText("Herramienta de aprendizaje para\nclasificación automática y \nanálisis de ventanas.")
        elif module == 5:
            self.tt.SetLabelText("Módulo de Árbol\n de Decisión.")
            self.it.SetLabelText("Herramienta de aprendizaje para\nclasificación y \nanálisis de ventanas.")
        elif module == 6:
            self.tt.SetLabelText("Módulo de Filtrado\n por Bandas.")
            self.it.SetLabelText("Filtra EEGs por las \nbandas que necesites.")
        elif module == 7:
            self.tt.SetLabelText("Módulo de Filtrado\n por Bandas.")
            self.it.SetLabelText("Filtra EEGs por las \nbandas que necesites.")
