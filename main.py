#local imports
from FileReader import *

fileAddress = raw_input("EEG File to read: ")
reader = FileReader()
eeg = reader.readFile(fileAddress)
print("File Read successfully")
