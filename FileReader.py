'''
FileReader can read the next EEG formats:
.mat
.gdf/.edf
.rec
.bci2000
.acq
.eeg
It returns a EEGData object.
'''
#lib imports

#local imports
from EEGData import *

class FileReader:

    def readFile(self, file):
        eeg = EEGData(None, None, None, None, None)
        #TODO leer los diferentes tipos de archivos
        return eeg

