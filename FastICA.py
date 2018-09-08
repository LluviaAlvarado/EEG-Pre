# imports
import numpy as np
from sklearn.decomposition import FastICA as ICA


class FastICA():
    '''This class implements the Fast ICA algorithm to remove artifacts
       it may do this automatically or the user can select the components
       to remove'''

    def __init__(self, signals, t, auto):
        self.signals = signals
        self.components = []
        self.amUnits = []
        self.duration = t
        self.selectedComponents = []
        self.icaParameters = []
        self.separateComponents()

    # actual FastICA algorithm part 1: just creating matrix of independent components
    def separateComponents(self):
        self.ica = ICA(n_components=len(self.signals[0]))
        self.components = np.matrix.transpose(self.ica.fit_transform(self.signals))
        self.amUnits = [np.amax(self.components), np.amin(self.components)]
        self.selectedComponents = list(range(len(self.components)))

    # recreates signals with the independent components selected
    def recreateSignals(self):
        # modify the mixing matrix so it only adds the selected components
        for i in range(len(self.ica.mixing_)):
            if not self.isSelected(i):
                # turn to 0 all this row
                for j in range(len(self.ica.mixing_[i])):
                    self.ica.mixing_[j][i] = 0
        self.signals = self.ica.inverse_transform(np.matrix.transpose(np.array(self.components)))
        # transposing
        self.signals = np.matrix.transpose(self.signals)

    def isSelected(self, i):
        for selected in self.selectedComponents:
            if i == selected:
                return True
        return False
    # returns the components so user can see them and select manually
    def getComponents(self):
        return self.components

    # sets the components to recreate signals after user selects them
    def setComponents(self, components):
        self.selectedComponents = components

    # returns the signals in there current state
    def getSignals(self):
        return self.signals
