# Python script for generating the required configuration files for area detector.
#
# Author: Jakub Wlodek
# Copyright (c): Brookhaven National Laboratory
# Created: September 28, 2018

import os
import shutil
import argparse

# Global variables. isLinux is necessary because of the .Linux file being univeral across Linux arches
isLinux = True
EPICS_ARCH = "linux-x86_64"

# MACROS FOR REQUIRED PACKAGES
#####################################################################################################################################################
# Macro/Value pairs. To add new macros and values, add them here, and add the name to the list. Follow the same format as below
# Check the paths in each pair against your file system and change as necessary
epicsBasePair       = ["EPICS_BASE",                        "/epics/base-7.0.1.1"]
supportPair         = ["SUPPORT",                           "/epics/synAppsRelease/synApps/support"]
adPair              = ["AREA_DETECTOR",                     "$(SUPPORT)/areaDetector-3-3-2"]
adSupportPair       = ["ADSupport",                         "$(AREA_DETECTOR)/ADSupport"]
busyPair            = ["BUSY",                              "$(SUPPORT)/busy"]
asynPair            = ["ASYN",                              "$(SUPPORT)/asyn"]
seqPair             = ["SNCSEQ",                            "$(SUPPORT)/seq-2-2-5"]
sscanPair           = ["SSCAN",                             "$(SUPPORT)/sscan"]
alivePair           = ["ALIVE",                             "$(SUPPORT)/alive"]
autosavePair        = ["AUTOSAVE",                          "$(SUPPORT)/autosave"]
calcPair            = ["CALC",                              "$(SUPPORT)/calc"]
adCorePair          = ["ADCORE",                            "$(AREA_DETECTOR)/ADCore"]
iocStatsPair        = ["DEVIOCSTATS",                       "$(SUPPORT)/iocStats"]
pvaPair             = ["PVA",                               "path to pva"]

# List containing macros and values to replace. List looks as follows: [ ["EPICS_BASE", pathToBase], ["SUPPORT", pathToSupport], ...]
macroValList = [epicsBasePair, supportPair, adPair, busyPair, asynPair, seqPair, 
                sscanPair, alivePair, autosavePair, calcPair, adCorePair,  
                iocStatsPair, pvaPair]
#######################################################################################################################################################

# MACROS FOR OPTIONAL PACKAGES (All of these values are set to defaults here to start)
#######################################################################################################################################################
# These macro/value pairs follow the same format as the required ones. To enable replacement set the replaceOptionalPackages toggle to 'True'
#
# NOTE: If the external tag is set to 'YES' and the with tag is set to 'YES', you must enter the generated CONFIG_SITE.local file and add paths to
#       the include and library paths of the external packages.

boostPair           = ["WITH_BOOST",                        "NO"]           # Boost is used for AD unit tests

incPVAPair          = ["WITH_PVA",                          "YES"]          # pva must be enabled for NDPluginPva, pvaDriver, and qsrv

qsrvPair            = ["WITH_QSRV",                         "YES"]          #controls whether IOCs are built with QSRV

# Blosc is required for specific compressors in the HDF5 plugin
incBloscPair        = ["WITH_BLOSC",                        "YES"]
extBloscPair        = ["BLOSC_EXTERNAL",                    "NO"]

# GraphicsMagick is used by NDFileMagick and ADURL
incGFXMagPair       = ["WITH_GRAPHICSMAGIK",                "YES"]
extGFXMagPair       = ["GRAPHICSMAGICK_EXTERNAL",           "NO"]
prefixGFXMagPair    = ["GRAPHICSMAGICK_PREFIX_SYMBOLS",     "YES"]

# HDF5 is required for HDF5 file processing as well as Nexus
incHDF5Pair         = ["WITH_HDF5",                         "YES"]
extHDF5Pair         = ["HDF5_EXTERNAL",                     "NO"]

# JPEG is required for jpg file processing
incJPGPair          = ["WITH_JPEG",                         "YES"]
extJPGPair          = ["JPEG_EXTERNAL",                     "NO"]

# NetCDF processing
incNCDFPair         = ["WITH_NETCDF",                       "YES"]
extNCDFPair         = ["NETCDF_EXTERNAL",                   "NO"]

# Nexus file processing
incNEXPair          = ["WITH_NEXUS",                        "YES"]
extNEXPair          = ["NEXUS_EXTERNAL",                    "NO"]

# Computer Vision ADCompVision ADPluginBar
incOpenCVPair       = ["WITH_OPENCV",                       "NO"]
extOpenCVPair       = ["OPENCV_EXTERNAL",                   "YES"]

# Required for HDF5 and Nexus.
incSzipPair         = ["WITH_SZIP",                         "YES"]
extSzipPair         = ["SZIP_EXTERNAL",                     "NO"]

# Tiff processing
incTIFPair          = ["WITH_TIFF",                         "YES"]
extTIFPair          = ["TIFF_EXTERNAL",                     "NO"]

# Required by ADCore, but can use external build.
extXML2Pair         = ["XML2_EXTERNAL",                     "NO"]

# Required for HDF5 and Nexus
incZlibPair         = ["WITH_ZLIB",                         "YES"]
extZlibPair         = ["ZLIB_EXTERNAL",                     "NO"]


# List containing all optional macro/value pairs
optionalValList = [boostPair, incPVAPair, qsrvPair, incBloscPair, extBloscPair, incGFXMagPair, extGFXMagPair, prefixGFXMagPair, incHDF5Pair, extHDF5Pair,
                    incJPGPair, extJPGPair, incNCDFPair, extNCDFPair, incNEXPair, extNEXPair, incOpenCVPair, extOpenCVPair, incSzipPair, extSzipPair,
                    incTIFPair, extTIFPair, extXML2Pair, incZlibPair, extZlibPair]
#######################################################################################################################################################


# Function that iterates over the configuration files that pertain to the current arch,
# identifies lines that contain the macros in the list, and replaces them. If not in the list 
# the line is copied as-is. upon completion, the old file is moved into a new "EXAMPLE_FILES"
# directory if it is needed again.
#
# @params: oldPath -> path to the example configuration file
# @return: void
#
def copy_macro_replace(oldPath, recPairs, optPairs, replaceOpt):
    oldFile = open(oldPath, "r+")
    # Every example file starts with EXAMPLE_FILENAME, so we disregard the first 8 characters 'EXAMPLE_' for the new name
    newPath = oldPath[8:]
    newFile = open(newPath, "w+")

    # Iterate over the lines in the old file, replacing macros as you go
    line = oldFile.readline()
    while line:
        wasMacro = False
        for pair in recPairs:
            if line.startswith(pair[0]):
                newFile.write("{}={}\n".format(pair[0],pair[1]))
                wasMacro = True
        if wasMacro == False and replaceOpt == True:
            for pair in optPairs:
                if line.startswith(pair[0]):
                    newFile.write("{}={}\n".format(pair[0],pair[1]))
                    wasMacro = True
        if wasMacro == False:
            newFile.write(line)
        line = oldFile.readline()
    oldFile.close()
    # Place the old file in a directory for future use.
    shutil.move(oldPath, "EXAMPLE_FILES/{}".format(oldPath))
    newFile.close()


# Removes unnecessary example files i.e. vxworks, windows etc.
# This cleans up the configuration directory, and only leaves necessary files.
#
# If building for multilple architectures, remove this requirement.
#
# @return: void
#
def remove_examples():
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE") and not file.endswith(".local") and not file.endswith(EPICS_ARCH):
                if not file.endswith(".Linux"):
                    os.remove(file)
                else:
                    if not isLinux:
                        os.remove(file)


# Basic function that iterates over all of the files and directories in the "configure" directory
# of area detector. If it detects "EXAMPLE" files, it passes them on to the macro replacing function
#
# @return: void
#
def process_examples(recPairs, optPairs, replaceOpt):
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE"):
                copy_macro_replace(file, recPairs, optPairs, replaceOpt)


# Top Level function of the configuration generator
def generate_config_files(use_external, path_to_extern, remove_other_arch, replace_opt_macros):
    # first make a directory to house all of the example files so they don't clutter up the workspace
    if not os.path.exists("EXAMPLE_FILES"):
        os.makedirs("EXAMPLE_FILES")

    if remove_other_arch == True:
        remove_examples()
    
    if use_external == True:
        recPairs, optPairs = generate_pairs_extern(path_to_extern)
        process_examples(recPairs, optPairs)
    
    else:
        process_examples(macroValList, optionalValList)

def parse_user_input():
    parser = argparse.ArgumentParser(description = 'Setup area detector configuration files')
    parser.add_argument('-o', '--opt', action = 'store_true', help = 'Substitute optional package macros')
    parser.add_argument('-r', '--rem', action = 'store_true', help = 'Remove example files for other arches')
    parser.add_argument('-e', '--ext', help = 'Use an eternal macro list')
    arguments = vars(parser.parse_args())
    if arguments["ext"] is not None:
        generate_config_files(True, arguments["ext"], arguments["rem"], arguments["opt"])
    else:
        generate_config_files(False, None, arguments["rem"], arguments["opt"])


    
parse_user_input()
# generate_config_files()