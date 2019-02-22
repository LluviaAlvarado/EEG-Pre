import numpy as np
from Utils import sampleToMS


class WindowCharacterization:

    def getMV(self, eegs, ch):
        MVE = []
        # gets the max-min voltaje of eeg and ms when it happened per channel
        for eeg in eegs:
            MV = []
            for i in ch:
                max = np.amax(eeg.channels[i].readings)
                imax = np.argmax(eeg.channels[i].readings)
                msmax = sampleToMS(imax, eeg.frequency, eeg.duration)
                min = np.amin(eeg.channels[i].readings)
                imin = np.argmin(eeg.channels[i].readings)
                msmin = sampleToMS(imin, eeg.frequency, eeg.duration)
                MV.append([[min, msmin], [max, msmax]])
            MVE.append(MV)
        return MVE

    def getFase(self, eegs, n, ch):
        FasE = []
        for eeg in eegs:
            fases = []
            for i in ch:
                Fase = []
                frFas = []
                for i in range(n):
                    Fase.append(0)
                    frFas.append(0)
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
                fases.append([Fase, frFas])
            FasE.append(fases)
        return FasE

    def getMag(self, eegs, n, ch):
        MagE = []
        for eeg in eegs:
            magns = []
            for i in ch:
                Mag = []
                frMag = []
                for i in range(n):
                    Mag.append(0)
                    frMag.append(0)
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
                magns.append([Mag, frMag])
            MagE.append(magns)
        return MagE

    def getAUC(self, eegs, ch):
        AUCE =[]
        for eeg in eegs:
            areas = []
            for i in ch:
                dx = 1
                area = np.trapz(eeg.channels[i].readings, dx=dx)
                areas.append(area)
            AUCE.append(areas)
        return AUCE