#!/usr/bin/python3

import hashlib
import json
import pprint
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



############ START LOGGING WHICH SEQ'S USE WHICH INSTRUMENTS, CREATE NEW WAVE_ARCS FOR EACH SEQ WITH JUST THE INSTRUMENTS IT USES ############



print("-----------------")
os.makedirs("NEW_FILES", exist_ok=True)
os.makedirs("NEW_FILES/NEW_WAVARC", exist_ok=True)

OldSWAVToNewSWAV = {}
NewSWAVToOldSWAV = {}

for seq in SEQDict:
    #try:
    #    print(seq, UsageDict[seq], UsageDict[UsageDict[seq]], BankToInstrument[UsageDict[seq]])
    #except KeyError:
    #    print(seq + " (File " + SEQToSSEQDict[seq] + ") does not exist!")
    if 'AIF' in seq:
        continue
    OldSWAVToNewSWAV[seq] = {}
    NewSWAVToOldSWAV[seq] = {}
    currOutputSwavWavarc = 0
    for instr in SSEQToInstrDict[SEQToSSEQDict[seq]]:
        print(seq + " (" + SEQToSSEQDict[seq] + ") uses instrument " + instr + " from " + UsageDict[seq] + ".  Searching for instrument...")
        OldSWAVToNewSWAV[seq][instr] = {}
        NewSWAVToOldSWAV[seq][instr] = {}
        for entry in BankToInstrument[UsageDict[seq]]:
            if "Unused" not in entry and int(entry) == int(instr):
                print("Instrument " + instr + " found...  Copying its WAVARC entries over...")
                #print(BankToInstrument[UsageDict[seq]][instr])
                os.makedirs("NEW_FILES/NEW_WAVARC/WAVE_ARC_" + seq[len("SEQ_"):], exist_ok=True)
                for n in range(1, len(BankToInstrument[UsageDict[seq]][instr]), 2):
                    if "GAMEBOY" not in UsageDict[seq]:
                        currOutputWavArc = BankToInstrument[UsageDict[seq]][instr][n-1]
                        currInputSwavArc = BankToInstrument[UsageDict[seq]][instr][n]
                        shutil.copyfile("gs_sound_data/Files/WAVARC/{}/{:02X}.swav".format(currOutputWavArc, int(currInputSwavArc)), "NEW_FILES/NEW_WAVARC/{}/{:02X}.swav".format("WAVE_ARC_" + seq[4:], currOutputSwavWavarc))
                        #if currOutputWavArc not in OldSWAVToNewSWAV[seq][instr]:
                        #    OldSWAVToNewSWAV[seq][instr][currOutputWavArc] = {}
                        #if currOutputWavArc not in NewSWAVToOldSWAV[seq][instr]:
                        #    NewSWAVToOldSWAV[seq][instr][currOutputWavArc] = {}
                        #OldSWAVToNewSWAV[seq][instr][currOutputWavArc][currInputSwavArc] = currOutputSwavWavarc
                        #NewSWAVToOldSWAV[seq][instr][currOutputWavArc][currOutputSwavWavarc] = currInputSwavArc
                        OldSWAVToNewSWAV[seq][instr][currInputSwavArc] = currOutputSwavWavarc
                        NewSWAVToOldSWAV[seq][instr][currOutputSwavWavarc] = currInputSwavArc
                        currOutputSwavWavarc += 1
    print("-----------------")



############ RUN THROUGH AND CREATE ALL OF THE NEW BANKS ############



# process here is to copy all of the existing instruments from the old banks and replace the swav indices in the sbnk text file

# OldSWAVToNewSWAV[SSEQ][INSTRUMENT][WAV_ARC][OLD_SWAV] = NEW_SWAV
# NewSWAVToOldSWAV[SSEQ][INSTRUMENT][WAV_ARC][NEW_SWAV] = OLD_SWAV

#print("OldSWAVToNewSWAV:")
#pprint.pprint(OldSWAVToNewSWAV)
os.makedirs("NEW_FILES/NEW_BANK", exist_ok=True)

for seq in SEQDict:
    if 'AIF' in seq:
        continue
    # need to keep the instrument index in the sbnk--copy over whole instruments at a time, then, rectify with wavarc topic
    oldBankFile = open("gs_sound_data/Files/BANK/" + UsageDict[seq] + ".txt")
    newBankFile = open("NEW_FILES/NEW_BANK/{}.txt".format("BANK_" + seq[4:]), 'w')
    for instr in OldSWAVToNewSWAV[seq].keys():
        currInstrText = ""
        print("[" + seq + "] Grabbing instrument " + instr + " from " + UsageDict[seq] + "...")
        instrLogging = False
        for line in oldBankFile:
            #print(line)
            if line.startswith(str(instr) + ",") and not instrLogging:
                currInstrText = line
                instrLogging = True
                print("Instrument found!")
            elif instrLogging and line.startswith("\t"):
                processingSteps = line.strip().replace(" ", "").split(",")
                processingSteps[1] = str(OldSWAVToNewSWAV[seq][str(instr)][processingSteps[1]])
                processingSteps[2] = "0" # map every instrument to wavarc 0
                line = "\t" + ", ".join(processingSteps) + "\n"
                currInstrText += line
                #print(line)
            else:
                instrLogging = False
        oldBankFile.seek(0)
        print(currInstrText)
        newBankFile.write(currInstrText)
    oldBankFile.close()
    newBankFile.close()



############ DELETE EXISTING BANKS, WAVARCS, EDIT SSEQ'S TO MAP PROPER ############



infoBlockJsonFile = open("gs_sound_data/InfoBlock.json")
fileBlockJsonFile = open("gs_sound_data/FileBlock.json")

infoBlockJson = json.load(infoBlockJsonFile)
fileBlockJson = json.load(fileBlockJsonFile)

infoBlockJsonFile.close()
fileBlockJsonFile.close()

# first, InfoBlock seqInfo
for n in range(0, len(infoBlockJson["seqInfo"])):
    if 'AIF' in infoBlockJson["seqInfo"][n]["name"] or "UMIBE" in infoBlockJson["seqInfo"][n]["name"]:
        continue
    if "SEQ_" in infoBlockJson["seqInfo"][n]["name"]:
        infoBlockJson["seqInfo"][n]["bnk"] = "BANK_" + infoBlockJson["seqInfo"][n]["name"][len("SEQ_"):]

# instead of deleting bank stuff, just add the new ones.  can come back through and actually delete things later
newBanks = sorted(os.listdir("NEW_FILES/NEW_BANK"))
n = 0
finalElement = len(infoBlockJson["bankInfo"])
while n < finalElement:
    if infoBlockJson["bankInfo"][n]["name"] in newBanks:
        del(infoBlockJson["bankInfo"][n])
        finalElement = finalElement - 1
    n = n + 1
for n in range(0, len(newBanks)):
    baseName = newBanks[n][0:len(newBanks[n]) - len(".txt")]
    newBankEntry = {"name": baseName, "fileName": baseName + ".sbnk", "unkA": 0, "wa": ["WAVE_ARC_" + baseName[len("BANK_"):], "", "", ""]}
    infoBlockJson["bankInfo"].append(newBankEntry)

# now the wavarcInfo--add new entries here as well
newWavarcs = sorted(os.listdir("NEW_FILES/NEW_WAVARC"))
n = 0
finalElement = len(infoBlockJson["wavarcInfo"])
while n < finalElement:
    if infoBlockJson["wavarcInfo"][n]["name"] in newWavarcs:
        del(infoBlockJson["wavarcInfo"][n])
        finalElement = finalElement - 1
    n = n + 1
for n in range(0, len(newWavarcs)):
    baseName = newWavarcs[n] # folder name need not be messed with
    newWavarcEntry = {"name": baseName, "fileName": baseName + ".swar", "unkA": 0}
    infoBlockJson["wavarcInfo"].append(newWavarcEntry)

infoBlockJsonFile = open("gs_sound_data/InfoBlock.json", "w", encoding="utf-8")
json.dump(infoBlockJson, infoBlockJsonFile, ensure_ascii=False, indent=4)



############ NOW UPDATE FILEBLOCK SUCH THAT EVERYTHING IS MAPPED PROPER ############



# order is by type:  SEQ, BANK, WAVARC (with subfile)
# just need to go through and append all of the new BANK and WAVARC files where they are expected!
# then sdattool will take over and be perfect and life will flow like river

seqIndex = 0
bankIndex = 0
wavarcIndex = 0
for n in range(0, len(fileBlockJson["file"])):
    if fileBlockJson["file"][n]["type"] == "BANK" and bankIndex == 0:
        bankIndex = n
    elif fileBlockJson["file"][n]["type"] == "WAVARC" and wavarcIndex == 0:
        wavarcIndex = n
for n in range(0, len(newBanks)):
    newEntry = {}
    newEntry["name"] = newBanks[n][:-1 * len(".txt")] + ".sbnk"
    newEntry["type"] = "BANK"
    newEntry["MD5"] = "" # fuck the md5 hash
    fileBlockJson["file"].insert(wavarcIndex, newEntry)
for n in range(0, len(newWavarcs)):
    newEntry = {}
    newEntry["name"] = newWavarcs[n] + ".swar"
    newEntry["type"] = "WAVARC"
    newEntry["MD5"] = "" # fuck the md5 hash
    newEntry["subFile"] = sorted(os.listdir("NEW_FILES/NEW_WAVARC/" + newWavarcs[n]))
    fileBlockJson["file"].append(newEntry)

fileBlockJsonFile = open("gs_sound_data/FileBlock.json", "w", encoding="utf-8")
json.dump(fileBlockJson, fileBlockJsonFile, ensure_ascii=False, indent=4)
