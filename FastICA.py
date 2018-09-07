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
        # this removes the components that are artifactual
        if auto:
            self.autoSelectComponents()
            self.recreateSignals()

    # actual FastICA algorithm part 1: just creating matrix of independent components
    def separateComponents(self):
        self.ica = ICA(n_components=len(self.signals[0]))
        self.components = np.matrix.transpose(self.ica.fit_transform(self.signals))
        #self.components = self.ica.components_  # Reconstruct signals
        self.amUnits = [np.amax(self.components), np.amin(self.components)]

    def autoSelectComponents(self):
        # TODO como identificarlos :'v?
        return

    # recreates signals with the independent components selected
    def recreateSignals(self):
        components = []
        for selected in self.selectedComponents:
            components.append(self.components[selected])
        self.signals = self.ica.transform(components)

    # returns the components so user can see them and select manually
    def getComponents(self):
        return self.components

    # sets the components to recreate signals after user selects them
    def setComponents(self, components):
        self.selectedComponents = components

    # returns the signals in there current state
    def getSignals(self):
        return self.signals
