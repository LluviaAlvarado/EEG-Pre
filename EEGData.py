'''
class that contains all the necessary information
from the EEG files
'''
#lib imports
import numpy as np

#local imports
from Channel import *


class EEGData:

    def __init__(self, s, chM, u, f, add):
        sampleData = s
        amUnits = u
        filterHz = f
        additionalData = add
        channelMatrix = chM
        channels = self.fillChannels()
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

    def copyChannel(self, ch):
        #TODO get channel tag and coordinates
        channel = Channel(ch)
        self.channels.append(channel)

    def fillChannels(self):
        self.channels = []
        #iterate channel matrix
        #np.apply_along_axis(self.copyChannel, axis=0, arr=self.channelMatrix)