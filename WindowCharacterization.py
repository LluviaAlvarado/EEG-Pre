import numpy as np
from Utils import sampleToMS


class WindowCharacterization:

    def getMV(self, eegs, ch):
        MVE = []
        # gets the max-min voltaje of eeg and ms when it happened
        for eeg in eegs:
            MV = []
            max = 0
            msmax = 0
            min = 0
            msmin = 0
            for i in ch:
                mx = np.amax(eeg.channels[i].readings)
                mn = np.amin(eeg.channels[i].ch.readings)
                if mx > max:
                    max = mx
                    imax = np.argmax(ch.readings)
                    msmax = sampleToMS(imax, eeg.frequency, eeg.duration)
                if mn < min:
                    min = mn
                    imin = np.argmin(ch.readings)
                    msmin = sampleToMS(imin, eeg.frequency, eeg.duration)
            MV.append([[min, msmin], [max, msmax]])
            MVE.append(MV)
        return MVE

    def getFas(self, eegs, n, ch):
        FasE = []
        for eeg in eegs:
            Fase = []
            frFas = []
            for i in range(n):
                Fase.append(0)
                frFas.append(0)
            for i in ch:
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                mags = []
                for v in range(len(fft)):
                    # getting the fase for each value of fft
                    fase = np.arctan((np.exp2(fft.imag) / np.exp2(fft.real)))
                    for j in range(n):
                        if fase > Fase[j]:
                            Fase[j] = fase
                            frFas[j] = v
            FasE.append([Fase, frFas])
        return FasE

    def getMag(self, eegs, n, ch):
        MagE = []
        for eeg in eegs:
            Mag = []
            msMag = []
            for i in range(n):
                Mag.append(0)
                msMag.append(0)
            for i in ch:
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                mags = []
                for v in range(len(fft)):
                    # getting the magnitude for each value of fft
                    magnitude = np.sqrt(np.exp2(fft[v].real) + np.exp2(fft[v].imag))
                    for j in range(n):
                        if magnitude > Mag[j]:
                            Mag[j] = magnitude
                            msMag[j] = v
            MagE.append([Mag, msMag])
        return MagE

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