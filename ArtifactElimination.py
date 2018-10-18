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


def autoRemoveECG(icas, f, d):
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
            ecg = ecg.additionalData[0].readings[0:int(ecg.frequency * icas[0].duration)]
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


def autoRemoveBlink(icas, frequency, duration):
    for ica in icas:
        newC = []
        for c in ica.components:
            # we need to get up to Ca4 to get to theta band
            Ca4 = pywt.downcoef('a', c, 'Haar', mode='symmetric', level=4)
            # padding to make map to time domain
            new = []
            pad = int((len(c) - len(Ca4)) / len(Ca4))
            for i in range(len(Ca4)):
                new.append(Ca4[i])
                for j in range(pad):
                    new.append(Ca4[i])
            Ca4 = np.array(new)
            # computing the mean of the negative values
            neg = Ca4[Ca4 <= 0]
            mean = np.sum(neg) / len(neg)
            # getting all negative peaks index in Ca4
            negative = []
            for i in range(len(Ca4)):
                if Ca4[i] < mean:
                    negative.append(i)
            # deciding if we remove
            for n in negative:
                # remove window of 400ms with eye blink
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
                    if Ca4[s] < maxN:
                        maxN = Ca4[s]
                        maxI = s
                    s += 1
                # the maximum negative peak is turned to 0
                Ca4[maxI] = 0.0
            # returning Ca4 to original shape
            ca = []
            for i in range(len(Ca4)):
                if i % (pad + 1) == 0:
                    ca.append(Ca4[i])
            # applying reverse wavelet
            component = pywt.upcoef('a', ca, 'Haar', level=4)
            newC.append(component)
        ica.components = newC


def autoRemoveMuscular(icas):
    for ica in icas:
        ss = []
        for c in ica.components:
            # applying soft thresholding to denoise, removing everything above 50Hz
            c = pywt.threshold(c, 50, 'less')
            waveletC = pywt.wavedec(c, 'Haar', level=6)
            # wavelet[0] = Ca2 wavelet[1] = Cd2 wavelet[2] = Cd1
            # padding Cd2 to make it same length of Cd1
            new = []
            cd2 = waveletC[1]
            for i in range(len(waveletC[1])):
                new.append(cd2[i])
                new.append(0.0)
            waveletC[1] = np.array(new)
            # getting the wavelet power spectral density
            # elevating to power 2 the elements of Cd1
            cd1 = np.power(waveletC[2], 2)
            # elevating to power 2 the elements of Cd2
            cd2 = np.power(waveletC[1], 2)
            s1 = np.sum(cd1)
            s2 = np.sum(cd2)
            if s1 > s2:
                ss.append(s1)
            else:
                ss.append(s2)
        for i in range(len(ica.components)):
            if ss[i] > 0.2:
                # this is an EMG artifact
                ica.components[i] = np.array([0.0] * len(ica.components[i]))


def eliminateArtifacts(eegs, icas):
    i = 0
    for ica in icas:
        ica.recreateSignals()
        eegs[i].SetChannels(ica.getSignals())
        i += 1
