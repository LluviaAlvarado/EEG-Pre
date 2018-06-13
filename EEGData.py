'''
class that contains all the necessary information
from the EEG files
'''
#lib imports
import numpy as np

#local imports
from Channel import *
from System10_20 import *
class EEGData:


    def __init__(self, freq, time, chM, f, labels):
        self.system10_20 = System10_20()
        self.i = 0
        self.frequency = freq
        self.duration = time
        self.filterHz = f
        self.channelMatrix = chM
        self.amUnits = [np.amax(self.channelMatrix), np.amin(self.channelMatrix)]
        self.additionalData = []
        self.channels = []
        self.fillChannels(labels)
        self. windows = []

    #adds a WindowEEG object to the list
    def addWindow(self, w):
        self.windows.append(w)

    def windowOverlap(self):
        #TODO check window overlap
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
        #making all labels 10/10 or 10/20 system
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

    def fillChannels(self, labels):
        #iterate channel matrix
        self.i = 0
        np.apply_along_axis(self.copyChannel, 1, self.channelMatrix, labels)

    def getLabels(self):
        lbls = []
        for ch in self.channels:
            lbls.append(ch.label)
        for ex in self.additionalData:
            lbls.append(ex.label)
        return lbls


