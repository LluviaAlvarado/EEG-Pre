class Project:
    '''Saves the state of a Project
    with eegs and parameters'''
    def __init__(self):
        self.EEGS = []
        self.frequency = None
        self.duration = None
        self.numCh = None
        self.chLabels = []
        self.windowLength = None
        #TODO aqui has todo lo que necesites guardar miguel c: y ve como guardarlo en archivo o algo gg