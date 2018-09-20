#imports
from FileReaderWriter import *
import os
import numpy as np
import copy
from scipy.stats.stats import pearsonr
import csv


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
    e = copy.deepcopy(eeg)
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\EMG.edf"
    emg = FileReaderWriter().read_EDF(path)
    # adapting to eeg length
    l = e.duration
    x = l * emg.frequency
    el = emg.duration * emg.frequency
    i = int(el * 0.8 - x/2)
    f = int(i + x)
    s = emg.additionalData[2].readings[i:f]
    # make same sample frequency
    signal = []
    diff = int(len(e.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(e.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal)-1]] * int(diff)
        signal.extend(pad)
    incPond = 1 / (len(e.channels)/2)
    pond = 0
    signal = np.array(signal)
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
    e = copy.deepcopy(eeg)
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\ECG.edf"
    ecg = FileReaderWriter().read_EDF(path)
    # adapting to eeg length
    l = e.duration
    x = int(l * ecg.frequency)
    el = ecg.duration * ecg.frequency
    i = int(el * 0.5 - x / 2)
    f = int(i + x)
    s = ecg.additionalData[0].readings[0:x]
    # make same sample frequency
    signal = []
    diff = int(len(e.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(e.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal) - 1]] * int(diff)
        signal.extend(pad)
    incPond = 1 / (len(e.channels) / 2)
    pond = 0
    signal = np.array(signal)
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
    e = copy.deepcopy(eeg)
    path = os.getcwd() + "\\src\\EOG\\heog_4.csv"
    eog = None
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            eog = row[0:int(len(row) - 1)]
    # adapting to eeg length
    s = eog[0:int(200 * eeg.duration)]
    # make same sample frequency
    signal = []
    diff = int(len(e.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(e.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal) - 1]] * int(diff)
        signal.extend(pad)
    incPond = 1 / (len(e.channels) / 2)
    pond = 0
    signal = np.array(signal).astype('float64')
    for i in range(len(e.channels)):
        s = signal * pond
        e.channels[i].readings = np.add(e.channels[i].readings, s)
        if i <= (len(e.channels) / 2):
            pond += incPond
        else:
            pond -= incPond
    e.name = eeg.name + "_EOGcontaminated"
    return e


def correlate(eeg, artifact):
    correlation = -1
    if artifact == 0:
        correlation = corrEOG(eeg)
    elif artifact == 2:
        correlation = corrEMG(eeg)
    elif artifact == 3:
        correlation = corrECG(eeg)
    return correlation


def corrEMG(eeg):
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\EMG.edf"
    emg = FileReaderWriter().read_EDF(path)
    # adapting to eeg length
    l = eeg.duration
    x = l * emg.frequency
    el = emg.duration * emg.frequency
    i = int(el * 0.8 - x/2)
    f = int(i + x)
    s = emg.additionalData[2].readings[i:f]
    # make same sample frequency
    signal = []
    diff = int(len(eeg.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(eeg.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal) - 1]] * int(diff)
        signal.extend(pad)
    mean = 0
    mean2 = 0
    for c in eeg.channels:
        correlation = pearsonr(np.array(c.readings), np.array(signal))
        mean += correlation[0]
        mean2 += correlation[1]
    mean = mean / len(eeg.channels)
    mean2 = mean2 / len(eeg.channels)
    if abs(mean) > abs(mean2):
        return mean
    return mean2


def corrECG(eeg):
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\ECG.edf"
    ecg = FileReaderWriter().read_EDF(path)
    # adapting to eeg length
    l = eeg.duration
    x = int(l * ecg.frequency)
    el = ecg.duration * ecg.frequency
    i = int(el * 0.5 - x / 2)
    f = int(i + x)
    s = ecg.additionalData[0].readings[0:x]
    # make same sample frequency
    signal = []
    diff = int(len(eeg.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(eeg.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal) - 1]] * int(diff)
        signal.extend(pad)
    mean = 0
    mean2 = 0
    for c in eeg.channels:
        correlation = pearsonr(np.array(c.readings), np.array(signal))
        mean += correlation[0]
        mean2 += correlation[1]
    mean = mean / len(eeg.channels)
    mean2 = mean2 / len(eeg.channels)
    if abs(mean) > abs(mean2):
        return mean
    return mean2

def corrEOG(eeg):
    path = os.getcwd() + "\\src\\EOG\\heog_4.csv"
    eog = None
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            eog = row[0:int(len(row) - 1)]
    # adapting to eeg length
    s = eog[0:int(200 * eeg.duration)]
    # make same sample frequency
    signal = []
    diff = int(len(eeg.channels[0].readings) - len(s))
    for v in s:
        pad = [v] * (int(diff / len(s)) + 1)
        signal.extend(pad)
    diff = int(len(eeg.channels[0].readings) - len(signal))
    if diff != 0:
        pad = [signal[len(signal) - 1]] * int(diff)
        signal.extend(pad)
    signal = np.array(signal).astype('float64')
    mean = 0
    mean2 = 0
    for c in eeg.channels:
        correlation = pearsonr(np.array(c.readings), np.array(signal))
        mean += correlation[0]
        mean2 += correlation[1]
    mean = mean / len(eeg.channels)
    mean2 = mean2 / len(eeg.channels)
    if abs(mean) > abs(mean2):
        return mean
    return mean2
