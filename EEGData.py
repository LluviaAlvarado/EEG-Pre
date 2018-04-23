'''
class that contains all the necessary information
from the EEG files
'''
#lib imports
import numpy as np

#local imports
from Channel import *


class EEGData:

    def __init__(self, freq, time, chM, f, add, labels):
        self.frequency = freq
        self.duration = time
        self.filterHz = f
        self.channelMatrix = chM
        self.amUnits = [np.amax(self.channelMatrix), np.amin(self.channelMatrix)]
        self.additionalData = add
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

    def copyChannel(self, ch, i, label):
        channel = Channel(label[i], ch)
        i += 1
        self.channels.append(channel)

    def fillChannels(self, labels):
        #iterate channel matrix
        i = 0
        np.apply_along_axis(self.copyChannel, 1, self.channelMatrix, i, labels)