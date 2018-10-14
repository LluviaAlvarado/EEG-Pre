'''class that contains all the necessary information
from the EEG files'''
# lib imports
import numpy as np
from copy import deepcopy, copy
# local imports
from Channel import *
from System10_20 import *
from WindowEEG import *


class EEGData:

    def __init__(self, freq, time, chM, f, labels):
        self.name = ""
        self.system10_20 = System10_20()
        self.i = 0
        # sample frequency
        self.frequency = freq
        self.duration = time
        self.filterHz = f
        self.amUnits = [np.amax(chM), np.amin(chM)]
        self.additionalData = []
        self.channels = []
        self.fillChannels(labels, chM)
        self.selectedCh = list(range(0, len(self.channels) + len(self.additionalData)))
        self. windows = []
        self.prev = None

    def clear(self):
        self.name = ""
        self.system10_20 = System10_20()
        self.frequency = 0
        self.duration = 0
        self.filterHz = 0
        self.amUnits = [0, 0]
        self.additionalData = []
        self.channels =[]
        self.windows = []
        self.prev = None

    def setSelected(self, sel):
        self.selectedCh = sel

    def SaveState(self):
        self.prev = deepcopy(self)

    def setSaveState(self, eeg):
        self.prev = eeg

    def getChannel(self, i):
        if i < len(self.channels):
            return self.channels[i]
        else:
            try:
                if len(self.channels) == 0:
                    return self.additionalData[i]
                else:
                    return self.additionalData[i - len(self.channels)]
            except:
                return None

    def setName(self, na):
        self.name = na

    # adds a WindowEEG object to the list
    def addWindow(self, w):
        self.windows.append(w)

    def SortWindows(self):
        if len(self.windows) > 1:
            # orders windows from shortest time to longer
            w = []
            i = 0
            dtype = [('idx', int), ('start', float)]
            for win in self.windows:
                start, end = win.GetSE()
                w.append((i, start))
                i += 1
            w = np.array(w, dtype=dtype)
            w = np.sort(w, order='start')
            aux = []
            for i in range(len(w)):
                idx = w[i]['idx']
                aux.append(self.windows[idx])
            self.windows = aux

    # adds windows loaded by a csv
    def addMultipleWindows(self, windows, l, tbe):
        for st in windows:
            # avoid white space
            if st != '':
                window = WindowEEG(int(st), int(l), int(tbe), self)
                self.windows.append(window)

    def removeWindow(self, i):
        self.windows.remove(self.windows[i])

    def concatenateWindows(self):
        if len(self.windows) == 0:
            return self
        self.SortWindows()
        channels = []
        for ch in self.channels:
            channels.append(Channel(ch.label, []))
        if len(self.windows) == 1:
            for i in range(len(channels)):
                reads = self.windows[0].readings[i]
                channels[i].readings.extend(reads)
        else:
            for w in range(len(self.windows)-1):
                for i in range(len(channels)):
                    reads = self.windows[w].readings[i]
                    start, end = self.windows[w].GetSE()
                    s, e = self.windows[w+1].GetSE()
                    if start <= s <= end:
                        # there's overlapping
                        reads = self.windows[w].GetReadsUpTo(s)
                    channels[i].readings.extend(reads)
        concatenated = copy(self)
        concatenated.channels = channels
        concatenated.duration = len(channels[0].readings) / self.frequency
        return concatenated

    def copyChannel(self, ch, labels):
        # making all labels 10/1 or 10/20 system
        label = self.system10_20.testLabel(labels[self.i])
        if label is None:
            '''This a label not in the system so we add
            it as additional information'''
            channel = Channel(labels[self.i], ch)
            self.additionalData.append(channel)
        else:
            channel = Channel(label, ch)
            self.channels.append(channel)
        self.i += 1

    def fillChannels(self, labels, chM):
        # iterate channel matrix
        self.i = 0
        np.apply_along_axis(self.copyChannel, 1, chM, labels)

    def getLabels(self):
        lbls = []
        for ch in self.channels:
            lbls.append(ch.label)
        for ex in self.additionalData:
            lbls.append(ex.label)
        return lbls

    def getChannelLabels(self):
        lbls = []
        for ch in self.channels:
            lbls.append(ch.label)
        return lbls

    def sameLabels(self, test):
        different = 0
        equal = False
        chans = self.channels
        for ts in test:
            for ch in chans:
                if ch.label == ts.label:
                    equal = True
            if not equal:
                different += 1
            equal = False
        if different > 0:
            return False
        return True

    def sameLabelsCh(self, labels):
        different = 0
        equal = False
        chans = self.channels
        for ts in labels:
            for ch in chans:
                if ch.label == ts:
                    equal = True
            if not equal:
                different += 1
            equal = False
        if different > 0:
            return False
        return True

    def sameProject(self, test):
        if test.frequency != self.frequency:
            return "Frequency"
        if test.duration != self.duration:
            return "Duration"
        if len(test.channels) != len(self.channels):
            return "Number of Channels"
        if not self.sameLabels(test.channels):
            return "Channel Names"
        return ""

    # sets channels after applying fastICA
    def SetChannels(self, signals):
        i = 0
        j = 0
        for signal in signals:
            if i < len(self.channels):
                self.channels[i].readings = signal
            else:
                self.additionalData[j].readings = signal
                j += 1
            i += 1
