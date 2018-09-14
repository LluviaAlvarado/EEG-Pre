import numpy as np

class WindowCharacterization():

    def getMV(self, eegs):
        MV = []
        for eeg in eegs:
            for w in eeg.windows:
                maxs = []
                mins = []
                for ch in w.readings:
                    max = np.amax(ch)
                    min = np.amin(ch)
                    maxs.append(max)
                    mins.append(min)
                # getting the average max voltage per window
                max = np.average(maxs)
                min = np.average(mins)
                MV.append([min, max])
        return MV

    def getMagFase(self, eegs, amountHF):
        MagFase = []
        for eeg in eegs:
            for w in eeg.windows:
                ffts = []
                for ch in w.readings:
                    fourier = np.fft.rfft(ch, len(ch))
                    index = int((len(ch) / 2) - amountHF)
                    group = []
                    for i in range(index, int(len(ch) / 2)):
                        group.append(fourier[i])
                    ffts.append(group)
                # getting the average frequency for the selected group per window
                MF = []
                for i in range(amountHF):
                    aux = []
                    for fft in ffts:
                        aux.append(fft[i])
                    fft = np.average(aux)
                    # getting the magnitude and fase for each value of fft
                    magnitude = np.sqrt(np.exp2(fft.real) + np.exp2(fft.imag))
                    fase = np.arctan((np.exp2(fft.imag) / np.exp2(fft.real)))
                    MagFase.append([magnitude, fase])
        return MagFase

    def getAUC(self, eegs):
        AUC = []
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
        return AUC