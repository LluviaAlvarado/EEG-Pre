#imports
from FileReaderWriter import *
import os
import numpy as np

def contamineteEEG(eeg, artifact):
    new = None
    if artifact == 0:
        new = addEMG(eeg)
    elif artifact == 1:
        new = addECG(eeg)
    elif artifact == 2:
        new = addEOG(eeg)
    return new

def addEMG(eeg):
    e = None
    path = os.getcwd() + "\\TestFiles\\gdf_edf\\EMG.edf"
    emg = FileReaderWriter().read_EDF(path)

    return e


def addECG(eeg):
    e = None

    return e


def addEOG(eeg):
    e = None

    return e

def correlate(eeg, artifact):
    correlation = -1
    if artifact == 0:
        correlation = corrEMG(eeg)
    elif artifact == 1:
        correlation = corrECG(eeg)
    elif artifact == 2:
        correlation = corrEOG(eeg)
    return correlation

def corrEMG(eeg):
    corr = -1

    return corr


def corrECG(eeg):
    corr = -1

    return corr

def corrEOG(eeg):
    corr = -1

    return corr
