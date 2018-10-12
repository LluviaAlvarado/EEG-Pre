class WindowEEG:
    """Contains basic info of a window inside and EEG
    that is the length in ms, the Time Before Estimulus
    indicates were the start ms should be calculated also
    in ms and the time of the stimulus in ms as well"""

    def __init__(self, st, length, tbe, eeg):
        self.length = length
        self.TBE = tbe
        self.stimulus = st
        # contains the readings of the selected channels just for this window
        self.readings = self.fillReadings(eeg)

    def GetSE(self):
        start = self.stimulus - self.TBE
        end = start + self.length
        return start, end

    def GetReadsUpTo(self, e):
        frequency = len(self.readings) / self.length
        start = self.stimulus - self.TBE
        e = int((e - start)*frequency)
        return self.readings[0:e]

    def fillReadings(self, eeg):
        readings = []
        for ch in eeg.channels:
            # ms to reading
            start = self.stimulus - self.TBE
            totalReadings = eeg.duration * eeg.frequency
            end = start + self.length
            srd = int((start * totalReadings) / (eeg.duration * 1000))
            erd = int((end * totalReadings) / (eeg.duration * 1000))
            row = []
            for i in range(srd, erd):
                row.append(ch.readings[i])
            readings.append(row)
        return readings

    # we can only change this value
    def modify(self, tbe, l, eeg):
        self.TBE = tbe
        self.length = l
        self.fillReadings(eeg)
