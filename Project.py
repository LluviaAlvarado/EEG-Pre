class Project:
    '''Saves the state of a Project
    with eegs and parameters'''
    def __init__(self):
        self.EEGS = []
        self.name = "new"
        self.frequency = None
        self.duration = None
        self.numCh = None
        self.chLabels = []
        self.windowLength = None
        self.windowTBE = None
        # this is an array:
        # [0] is the csv matrix
        # [1] the path of the csv
        self.windowCSV = None
        self.windowAUC = None
        self.windowFFT = None
        self.windowMaxVolt = None


    def updateWindowInfo(self, l, tbe):
        self.windowLength = l
        self.windowTBE = tbe

    def reset(self):
        self.EEGS = []
        self.frequency = None
        self.duration = None
        self.numCh = None
        self.chLabels = []
        self.windowLength = None
        self.windowTBE = None
        self.windowCSV = None
        self.name = "new"

    def addMany(self, eegs):
        for e in eegs:
            self.EEGS.append(e)