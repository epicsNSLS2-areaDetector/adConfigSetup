# Python script for generating the required configuration files for area detector.
#
# Author: Jakub Wlodek
# Copyright (c): Brookhaven National Laboratory
# Created: September 28, 2018

import os
import shutil


# Macro/Value pairs. To add new macros and values, add them here, and add the name to the list. Follow the same format as below
epicsBasePair   = ["EPICS_BASE",    "/epics/base-7.0.1.1"]
supportPair     = ["SUPPORT",       "/epics/synAppsRelease/synApps/support"]
adPair          = ["AREA_DETECTOR", "$(SUPPORT)/areaDetector-3-3-2"]
adSupportPair   = ["ADSupport",     "$(AREA_DETECTOR)/ADSupport"]
busyPair        = ["BUSY",          "$(SUPPORT)/busy"]
asynPair        = ["ASYN",          "$(SUPPORT)/asyn"]
seqPair         = ["SNCSEQ",        "$(SUPPORT)/seq-2-2-5"]
sscanPair       = ["SSCAN",         "$(SUPPORT)/sscan"]
alivePair       = ["ALIVE",         "$(SUPPORT)/alive"]
autosavePair    = ["AUTOSAVE",      "$(SUPPORT)/autosave"]
calcPair        = ["CALC",          "$(SUPPORT)/calc"]
adCorePair      = ["ADCORE",        "$(AREA_DETECTOR)/ADCore"]
iocStatsPair    = ["DEVIOCSTATS",   "$(SUPPORT)"]
pvaPair         = ["PVA",           "path to pva"]

# List containing macros and values to replace. List looks as follows: [ ["EPICS_BASE", pathToBase], ["SUPPORT", pathToSupport], ...]
macroValList = [epicsBasePair, supportPair, adPair, busyPair, asynPair, seqPair, 
                sscanPair, alivePair, autosavePair, calcPair, adCorePair,  
                iocStatsPair, pvaPair]

# Global variables:
isLinux = True
EPICS_ARCH = "linux-x86_64"


def copy_macro_replace(oldPath):
    oldFile = open(oldPath, "r+")
    newPath = oldPath[8:]
    newFile = open(newPath, "w+")

    line = oldFile.readline()
    while line:
        wasMacro = False
        for pair in macroValList:
            if line.startswith(pair[0]):
                newFile.write("{}={}\n".format(pair[0],pair[1]))
                wasMacro = True
        if wasMacro == False:
            newFile.write(line)
        line = oldFile.readline()
    oldFile.close()
    shutil.move(oldPath, "EXAMPLE_FILES/{}".format(oldPath))
    newFile.close()


# Removes unnecessary example files i.e. vxworks, windows etc.
def remove_examples():
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE") and not file.endswith(".local") and not file.endswith(EPICS_ARCH):
                if not file.endswith(".Linux"):
                    os.remove(file)
                else:
                    if not isLinux:
                        os.remove(file)



def process_examples():
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE"):
                copy_macro_replace(file)


def generate_config_files():
    # first make a directory to house all of the example files so they don't clutter up the workspace
    if not os.path.exists("EXAMPLE_FILES"):
        os.makedirs("EXAMPLE_FILES")

    remove_examples()
    process_examples()
    

generate_config_files()