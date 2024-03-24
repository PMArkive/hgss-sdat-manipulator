#!/usr/bin/python3

import os
import shutil



############ CREATE SSEQ TO BANK/BANK TO SWAR DICTIONARY ############



UsageFile = open("usage.txt")

UsageDict = {}
SEQToSSEQDict = {}
SEQDict = {}
BankDict = {}

seqCount = 0
bankCount = 1

for line in UsageFile:
    if line.startswith("SEQ_"):
        UsageDict[line.split(" uses ")[0].strip()] = line.split(" uses ")[2].strip()
        SEQToSSEQDict[line.split(" uses ")[0].strip()] = line.split(" uses ")[1].strip()
        SEQDict[line.split(" uses ")[0].strip()] = seqCount
        seqCount += 1
    elif line.startswith("BANK_"):
        UsageDict[line.split(" uses ")[0].strip()] = line.split(" uses ")[1].strip().replace("[", "").replace(" ", "").replace("]", "").split(",")
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
SSEQToInstrDict = {}

for line in InstrFile:
    if line.startswith("File:"):
        currentFile = line.strip().strip("File: ").replace(" ", "").strip(".smft")
    elif line.startswith("Program"):
        SSEQToInstrDict[currentFile] = line.strip().strip("Program Numbers:[").strip("]").replace(" ", "").split(",")

InstrFile.close()



############ CREATE BANK TO INSTRUMENT DICTIONARY ############



BankToInstrument = {}

for fileName in BankDict:#["BANK_BGM_FIELD6"]:
    bankFile = open("gs_sound_data/Files/BANK/" + fileName + ".txt")
    BankToInstrument[fileName] = {}
    for line in bankFile:
        if line.startswith("\t"):
            lineArray = line.strip().replace(" ", "").split(",")
            waveArc = lineArray[2]
            waveId = lineArray[1]
            BankToInstrument[fileName][currInstrument] += [UsageDict[fileName][int(waveArc)], waveId]
        elif "NULL" not in line:
            lineArray = line.strip().replace(" ", "").split(",")
            currInstrument = lineArray[0]
            if len(lineArray) > 4 and "Keysplit" not in line:
                waveArc = lineArray[3]
                waveId = lineArray[2]
                BankToInstrument[fileName][currInstrument] = [UsageDict[fileName][int(waveArc)], waveId]
            else:
                BankToInstrument[fileName][currInstrument] = []
    bankFile.close()



############ START LOGGING WHICH SEQ'S USE WHICH INSTRUMENTS ############



os.makedirs("NEW_WAVARC", exist_ok=True)

for seq in SEQDict:
    #try:
    #    print(seq, UsageDict[seq], UsageDict[UsageDict[seq]], BankToInstrument[UsageDict[seq]])
    #except KeyError:
    #    print(seq + " (File " + SEQToSSEQDict[seq] + ") does not exist!")
    if 'AIF' in seq:
        continue
    for instr in SSEQToInstrDict[SEQToSSEQDict[seq]]:
        print(seq + " (" + SEQToSSEQDict[seq] + ") uses instrument " + instr + " from " + UsageDict[seq] + ".  Searching for instrument...")
        for entry in BankToInstrument[UsageDict[seq]]:
            if "Unused" not in entry and int(entry) == int(instr):
                print("Instrument " + instr + " found...")
                print(BankToInstrument[UsageDict[seq]][instr])
                os.makedirs("NEW_WAVARC/BANK_" + seq[len("SEQ_"):], exist_ok=True)
                currOutputSwavWavarc = 0
                for n in range(1, len(BankToInstrument[UsageDict[seq]][instr]), 2):
                    currOutputWavArc = BankToInstrument[UsageDict[seq]][instr][n-1]
                    currInputSwavArc = BankToInstrument[UsageDict[seq]][instr][n]
                    shutil.copyfile("gs_sound_data/Files/WAVARC/{}/{:02X}.swav".format(currOutputWavArc, int(currInputSwavArc)), "NEW_WAVARC/{}/{:02X}.swav".format("BANK_" + seq[4:], currOutputSwavWavarc))
                    currOutputSwavWavarc += 1
    print("-----------------")
