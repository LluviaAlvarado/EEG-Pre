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
        frequency = freq
        duration = time
        filterHz = f
        channelMatrix = chM
        amUnits = [self.channelMatrix.min, self.channelMatrix.max]
        additionalData = add
        channels = self.fillChannels(labels)
        windows = []

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

    def copyChannel(self, ch, label):
        channel = Channel(label, ch)
        self.channels.append(channel)

    def fillChannels(self, labels):
        self.channels = []
        #iterate channel matrix
        np.apply_along_axis(self.copyChannel, 0, self.channelMatrix, labels)
