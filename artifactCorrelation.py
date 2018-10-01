#imports
from FileReaderWriter import *
import os
import numpy as np
from copy import deepcopy
from scipy.stats.stats import pearsonr
import csv
from math import ceil


def contaminateEEG(eeg, artifact):
    new = None
    if artifact == 0:
        new = addEOG(eeg)
    elif artifact == 2:
        new = addEMG(eeg)
    elif artifact == 3:
        new = addECG(eeg)
    return new


def addEMG(eeg):
    e = deepcopy(eeg)
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\EMG.edf"
    emg = FileReaderWriter().read_EDF(path)
    duration = emg.duration
    frequency = emg.frequency
    emg = emg.additionalData[2].readings
    # make ECG same length if EEG
    if eeg.duration != duration:
        diff = eeg.duration - duration
        if diff < 0:
            # getting just the amount of time
            # the patterns have a sample rate of 200Hz
            emg = emg.additionalData[0].readings[0:int(emg.frequency * eeg.duration)]
        else:
            # getting just the amount of time and padding samples
            # the patterns have a sample rate of 200Hz
            sampAdd = diff * frequency
            timesEMG = int(sampAdd / len(emg))
            aux = emg
            for i in range(timesEMG):
                emg = np.append(emg, aux)
        # making same sampling rate
        sDiff = len(emg) - len(eeg.channels[0].readings)
        if sDiff < 0:
            new = []
            for i in range(len(emg)):
                new.append(emg[i])
                pad = [emg[i]] * int(abs(sDiff) / len(emg))
                new.extend(pad)
            emg = new
        elif sDiff > 0:
            new = []
            i = 0
            while i < len(emg):
                new.append(emg[i])
                i += ceil(len(emg) / sDiff)
            emg = new
        sDiff = len(emg) - len(eeg.channels[0].readings)
        if sDiff < 0:
            pad = [0] * abs(sDiff)
            try:
                emg.extend(pad)
            except:
                emg = np.append(emg, pad)
        elif sDiff > 0:
            new = emg[0:int(len(emg) - sDiff)]
            emg = new
    incPond = 1 / (len(e.channels)/2)
    pond = 0
    signal = np.array(emg).astype('float64')
    for i in range(len(e.channels)):
        s = signal * pond
        e.channels[i].readings = np.add(e.channels[i].readings, s)
        if i <= (len(e.channels)/2):
            pond += incPond
        else:
            pond -= incPond
    e.name = eeg.name + "_EMGcontaminated"
    return e


def addECG(eeg):
    e = deepcopy(eeg)
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\ECG.edf"
    ecg = FileReaderWriter().read_EDF(path)
    duration = ecg.duration
    frequency = ecg.frequency
    ecg = ecg.additionalData[0].readings
    # make ECG same length if EEG
    if eeg.duration != duration:
        diff = eeg.duration - duration
        if diff < 0:
            # getting just the amount of time
            ecg = ecg.additionalData[0].readings[0:int(ecg.frequency * eeg.duration)]
        else:
            # getting just the amount of time and padding samples
            sampAdd = diff * frequency
            timesECG = int(sampAdd / len(ecg))
            aux = ecg
            for i in range(timesECG):
                ecg = np.append(ecg, aux)
        # making same sampling rate
        sDiff = len(ecg) - len(eeg.channels[0].readings)
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
        sDiff = len(ecg) - len(eeg.channels[0].readings)
        if sDiff < 0:
            pad = [0] * abs(sDiff)
            try:
                ecg.extend(pad)
            except:
                ecg = np.append(ecg, pad)
        elif sDiff > 0:
            new = ecg[0:int(len(ecg) - sDiff)]
            ecg = new
    incPond = 1 / (len(e.channels) / 2)
    pond = 0
    signal = np.array(ecg).astype('float64')
    for i in range(len(e.channels)):
        s = signal * pond
        e.channels[i].readings = np.add(e.channels[i].readings, s)
        if i <= (len(e.channels) / 2):
            pond += incPond
        else:
            pond -= incPond
    e.name = eeg.name + "_ECGcontaminated"
    return e


def addEOG(eeg):
    e = deepcopy(eeg)
    path = os.getcwd() + "\\src\\EOG\\heog_4.csv"
    eog = None
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            eog = row[0:int(len(row) - 1)]
    # make EOG same length of eeg, the patterns are 30s long
    if eeg.duration != 30:
        diff = eeg.duration - 30
        if diff < 0:
            # getting just the amount of time
            # the patterns have a sample rate of 200Hz
            eog = eog[0:int(200 * eeg.duration)]
        else:
            # getting just the amount of time and padding samples
            # the patterns have a sample rate of 200Hz
            sampAdd = diff * 200
            timesEOG = int(sampAdd / len(eog))
            aux = eog
            for i in range(timesEOG):
                eog = np.append(eog, aux)
        # making same sampling rate
        sDiff = len(eog) - len(eeg.channels[0].readings)
        if sDiff < 0:
            new = []
            for i in range(len(eog)):
                new.append(eog[i])
                pad = [eog[i]] * int(abs(sDiff) / len(eog))
                new.extend(pad)
            eog = new
        elif sDiff > 0:
            new = []
            i = 0
            while i < len(eog):
                new.append(eog[i])
                i += ceil(len(eog) / sDiff)
            eog = new
        sDiff = len(eog) - len(eeg.channels[0].readings)
        if sDiff < 0:
            pad = [0] * abs(sDiff)
            eog.extend(pad)
        elif sDiff > 0:
            new = eog[0:int(len(eog) - sDiff)]
            eog = new
    # contaminating
    incPond = 1 / (len(e.channels) / 2)
    pond = 0
    signal = np.array(eog).astype('float64')
    for i in range(len(e.channels)):
        s = signal * pond
        e.channels[i].readings = np.add(e.channels[i].readings, s)
        if i <= (len(e.channels) / 2):
            pond += incPond
        else:
            pond -= incPond
    e.name = eeg.name + "_EOGcontaminated"
    return e


def correlate(eeg1, eeg2):
    mean1 = 0.0
    mean2 = 0.0
    i = 0
    for i in range(len(eeg1.channels)):
        corr = pearsonr(np.array(eeg1.channels[i].readings), np.array(eeg2.channels[i].readings))
        mean1 += corr[0]
        mean2 += corr[1]
    mean1 /= i+1
    mean2 /= i+1
    correlation = [mean1, mean2]
    return correlation
