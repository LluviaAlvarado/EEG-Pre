import csv
from os import listdir, getcwd, remove
from os.path import isfile, join
import wx
from FileReaderWriter import FileReaderWriter
from copy import copy, deepcopy


# changes the value for printable purposes
def ChangeRange(v, ou, ol, nu, nl):
    # v is the value to change range, old upper, old lower, new upper and new lower
    oldRange = ou - ol
    newRange = nu - nl
    return round((((v - ol) * newRange) / oldRange) + nl, 2)


def sampleToMS(s, frequency, duration):
    # s is te sample to convert to ms
    # frequency is the sample frequency of the project and duration of the project
    nSamp = frequency * duration
    return ((duration * 1000) * s) / nSamp


def frequencyToSample(fr, frequency, duration):
    # bit reversal to get the actual sample
    return int('{:32b}'.format(fr)[::-1], 2)

def msToReading(ms, frequency, duration):
    # ms is te sample to convert to sample/reading
    # frequency is the sample frequency of the project and duration of the project
    nSamp = frequency * duration
    return int((ms * nSamp) / (duration * 1000))


def ReadEOGS():
    # let's read the EOGS saved in .csv
    p = getcwd() + "\\src\\EOG\\"
    paths = [f for f in listdir(p) if isfile(join(p, f))]
    csv = []
    for path in paths:
        if ".csv" in path:
            csv.append(readEOGSCSV(p + "\\" + path))
    return csv


def readEOGSCSV(path):
    r = []
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            r = row[0:int(len(row) - 1)]
    return r


def exportEEGS(project, eegs):
    pathPicker = wx.DirDialog(None, "Exportar en:", getcwd(),
                             wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    if pathPicker.ShowModal() != wx.ID_CANCEL:
        writer = FileReaderWriter()
        windows = []
        windowsExist = False
        for eeg in eegs:
            writer.writeFile(eeg, project.name, pathPicker.GetPath())
            if len(eeg.windows) > 0:
                windowsExist = True
            windows.append([eeg.name, eeg.windows])
        # exporting csv with window information and a txt with the TBE and length in ms
        if windowsExist:
            writeWindowFiles(project, windows, pathPicker.GetPath())


def writeWindowFiles(project, windows, path):
    file = path + "\\" + project.name + "_windows.csv"
    txt = path + "\\" + project.name + "_windows.txt"
    if isfile(file):
        # it already exists
        f = project.name + "_windows.csv"
        msg = wx.MessageDialog(None, "El archivo '" + f + "' ya existe. "
                            "\n¿Desea reemplazar el archivo?", caption="¡Alerta!",
                            style=wx.YES_NO | wx.CENTRE)
        if msg.ShowModal() == wx.ID_NO:
            return  # we don't to anything
        else:
            # deleting the prev file and txt
            remove(file)
            remove(txt)
    # writing windowFiles
    FileReaderWriter().writeWindowFiles(windows, file, txt, project.windowLength, project.windowTBE)


def eegs_copy(eegs, tmp):
    copy_eegs = []
    if tmp != None:
        tmp.clear()
        copy_eegs = []
        for eeg in eegs:
            copy_eegs.append(eeg_copy(eeg, tmp))
    return copy_eegs


def eeg_copy(eeg, tmp):
    copi = copy(tmp)
    copy_eeg = copy(eeg)
    channels = []
    for i in copy_eeg.channels:
        channels.append(copy(i))
    copi.channels = channels
    windows = []
    for w in copy_eeg.windows:
        windows.append(copy(w))
    additional = []
    for i in copy_eeg.additionalData:
        additional.append(copy(i))
    copi.additionalData = additional
    copi.windows = windows
    copi.amUnits = copy_eeg.amUnits
    copi.duration = copy_eeg.duration
    copi.filterHz = copy_eeg.filterHz
    copi.frequency = copy_eeg.frequency
    copi.name = copy_eeg.name
    copi.prev = copy_eeg.prev
    return copi