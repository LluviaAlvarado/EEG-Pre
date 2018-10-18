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
                mn = np.amin(eeg.channels[i].readings)
                if mx > max:
                    max = mx
                    imax = np.argmax(eeg.channels[i].readings)
                    msmax = sampleToMS(imax, eeg.frequency, eeg.duration)
                if mn < min:
                    min = mn
                    imin = np.argmin(eeg.channels[i].readings)
                    msmin = sampleToMS(imin, eeg.frequency, eeg.duration)
            MV.append([[min, msmin], [max, msmax]])
            MVE.append(MV)
        return MVE

    def getFase(self, eegs, n, ch):
        FasE = []
        for eeg in eegs:
            Fase = []
            frFas = []
            for i in range(n):
                Fase.append(0)
                frFas.append(0)
            for i in ch:
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                real = fft.real
                imag = fft.imag
                for v in range(len(fft)):
                    # getting the fase for each value of fft
                    fase = np.arctan((imag[v]**2 / real[v]**2))
                    for j in range(n):
                        if abs(fase) > abs(Fase[j]):
                            Fase[j] = fase
                            frFas[j] = v
            FasE.append([Fase, frFas])
        return FasE

    def getMag(self, eegs, n, ch):
        MagE = []
        for eeg in eegs:
            Mag = []
            frMag = []
            for i in range(n):
                Mag.append(0)
                frMag.append(0)
            for i in ch:
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                real = fft.real
                imag = fft.imag
                for v in range(len(fft)):
                    # getting the magnitude for each value of fft
                    magnitude = round(np.sqrt(real[v]**2 + imag[v]**2), 2)
                    for j in range(n):
                        if magnitude > Mag[j]:
                            Mag[j] = magnitude
                            frMag[j] = v
            MagE.append([Mag, frMag])
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