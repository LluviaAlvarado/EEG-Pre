# imports
import numpy as np
from sklearn.decomposition import FastICA

class FastICA():

    '''This class implements the Fast ICA algorithm to remove artifacts
       it may do this automatically or the user can select the components
       to remove'''

    def __init__(self, signals, auto):
        self.signals = signals
        self.components = []
        self.icaParameters = []
        self.separateComponents()
        # this removes the components that are artifactual
        if auto:
            self.autoSelectComponents()
            self.recreateSignals()

    # actual FastICA algorithm part 1: just creating matrix of independent components
    def separateComponents(self):
        ica = FastICA(len(self.signals))
        A = ica.mixing_  # Get estimated mixing matrix
        X = np.dot(self.signals, A.T)  # Generate observations
        components = ica.fit_transform(X)  # Reconstruct signals
        self.components = components
        self.icaParameters.append([A, X, ica])

    def autoSelectComponents(self):
        # TODO como identificarlos :'v?
        return

    # recreates signals with the independent components selected
    def recreateSignals(self):
        signals = []
        i = 0
        for components in self.components:
            params = self.icaParameters[i]
            assert np.allclose(params[1], np.dot(components, params[0].T) + params[2].mean_)
            i += 1

    # returns the components so user can see them and select manually
    def getComponents(self):
        return self.components

    # sets the components to recreate signals after user selects them
    def setComponents(self, components):
        self.components = components

    # returns the signals in there current state
    def getSignals(self):
        return self.signals
