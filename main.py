#local imports
from FileReader import *

fileAddress = raw_input("EEG File to read: ")
reader = FileReader()
eeg = reader.readFile(fileAddress)
if not reader.hasError():
    print("File Read Successfully!")
