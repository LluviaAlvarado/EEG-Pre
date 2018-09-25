import numpy as np

class WindowCharacterization():

    def getMV(self, eegs, ch):
        MV = []
        MVE = []
        for eeg in eegs:
            MV = []
            for channel in ch:
                maxs = []
                mins = []
                for w in eeg.windows:
                    max = np.amax(w.readings[channel])
                    min = np.amin(w.readings[channel])
                    maxs.append(max)
                    mins.append(min)
                    # getting the average max voltage per window
                max = np.average(maxs)
                min = np.average(mins)
                MV.append([min, max])
            MVE.append(MV)
        return MVE

    def getMagFase(self, eegs, amountHF, ch):
        MagFaseE = []
        for eeg in eegs:
            MagFas = []
            for channel in ch:
                ffts = []
                Mag = []
                Fase =[]
                for w in eeg.windows:
                    fourier = np.fft.rfft(w.readings[channel], len(w.readings[channel]))
                    index = int((len(w.readings[channel]) / 2) - amountHF)
                    group = []
                    for i in range(index, int(len(w.readings[channel]) / 2)):
                        group.append(fourier[i])
                    ffts.append(group)
                    for i in range(amountHF):
                        aux = []
                        for fft in ffts:
                            aux.append(fft[i])
                        fft = np.average(aux)
                        # getting the magnitude and fase for each value of fft
                        magnitude = np.sqrt(np.exp2(fft.real) + np.exp2(fft.imag))
                        fase = np.arctan((np.exp2(fft.imag) / np.exp2(fft.real)))
                        Mag.append(magnitude)
                        Fase.append(fase)
                for i in range(amountHF):
                    n = i
                    fc =[]
                    fm =[]
                    for u in range(len(eeg.windows)):
                        fc.append(Fase[n])
                        fm.append(Mag[n])
                        n += amountHF
                    MagFas.append([np.average(fm), np.average(fc)])
                    i += amountHF
            MagFaseE.append(MagFas)
        return MagFaseE

    def getAUC(self, eegs, ch):
        AUCE =[]
        for eeg in eegs:
            AUC = []
            for channel in ch:
                areas = []
                for w in eeg.windows:
                    dx = 1
                    area = np.trapz(w.readings[channel], dx=dx)
                    areas.append(area)
                    # getting the average area per window
                area = np.average(areas)
                AUC.append(area)
            AUCE.append(AUC)
        return AUCE