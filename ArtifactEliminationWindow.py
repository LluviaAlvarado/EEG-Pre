# local imports
from FilesWindow import *
from BPFWindow import *
from WindowDialog import *
from ComponentViewer import *
from FastICA import *
import numpy as np
import threading
from wx.adv import NotificationMessage
import pywt
import scipy.signal as signal
import peakutils
from os import listdir
from os.path import isfile, join
from scipy.stats.stats import pearsonr
from wx.adv import AnimationCtrl, Animation


class ArtifactEliminationWindow(wx.Frame):
    """
        window that contains the artifact elimination configuration and
        opens a visualisation window
        """

    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Eliminación de Artefactos con FastICA")
        self.SetSize(250, 250)
        self.Centre()
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
        self.exportButton.Bind(wx.EVT_BUTTON, self.exportar)
        self.baseSizer.Add(manualButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(autoButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.viewButton, -1, wx.EXPAND | wx.ALL, 5)
        self.baseSizer.Add(self.exportButton, -1, wx.EXPAND | wx.ALL, 5)
        self.pnl.SetSizer(self.baseSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        # making ECG template
        # The "Daubechies" wavelet is a rough approximation to a real,
        # single, heart beat ("pqrst") signal
        pqrst = signal.wavelets.daub(10)
        # Add the gap after the pqrst when the heart is resting.
        samples_rest = 10
        zero_array = np.zeros(samples_rest, dtype=float)
        self.pqrst_full = np.concatenate([pqrst, zero_array])

    def onClose(self, event):
        self.GetParent().onARClose()
        self.Destroy()

    def exportar(self, event):
        pathPicker = wx.DirDialog(None, "Exportar en:", "D:\Documentos\Computacion\EEG\EEG-Pre\TestFiles\\",
                                  wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if pathPicker.ShowModal() != wx.ID_CANCEL:
            writer = FileReaderWriter()
            windows = []
            windowsExist = False
            for eeg in self.GetParent().project.EEGS:
                writer.writeFile(eeg, self.GetParent().project.name, pathPicker.GetPath())
                if len(eeg.windows) > 0:
                    windowsExist = True
                windows.append([eeg.name, eeg.windows])
            # exporting csv with window information and a txt with the TBE and length in ms
            if windowsExist:
                self.writeWindowFiles(windows, pathPicker.GetPath())

    def writeWindowFiles(self, windows, path):
        # setting cursor to wait to inform user
        self.GetParent().setStatus("Exportando...", 1)
        file = path + "\\" + self.GetParent().project.name + "_windows.csv"
        txt = path + "\\" + self.GetParent().project.name + "_windows.txt"
        if os.path.isfile(file):
            # it already exists
            f = self.GetParent().project.name + "_windows.csv"
            msg = wx.MessageDialog(None, "El archivo '" + f + "' ya existe. "
                                                              "\n¿Desea reemplazar el archivo?", caption="¡Alerta!",
                                   style=wx.YES_NO | wx.CENTRE)
            if msg.ShowModal() == wx.ID_NO:
                return  # we don't to anything
            else:
                # deleting the prev file and txt
                os.remove(file)
                os.remove(txt)
            # writing windowFiles
            FileReaderWriter().writeWindowFiles(windows, file, txt, self.GetParent().project.windowLength,
                    self.GetParent().project.windowTBE)
        self.GetParent().setStatus("", 0)

    def applyFastICA(self, event):
        self.GetParent().setStatus("Buscando Componentes...", 1)
        self.FastICA()
        self.viewButton.Enable()
        self.exportButton.Enable()
        # refresh file window if it is opened
        if self.GetParent().filesWindow is not None:
            self.GetParent().filesWindow.Destroy()
            self.GetParent().filesWindow = FilesWindow(self.GetParent())
            self.GetParent().filesWindow.Show()
        self.openCompView(event)
        self.GetParent().setStatus("", 0)

    def apply(self, artifactSelected):
        if 0 in artifactSelected:
            self.removeEOG()
        if 1 in artifactSelected:
            if len(self.icas) == 0:
                self.FastICA()
            self.removeBlink()
        if 2 in artifactSelected:
            if len(self.icas) == 0:
                self.FastICA()
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
            self.loading = WorkingAnimation(self.GetParent(), 'search')
            self.loading.Play()
            threading.Thread(target=self.apply, args=[artifactSelected]).start()

    def ReadEOGS(self):
        # let's read the EOGS saved in .csv
        p = "src/EOG"
        paths = [f for f in listdir(p) if isfile(join(p, f))]
        csv = []
        for path in paths:
            if ".csv" in path:
                csv.append(self.readCSV(p + "\\" + path))
        return csv

    def readCSV(self, path):
        r = []
        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                r = row[0:int(len(row) - 1)]
        return r

    def removeEOG(self):
        # first we apply FastICA to get IC
        if len(self.icas) == 0:
            self.FastICA()
        for ica in self.icas:
            # reading EOG patterns
            EOGS = self.ReadEOGS()
            # make EOGS same length of components, the patterns are 30s long
            if ica.duration != 30:
                diff = ica.duration - 30
                if diff < 0:
                    # getting just the amount of time
                    newE = []
                    for e in EOGS:
                        # the patterns have a sample rate of 200Hz
                        e = e[0:int(200 * ica.duration)]
                        newE.append(e)
                    EOGS = newE
                else:
                    # getting just the amount of time and padding samples
                    newE = []
                    # the patterns have a sample rate of 200Hz
                    sampAdd = diff * 200
                    timesEOG = sampAdd / len(EOGS[0])
                    for e in EOGS:
                        extension = e * timesEOG
                        e.extend(extension)
                        newE.append(e)
                    EOGS = newE
                sDiff = len(EOGS[0]) - len(ica.components[0])
                if sDiff < 0:
                    newE = []
                    for e in EOGS:
                        new = []
                        for i in range(len(e)):
                            new.append(e[i])
                            pad = [0] * int(abs(sDiff) / len(e))
                            new.extend(pad)
                        newE.append(new)
                    EOGS = newE
                elif sDiff > 0:
                    newE = []
                    for e in EOGS:
                        new = []
                        for i in range(len(e)):
                            new.append(e[i])
                            i += int(abs(sDiff) / len(e))
                        newE.append(new)
                    EOGS = newE
            sDiff = len(EOGS[0]) - len(ica.components[0])
            if sDiff < 0:
                for e in EOGS:
                    pad = [0] * abs(sDiff)
                    e.extend(pad)
            elif sDiff > 0:
                newE = []
                for e in EOGS:
                    new = e[0:int(len(e) - sDiff)]
                    newE.append(new)
                EOGS = newE
            # next we compare with EOG patterns, the ones with
            # high correlation will be analyzed
            newC = []
            for c in ica.components:
                mean = 0
                mean2 = 0
                for eog in EOGS:
                    e = np.array(eog).astype('float64')
                    correlation = pearsonr(c, e)
                    mean += correlation[0]
                    mean2 += correlation[1]
                mean = mean / len(EOGS)
                mean2 = mean2 / len(EOGS)
                if abs(mean) > 0.6 or abs(mean2) > 0.6:
                    # this is an EOG component
                    c = np.array([0.0] * len(c))
                newC.append(c)
            ica.components = newC

    def removeECG(self):
        # first we apply FastICA to get IC
        if len(self.icas) == 0:
            self.FastICA()
        for ica in self.icas:
            # next we compare with ECG pattern, the ones with
            # high correlation will be analyzed
            # Simulated Beats per minute rate
            # For a health, athletic, person, 60 is resting, 180 is intensive exercising
            bpm = 60
            bps = bpm / 60
            # Simumated period of time in seconds that the ecg is captured in
            capture_length = ica.duration
            # Caculate the number of beats in capture time period
            # Round the number to simplify things
            num_heart_beats = int(capture_length * bps)
            # Concatonate together the number of heart beats needed
            ecg_template = np.tile(self.pqrst_full, num_heart_beats)
            diff = int(len(ica.components[0]) - len(ecg_template))
            if diff != 0:
                new = []
                if diff < 0:
                    for i in range(len(ecg_template)):
                        new.append(ecg_template[i])
                        i += int(abs(diff) / len(ecg_template))
                else:
                    for i in range(len(ecg_template)):
                        new.append(ecg_template[i])
                        pad = [0] * int(diff / len(ecg_template))
                        new.extend(pad)
                ecg_template = new
                diff = int(len(ica.components[0]) - len(ecg_template))
                if diff != 0:
                    if diff < 0:
                        ecg_template = ecg_template[0:(len(ecg_template) - diff)]
                    else:
                        ecg_template.extend([0] * diff)
            # checking correlation
            newC = []
            for c in ica.components:
                correlation = pearsonr(c, ecg_template)
                if abs(correlation[0]) > 0.6 or abs(correlation[1]) > 0.6:
                    # checking peaks
                    dist = len(c) / ica.duration / 2
                    peaks = peakutils.indexes(c, thres=0.6, min_dist=dist)
                    if len(peaks) != 0:
                        # testing periodicity}
                        F = 0.0
                        for i in range(len(peaks) - 1):
                            t = float(self.sampleToMS(peaks[i + 1]) - self.sampleToMS(peaks[i]))
                            F += 1 / t
                        # median frequency of peaks
                        F = F / len(peaks)
                        # if it is between min and max of heart rate
                        N = F * (1 + 0.25) - F * (1 - 0.25)
                        if (2 / 3) <= F <= 3:
                            if N >= int(0.8 * F * ica.duration):
                                # this is an ECG component
                                c = np.array([0.0] * len(c))
                newC.append(c)
            ica.components = newC

    def FastICA(self):
        # to remove eye blink and muscular artifacts we
        # will use fastICA then wavelets
        eegs = self.GetParent().project.EEGS
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
        for ica in self.icas:
            newC = []
            for c in ica.components:
                # we need to get up to Ca4 to get to theta band
                Ca4 = pywt.downcoef('a', c, 'Haar', mode='symmetric', level=4)
                # padding to make map to time domain
                new = []
                for i in range(len(Ca4)):
                    new.append(Ca4[i])
                    for j in range(15):
                        new.append(0.0)
                Ca4 = np.array(new)
                # getting all negative peaks index in Ca4
                negative = []
                for i in range(len(Ca4)):
                    if Ca4[i] < 0:
                        negative.append(i)
                neg = Ca4[Ca4 >= 0]
                # computing the mean of the negative peaks
                mean = np.sum(neg) / len(neg)
                # deciding if we remove
                for n in negative:
                    if Ca4[n] < mean:
                        # remove window of 400ms with eye blink
                        centerMs = self.sampleToMS(n)
                        s = self.msToReading(centerMs - 200)
                        e = self.msToReading(centerMs + 200)
                        nSamp = self.GetParent().project.frequency * self.GetParent().project.duration
                        if e >= nSamp:
                            e = nSamp - 1
                        maxN = 0
                        maxI = s
                        while s <= e:
                            if Ca4[s] < maxN:
                                maxN = Ca4[s]
                                maxI = s
                            s += 1
                        # the maximum negative peak is turned to 0
                        Ca4[maxI] = 0.0
                # returning Ca4 to original shape
                ca = []
                for i in range(len(Ca4)):
                    if i % 16 == 0:
                        ca.append(Ca4[i])
                # applying reverse wavelet
                component = pywt.upcoef('a', ca, 'Haar', level=4)
                newC.append(component)
            ica.components = newC

    def sampleToMS(self, s):
        nSamp = self.GetParent().project.frequency * self.GetParent().project.duration
        return ((self.GetParent().project.duration * 1000) * s) / nSamp

    def msToReading(self, ms):
        nSamp = self.GetParent().project.frequency * self.GetParent().project.duration
        return int((ms * nSamp) / (self.GetParent().project.duration * 1000))

    def removeMuscular(self):
        for ica in self.icas:
            newC = []
            for c in ica.components:
                # applying soft thresholding to denoise, removing everythin above 50Hz
                c = pywt.threshold(c, 50, 'less')
                waveletC = pywt.wavedec(c, 'Haar', level=2)
                # wavelet[0] = Ca2 wavelet[1] = Cd2 wavelet[2] = Cd1
                # padding Cd2 to make it same length of Cd1
                new = []
                cd2 = waveletC[1]
                for i in range(len(waveletC[1])):
                    new.append(cd2[i])
                    new.append(0.0)
                waveletC[1] = np.array(new)
                # getting the wavelet power spectral density
                # dividing the component into x frames of a half of a second each
                x = int(ica.duration)*2
                frameL = int(len(new) / x)
                S1 = []
                S2 = []
                maximums = []
                i = 0
                # elevating to power 2 the elements of Cd1
                cd1 = np.power(waveletC[2], 2)
                # elevating to power 2 the elements of Cd2
                cd2 = np.power(waveletC[1], 2)
                for j in range(x):
                    s1 = np.sum(cd1[i:i + frameL])
                    S1.append(s1)
                    s2 = np.sum(cd2[i:i + frameL])
                    S2.append(s2)
                    if s1 > s2:
                        maximums.append(s1)
                    else:
                        maximums.append(s2)
                    i += frameL
                # calculating the mean
                pk = np.sum(maximums) / x
                # comparing mean to WPS
                for i in range(x):
                    if S1[i] > pk:
                        # make all samples in this frame 0
                        for j in range(frameL):
                            waveletC[2][j + (i * frameL)] = 0.0
                    if S2[i] > pk:
                        # make all samples in this frame 0
                        for j in range(frameL):
                            waveletC[1][j + (i * frameL)] = 0.0
                # returning cd2 to original shape
                cd2 = []
                for i in range(len(waveletC[1])):
                    if i % 2 == 0:
                        cd2.append(waveletC[1][i])
                waveletC[1] = np.array(cd2)
                # applying reverse wavelet transform to get resulting component
                component = pywt.waverec(waveletC, 'Haar')
                newC.append(component)
            ica.components = newC

    def EliminateComponents(self):
        self.GetParent().setStatus("Eliminando Artefactos...", 1)
        eegs = self.GetParent().project.EEGS
        i = 0
        for ica in self.icas:
            ica.recreateSignals()
            eegs[i].SetChannels(ica.getSignals())
            i += 1
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
        self.BPFwindow = BFPWindow(self)


