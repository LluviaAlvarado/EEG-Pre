# imports
import os
from math import ceil

import numpy as np
import peakutils
import pywt
from scipy.stats.stats import pearsonr
from FileReaderWriter import FileReaderWriter
from Utils import msToReading, sampleToMS, ReadEOGS


def autoRemoveEOG(icas):
    for ica in icas:
        # reading EOG patterns
        EOGS = ReadEOGS()
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
                timesEOG = int(sampAdd / len(EOGS[0]))
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
                        pad = [e[i]] * int(abs(sDiff) / len(e))
                        new.extend(pad)
                    newE.append(new)
                EOGS = newE
            elif sDiff > 0:
                newE = []
                for e in EOGS:
                    new = []
                    i = 0
                    while i < len(e):
                        new.append(e[i])
                        i += ceil(len(e) / sDiff)
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
            if abs(mean) > 0.2 or abs(mean2) > 0.2:
                # this is an EOG component
                c = np.array([0.0] * len(c))
            newC.append(c)
        ica.components = newC


def autoRemoveECG(icas):
    path = os.getcwd() + "\\src\\ECG.edf"
    ecg = FileReaderWriter().read_EDF(path)
    duration = ecg.duration
    frequency = ecg.frequency
    ecg = ecg.additionalData[0].readings
    # make ECG same length if icas
    if icas[0].duration != duration:
        diff = icas[0].duration - duration
        if diff < 0:
            # getting just the amount of time
            ecg = ecg[0:int(frequency * icas[0].duration)]
        else:
            # getting just the amount of time and padding samples
            sampAdd = diff * frequency
            timesECG = int(sampAdd / len(ecg))
            aux = ecg
            for i in range(timesECG):
                ecg = np.append(ecg, aux)
        # making same sampling rate
        sDiff = len(ecg) - len(icas[0].components[0])
        if sDiff < 0:
            new = []
            for i in range(len(ecg)):
                new.append(ecg[i])
                pad = [ecg[i]] * int(abs(sDiff) / len(ecg))
                new.extend(pad)
            ecg = new
        elif sDiff > 0:
            new = []
            i = 0
            while i < len(ecg):
                new.append(ecg[i])
                i += ceil(len(ecg) / sDiff)
            ecg = new
        sDiff = len(ecg) - len(icas[0].components[0])
        if sDiff < 0:
            pad = [0] * abs(sDiff)
            try:
                ecg.extend(pad)
            except:
                ecg = np.append(ecg, pad)
        elif sDiff > 0:
            new = ecg[0:int(len(ecg) - sDiff)]
            ecg = new
    for ica in icas:
        f = ica.frequency
        d = ica.duration
        ecg_template = ecg
        # checking correlation
        newC = []
        for c in ica.components:
            correlation = pearsonr(c, ecg_template)
            if abs(correlation[0]) >= 0.6 or abs(correlation[1]) >= 0.6:
                # checking peaks
                dist = len(c) / ica.duration / 2
                peaks = peakutils.indexes(c, min_dist=dist)
                if len(peaks) != 0:
                    # testing periodicity}
                    F = []
                    for i in range(len(peaks) - 1):
                        t = float(sampleToMS(peaks[i + 1], f, d) - sampleToMS(peaks[i], f, d))
                        F.append(1 / (t / 1000))
                    # median frequency of peaks
                    m = np.median(F)
                    # if it is between min and max of heart rate
                    F = np.array(F)
                    N = np.where(np.logical_and(F >= m * 0.75, F <= m * 1.25))
                    if (2 / 3) <= m <= 3:
                        if len(N[0]) >= int(0.7 * m * ica.duration):
                            # this is an ECG component
                            c = np.array([0.0] * len(c))
            newC.append(c)
        ica.components = newC


def autoRemoveBlink(icas):
    waveletLevel = 0
    if len(icas) > 0:
        # getting the level of decomposition for the wavelet transform
        # muscular artifacts appear in the Theta 4-7Hz and Mu 8-12 bands
        frq = icas[0].frequency
        while frq >= 4:
            frq = frq / 2
            waveletLevel += 1
    for ica in icas:
        frequency = ica.frequency
        duration = ica.duration
        newC = []
        for c in ica.components:
            # we need to get up to Ca4 to get to theta band
            Ca= pywt.downcoef('a', c, 'Haar', mode='symmetric', level=waveletLevel)
            # padding to make map to time domain
            new = []
            pad = int((len(c) - len(Ca)) / len(Ca))
            for i in range(len(Ca)):
                new.append(Ca[i])
                for j in range(pad):
                    new.append(Ca[i])
            Ca = np.array(new)
            # getting all negative peaks index in Ca4
            negative = Ca[Ca <= 0]
            maxsNP = []
            for n in negative:
                # checking window of 400ms with eye blink
                centerMs = sampleToMS(n, frequency, duration)
                s = msToReading(centerMs - 200, frequency, duration)
                e = msToReading(centerMs + 200, frequency, duration)
                nSamp = frequency * duration
                if s < 0:
                    s = 0
                if e >= nSamp:
                    e = nSamp - 1
                maxN = 0
                maxI = s
                while s < e:
                    if Ca[s] < maxN:
                        maxN = Ca[s]
                        maxI = s
                    s += 1
                # obtaining the maximum negative peak
                maxsNP.append([maxI, maxN])
            # computing the mean of the maximum negative peaks
            mean = np.sum(maxsNP[:][1]) / len(maxsNP)
            # turning all maximum negative peaks that are above the mean to zero
            for peak in maxsNP:
                if peak[1] < mean:
                    Ca[peak[0]] = 0.0
            # returning Ca to original shape
            ca = []
            for i in range(len(Ca)):
                if i % (pad + 1) == 0:
                    ca.append(Ca[i])
            # applying reverse wavelet
            component = pywt.upcoef('a', ca, 'Haar', level=waveletLevel)
            newC.append(component)
        ica.components = newC


def autoRemoveMuscular(icas):
    waveletLevel = 0
    if len(icas) > 0:
        # getting the level of decomposition for the wavelet transform
        # muscular artifacts appear in the Beta band 16-31Hz
        frq = icas[0].frequency
        while frq >= 16:
            frq = frq / 2
            waveletLevel += 1
    for ica in icas:
        maxs = []
        s1s = []
        s2s = []
        wavelets = []
        for c in ica.components:
            # applying soft thresholding to denoise, removing everything above 50Hz
            c = pywt.threshold(c, 50, 'less')
            # We use the Haar wavelet since it's the most similar to the muscular artifacts
            waveletC = pywt.wavedec(c, 'Haar', level=waveletLevel)
            wavelets.append(waveletC)
            # wavelet[0] = Ca2 wavelet[waveletLevel-1] = Cd2 wavelet[waveletLevel] = Cd1
            # padding Cd2 to make it same length of Cd1
            new = []
            cd2 = waveletC[waveletLevel-1]
            for i in range(len(waveletC[waveletLevel-1])):
                new.append(cd2[i])
                new.append(0.0)
            cd2 = np.array(new)
            # getting the wavelet power spectral density
            # elevating to power 2 the elements of Cd1
            cd1 = np.power(waveletC[waveletLevel], 2)
            # elevating to power 2 the elements of Cd2
            cd2 = np.power(cd2, 2)
            s1 = np.sum(cd1)
            s1s.append(s1)
            s2 = np.sum(cd2)
            s2s.append(s2)
            if s1 > s2:
                maxs.append(s1)
            else:
                maxs.append(s2)
        # getting the mean of all the peaks in the IC
        mean = np.mean(maxs)
        newComponents = []
        for i in range(len(ica.components)):
            if s1s[i] > mean:
                # making all samples zero since it's an EMG artifact
                wavelets[i][waveletLevel][:] = 0.0
            if s2s[i] > mean:
                # making all samples zero since it's an EMG artifact
                wavelets[i][waveletLevel-1][:] = 0.0
            # recreating the component with the inverse wavelet transform
            component = pywt.waverec(wavelets[i], 'Haar')
            newComponents.append(component)
        ica.components = newComponents


def eliminateArtifacts(eegs, icas):
    i = 0
    for ica in icas:
        ica.recreateSignals()
        eegs[i].SetChannels(ica.getSignals())
        i += 1
