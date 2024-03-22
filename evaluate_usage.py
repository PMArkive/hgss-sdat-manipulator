#!/usr/bin/python3

import os



############ CREATE SSEQ TO BANK/BANK TO SWAR DICTIONARY ############



UsageFile = open("usage.txt")

UsageDict = {}
SEQDict = {}
BankDict = {}

seqCount = 0
bankCount = 1

for line in UsageFile:
    if line.startswith("SEQ_"):
        UsageDict[line.split(" uses ")[0].strip()] = line.split(" uses ")[1].strip()
        SEQDict[seqCount] = line.split(" uses ")[0].strip()
        seqCount += 1
    elif line.startswith("BANK_"):
        UsageDict[line.split(" uses ")[0].strip()] = line.split(" uses ")[1].strip().strip("[").strip("]").split(",")
        BankDict[line.split(" uses ")[0].strip()] = bankCount
        bankCount += 1
        if (bankCount == 495):
            bankCount += 700-495
        if (bankCount == 739):
            bankCount += 750-739

UsageFile.close()



############ CREATE SSEQ TO INSTRUMENT DICTIONARY ############



InstrFile = open("SMFT_Program_Uses.txt")

currentFile = ""
SEQToInstrDict = {}

for line in InstrFile:
    if line.startswith("File:"):
        currentFile = line.strip().strip("File: ").strip(".smft")
    elif line.startswith("Program"):
        SEQToInstrDict[currentFile] = line.strip().strip("Program Numbers:[").strip("]").split(",")

InstrFile.close()



############ CREATE BANK TO INSTRUMENT DICTIONARY ############



BankToInstrument = {}

for fileName in BankDict:#["BANK_BGM_FIELD6"]:
    bankFile = open("gs_sound_data/Files/BANK/" + fileName + ".txt")
    BankToInstrument[fileName] = {}
    for line in bankFile:
        if line.startswith("\t"):
            lineArray = line.strip().split(",")
            waveArc = lineArray[2]
            waveId = lineArray[1]
            BankToInstrument[fileName][currInstrument] += [UsageDict[fileName][int(waveArc)], waveId]
        elif "NULL" not in line:
            lineArray = line.strip().split(",")
            currInstrument = lineArray[0]
            if len(lineArray) > 4 and "Keysplit" not in line:
                waveArc = lineArray[3]
                waveId = lineArray[2]
                BankToInstrument[fileName][currInstrument] = {UsageDict[fileName][int(waveArc)], waveId}
            else:
                BankToInstrument[fileName][currInstrument] = []



############ START LOGGING WHICH SEQ'S USE WHICH INSTRUMENTS ############
