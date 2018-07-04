class WindowEEG:
    '''Contains basic info of a window inside and EEG
    that is the length in ms, the Time Before Estimulus
    indicates were the start ms should be calculated also
    in ms and the time of the stimulus in ms as well'''

    def __init__(self, st, len, tbe):
        self.length = len
        self.TBE = tbe
        self.stimulus = st

    # we can only change this value
    def modify(self, tbe, l):
        self.TBE = tbe
        self.length = l