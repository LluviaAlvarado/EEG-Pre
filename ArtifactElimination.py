#imports
from Utils import msToReading, sampleToMS, ReadEOGS
import numpy as np
from scipy.stats.stats import pearsonr
import scipy.signal as signal
import peakutils
import pywt


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

def autoRemoveECG(icas, f, d):
    # making ECG template
    # The "Daubechies" wavelet is a rough approximation to a real,
    # single, heart beat ("pqrst") signal
    pqrst = signal.wavelets.daub(10)
    # Add the gap after the pqrst when the heart is resting.
    samples_rest = 10
    zero_array = np.zeros(samples_rest, dtype=float)
    pqrst_full = np.concatenate([pqrst, zero_array])
    for ica in icas:
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
        ecg_template = np.tile(pqrst_full, num_heart_beats)
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
                        t = float(sampleToMS(peaks[i + 1], f, d) - sampleToMS(peaks[i], f, d))
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

def autoRemoveBlink(icas, frequency, duration):
    for ica in icas:
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
                    centerMs = sampleToMS(n, frequency, duration)
                    s = msToReading(centerMs - 200, frequency, duration)
                    e = msToReading(centerMs + 200, frequency, duration)
                    nSamp = frequency * duration
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

def autoRemoveMuscular(icas):
    for ica in icas:
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
            x = int(ica.duration) * 2
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


def eliminateArtifacts(eegs, icas):
    i = 0
    for ica in icas:
        ica.recreateSignals()
        eegs[i].SetChannels(ica.getSignals())
        i += 1