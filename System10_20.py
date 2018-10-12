# imports
import re

'''Checks the labels se to electrodes in EEG
   and converts them to standard 10/20 if possible'''


class System10_20:

    def __init__(self):
        self.regularExpressions = []
        self.regularExpressions.append('NZ')
        self.regularExpressions.append('Fp1')
        self.regularExpressions.append('FpZ')
        self.regularExpressions.append('Fp2')
        self.regularExpressions.append('AF7')
        self.regularExpressions.append('AF3')
        self.regularExpressions.append('AFZ')
        self.regularExpressions.append('AF4')
        self.regularExpressions.append('AF8')
        self.regularExpressions.append('F9')
        self.regularExpressions.append('F7')
        self.regularExpressions.append('F5')
        self.regularExpressions.append('F3')
        self.regularExpressions.append('F1')
        self.regularExpressions.append('Fz')
        self.regularExpressions.append('F2')
        self.regularExpressions.append('F4')
        self.regularExpressions.append('F6')
        self.regularExpressions.append('F8')
        self.regularExpressions.append('F10')
        self.regularExpressions.append('FT9')
        self.regularExpressions.append('FT7')
        self.regularExpressions.append('FC5')
        self.regularExpressions.append('FC3')
        self.regularExpressions.append('FC1')
        self.regularExpressions.append('FCZ')
        self.regularExpressions.append('FC2')
        self.regularExpressions.append('FC4')
        self.regularExpressions.append('FC6')
        self.regularExpressions.append('FC8')
        self.regularExpressions.append('FC10')
        self.regularExpressions.append('A1')
        self.regularExpressions.append('T9')
        self.regularExpressions.append('T7')
        self.regularExpressions.append('T5')
        self.regularExpressions.append('T3')
        self.regularExpressions.append('C5')
        self.regularExpressions.append('C3')
        self.regularExpressions.append('C1')
        self.regularExpressions.append('Cz')
        self.regularExpressions.append('C2')
        self.regularExpressions.append('C4')
        self.regularExpressions.append('C6')
        self.regularExpressions.append('T4')
        self.regularExpressions.append('T6')
        self.regularExpressions.append('T8')
        self.regularExpressions.append('T10')
        self.regularExpressions.append('A2')
        self.regularExpressions.append('TP9')
        self.regularExpressions.append('TP7')
        self.regularExpressions.append('CP5')
        self.regularExpressions.append('CP3')
        self.regularExpressions.append('CP1')
        self.regularExpressions.append('CPZ')
        self.regularExpressions.append('CP2')
        self.regularExpressions.append('CP4')
        self.regularExpressions.append('CP6')
        self.regularExpressions.append('CP8')
        self.regularExpressions.append('CP10')
        self.regularExpressions.append('P9')
        self.regularExpressions.append('P7')
        self.regularExpressions.append('P5')
        self.regularExpressions.append('P3')
        self.regularExpressions.append('P1')
        self.regularExpressions.append('Pz')
        self.regularExpressions.append('P2')
        self.regularExpressions.append('P4')
        self.regularExpressions.append('P6')
        self.regularExpressions.append('P8')
        self.regularExpressions.append('P10')
        self.regularExpressions.append('PO7')
        self.regularExpressions.append('PO3')
        self.regularExpressions.append('POZ')
        self.regularExpressions.append('PO4')
        self.regularExpressions.append('PO8')
        self.regularExpressions.append('O1')
        self.regularExpressions.append('OZ')
        self.regularExpressions.append('O2')
        self.regularExpressions.append('IZ')

    def testLabel(self, lbl):
        for rex in self.regularExpressions:
            ex = re.compile(rex, re.IGNORECASE)
            res = ex.search(lbl)
            if res is not None:
                return rex
        return None
