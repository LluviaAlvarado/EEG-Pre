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

    def getMagFase(self, eegs, n, ch):
        MagFase = []
        for eeg in eegs:
            Mag = []
            frequency = []
            Fase = []
            for i in range(n):
                Mag.append(0)
                frequency.append(0)
                Fase.append(0)
            for i in ch:
                fft = np.fft.rfft(eeg.channels[i].readings, len(eeg.channels[i].readings))
                # normalizing
                real = (fft.real * 2) / len(eeg.channels[i].readings)
                imag = (fft.imag * 2) / len(eeg.channels[i].readings)
                for v in range(len(fft)):
                    # getting the magnitude for each value of fft
                    magnitude = round(np.sqrt(real[v]**2 + imag[v]**2), 2)
                    # getting the fase for each value of fft
                    fase = np.arctan((imag[v] ** 2 / real[v] ** 2))
                    for j in range(n):
                        if magnitude > Mag[j]:
                            Mag[j] = magnitude
                            frequency[j] = v
                            Fase[j] = fase
            MagFase.append([Mag, frequency, Fase])
        return MagFase

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