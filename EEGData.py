'''class that contains all the necessary information
from the EEG files'''
# lib imports
import numpy as np
from copy import deepcopy
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

    def setSelected(self, sel):
        self.selectedCh = sel

    def SaveState(self):
        self.prev = deepcopy(self)

    def getChannel(self, i):
        if i < len(self.channels):
            return self.channels[i]
        else:
            try:
                return self.additionalData[i]
            except:
                return None

    def setName(self, na):
        self.name = na

    # adds a WindowEEG object to the list
    def addWindow(self, w):
        self.windows.append(w)

    # adds windows loaded by a csv
    def addMultipleWindows(self, windows, l, tbe):
        for st in windows:
            # avoid white space
            if st != '':
                window = WindowEEG(int(st), int(l), int(tbe), self)
                self.windows.append(window)

    def removeWindow(self, i):
        self.windows.remove(self.windows[i])

    def windowOverlap(self):
        # TODO check window overlap
        return False

    def concatenateWindows(self):
        concatenated = EEGData()
        concatenated.filter = self.filter
        # TODO concatenate windows
        return concatenated

    def createConcatenatedEEG(self):
        new = None
        if not self.windowOverlap():
            new = self.concatenateWindows()
        return new

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
        for signal in signals:
            if i < len(self.channels):
                self.channels[i].readings = signal
            else:
                self.additionalData[i].readings = signal
            i += 1