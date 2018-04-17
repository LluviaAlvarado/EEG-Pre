import os.path


class Event():
    def __init__(self):
        self.code = None
        self.time = None
        self.precision = None
        self.order = ['time', 'code']

    def __getitem__(self, index):
        """Used for iterating over when writing to file"""
        attval = getattr(self, self.order[index])
        if type(attval) is float:
            if self.order[index] == 'time':
                if self.precision:
                    return '{0:.{1}f}'.format(attval, self.precision)
            return '{:.4f}'.format(attval)
        return str(attval)


class BESAEvent(Event):
    '''Event = time, typecode, code, codestr'''
    def __init__(self, ts, tc, co, cs):
        """Initialise the event based on the raw line"""
        super().__init__()
        try:
            self.time = int(ts)
        except ValueError:
            self.time = float(ts)
        self.typecode = tc
        self.code = int(co)
        self.order = 'time,typecode,code,codestr'.split(',')

    @property
    def codestr(self):
        return 'Trig. ' + str(self.code)


class NeuroscanEvent(Event):
    """Event = evtnum, code, rcode, racc, rlat, time"""
    def __init__(self, en, co, rc, ra, rl, ts):
        super().__init__()
        self.evtnum = int(en)
        self.code = int(co)
        self.rcode = int(rc)
        self.racc = int(ra)
        self.rlat = float(rl)
        try:
            self.time = int(ts)
        except ValueError:
            self.precision = len(ts.split('.')[1])
            self.time = float(ts)
        self.order = 'evtnum,code,rcode,racc,rlat,time'.split(',')


class EventFile:
    """docstring for EventFile"""
    def __init__(self, filename):
        self.source = os.path.abspath(filename)
        self.root, self.ext = os.path.splitext(filename)
        self.raw = self._read()

    def _sniff(self, firstline):
        """Sniff the file type (creating software)"""
        if self.ext == '.evt' and firstline.startswith('Tmu'):
            self.filetype = 'BESA'
            return
        if self.ext == '.ev2':
            self.filetype = 'Neuroscan_2'
            return
        raise ValueError('Undetected type', 'Extension:' + self.ext,
                         'First Line: ' + firstline)

    def _splitBESA(self, lines):
        """Split lines in a BESA specific way"""
        self.header = [h.strip() for h in lines[0].split('\t')]
        if self.header != ['Tmu', 'Code', 'TriNo', 'Comnt']:
            raise ValueError('BESA header format not expected')
        line2 = [d.strip() for d in lines[1].split('\t')]
        if line2[1] == '41':
            self.extra = line2
            self.timestamp = line2[2]
            lines = lines[2:]
        else:
            self.extra = None
            lines = lines[1:]
        self.events = [BESAEvent(*[d.strip() for d in l.split('\t')])
                       for l in lines]

    def _splitNS2(self, lines):
        """split lines in a Neuroscan ev2 specific way"""
        if 'Offset' in lines[0]:
            self.header = [h.strip() for h in lines[0].split()]
            lines = lines[1:]
        else:
            self.header = None
        self.events = [NeuroscanEvent(*[d.strip() for d in l.split()])
                       for l in lines]

    def _split(self, lines):
        """Split lines in a fileformat dependant way and extract header"""
        if self.filetype == 'BESA':
            self._splitBESA(lines)
        elif self.filetype == 'Neuroscan_2':
            self._splitNS2(lines)

    def mod_code(self, linenum, newcode):
        '''Modify the stored event code on linenum to be newcode'''
        self.events[linenum].code = newcode

    def _read(self):
        """Read the text from the event file into memory, sniffing file type
        as we go
        """
        with open(self.source, 'r') as ef:
            lines = ef.read().splitlines()
        self._sniff(lines[0])
        self._split(lines)
        return lines

    def _save(self, appendtext, writemode='x'):
        """Save the current data to file (build from root/ext) and throw error
        if file exists and overwrite == False"""
        with open(self.root + appendtext + self.ext, writemode) as ef:
            if self.filetype == 'BESA':
                ef.write('\t'.join(self.header))
                ef.write('\n')
                if self.extra:
                    ef.write('\t'.join(self.extra))
                    ef.write('\n')
                ef.write('\n'.join(['\t'.join(d) for d in self.events]) + '\n')
                return
            if self.filetype == 'Neuroscan_2':
                if self.header:
                    ef.write('\t'.join(self.header) + '\n')
                ef.write('\n'.join([' '.join(d) for d in self.events]) + '\n')
                return


def load_efile(filepath):
    """Load and return an EventFile object"""
    return EventFile(filepath)


def save_efile(efile, appendtext='_recoded', **kwargs):
    """save the event file with an optional filename append string"""
    efile._save(appendtext, **kwargs)
