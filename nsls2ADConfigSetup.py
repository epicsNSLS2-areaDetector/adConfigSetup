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
macroValList = [epicsBasePair, supportPair, adPair, adSupportPair, busyPair, asynPair, seqPair, 
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



# Function that removes all whitespace in a string
def remove_whitespace(line):
    line.strip()
    no_whitespace = line.replace(" ", "")
    return no_whitespace



# Function that prints macro value pairs. Used to test external config file support.
def print_pair_list(macroValuePairs):
    for pair in macroValuePairs:
        print("A value of '{}' will be assigned to the '{}' macro.\n".format(pair[1][:-1], pair[0]))



# Function that iterates over the configuration files that pertain to the current arch,
# identifies lines that contain the macros in the list, and replaces them. If not in the list 
# the line is copied as-is. upon completion, the old file is moved into a new "EXAMPLE_FILES"
# directory if it is needed again.
#
# @params: oldPath -> path to the example configuration file
# @params: recPairs -> pairs of required Macros to edit
# @params: optPairs -> pairs of optional macros to edit
# @params: replaceOpt -> flag to see if opt macros are to be replaced
# @return: void
#
def copy_macro_replace(oldPath, reqPairs, optPairs, replaceOpt):
    oldFile = open(oldPath, "r+")
    # Every example file starts with EXAMPLE_FILENAME, so we disregard the first 8 characters 'EXAMPLE_' for the new name
    newPath = oldPath[8:]
    newFile = open(newPath, "w+")

    # Iterate over the lines in the old file, replacing macros as you go
    line = oldFile.readline()
    while line:
        wasMacro = False
        for pair in reqPairs:
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
# If building for multilple architectures, do not use the -r flag enabling this.
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
# @params: recPairs -> recquired macro/value pairs
# @params: optPairs -> optional macro/value pairs
# @params: replaceOpt -> flag to see if optional macro/value pairs should be replaced
# @return: void
#
def process_examples(recPairs, optPairs, replaceOpt):
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE"):
                copy_macro_replace(file, recPairs, optPairs, replaceOpt)



# Simple function that checks if a macro is required for substitution
#
# @params: macro -> macro that is being substituted
# @return: True if macro is required False otherwise
def check_required(macro):
    for pair in macroValList:
        if macro == pair[0]:first make a directory to house all of the example files so they don't clutter up the workspace
            return True
    return False



# Function that adds required pairs that were not found in an external file and fills them with default values.
#
# @params: reqPairs -> required pair list taken from the external setup file
# @return: reqPairsFilled -> list of pairs from file + all missing required pairs.
def add_req_pairs(reqPairs):
    reqPairsFilled = []
    for pair in macroValList:
        isExternal = False
        for externPair in reqPairs:
            if externPair[0] == pair[0]:
                reqPairsFilled.append(externPair)
                isExternal = True
        if not isExternal:
            print("{} macro not found in external setup file. Assigning default value: {} to {}.".format(pair[0],pair[1],pair[0]))
            reqPairsFilled.append(pair)
    return reqPairsFilled



# Function that generates macro value pairs from an external file.
# Takes path to file as input, reads line by line breaking apart macros and values
# Checks if the macro is required or not, and if only required macros are being replaced,
# takes that into account.
#
# @params: path_to_extern -> path to external setup file.
# @return: reqPairsFilled -> list of macro/value pairs taken from the file + all remaining required pairs with default values
# @return: optPairs -> optional macro/value pairs taken from the external setup file
def generate_pairs_extern(path_to_extern):
    reqPairs = []
    optPairs = []
    externFile = open(path_to_extern, "r+")

    line = externFile.readline()

    while line:
        if line[0] != '#' and "=" in line:
            print("{}".format(line))
            pair = line.split('=')
            req = check_required(pair[0])
            if req:
                reqPairs.append(pair)
            else:
                optPairs.append(pair)
        line = externFile.readline()
    reqPairsFilled = add_req_pairs(reqPairs)
    externFile.close()
    return reqPairsFilled, optPairs



# Top Level function of the configuration generator
# First makes a directory to house all of the example files so they don't clutter up the workspace
# Then if specified, removes all 'EXAMPLE' files not used for the current architecture.
# Next calls the process examples function either with the built in macro/value pairs, or with an
# external setup file. Such a setup file can also be automatically generated using this script with the -g flag.
#
# @params: use_external -> flag to use external setup file set by '-o'
# @params: path_to_extern -> path to external setup file, or None if using built in macro/val pairs
# @params: remove_other_arch -> flag that decides if 'EXAMPLE' files of other arches are removed. Set by '-r'
# @params: replace_opt_macros -> flag that decides if optional macros are also replaced. Set by '-o'
# @return: void
#
def generate_config_files(use_external, path_to_extern, remove_other_arch, replace_opt_macros):
    if not os.path.exists("EXAMPLE_FILES"):
        os.makedirs("EXAMPLE_FILES")

    if remove_other_arch == True:
        remove_examples()
    
    if use_external == True:
        reqPairs, optPairs = generate_pairs_extern(path_to_extern)
        process_examples(reqPairs, optPairs, replace_opt_macros)
    
    else:
        process_examples(macroValList, optionalValList, replace_opt_macros)



# Function that checks a detected macro line against a list of discovered lines
#
# @params: macroLines -> list of discovered lines containing macros/values
# @params: line -> current line being tested
# @return -> true if the line was accounted for false otherwise
#
def counted_check(macroLines, line):
    noWhitespace = remove_whitespace(line)
    macro = line.split('=')[0]
    for l in macroLines:
        if l.split('=')[0] == macro:
            return True
    return False



# Function that finds a list of all of the macros in a given file, with the caveat that duplicates are removed
#
# @params: filePath -> path to file in which search is done.
# @params: countedMacros -> list of macros already discovered.
# @return: macroLines -> list of all of the discovered macro lines
#
def find_macros(filePath, countedMacros):
    file = open(filePath, "r+")
    macroLines = []
    line = file.readline()
    while line:
        if "=" in line and line[0]!='#':
            if not counted_check(countedMacros, line):
                macroLines.append(remove_whitespace(line))
        line = file.readline()
    return macroLines



# Core function used to generate setup file from existing files
# First, open a new file, then read all of the current files  searching for non-commented macros
# then write these lines with whitespace removed to the new setup file
#
# @params: includeOptional -> decides whether all macros are added, or just required ones. (Set with -o default is false)
# @return: void
#
def generate_setup_file(includeOptional):
    setupFile = open("AD_SETUP_MACROS", "w+")
    setupFile.write("# Autogenerated setup file for Area Detector for use with configuration script.\n")
    setupFile.write("\n")
    macroLines = []
    for file in os.listdir():
        if os.path.isfile(file) and file != "nsls2ADConfigSetup.py":
            fileMacros = find_macros(file, macroLines)
            macroLines = macroLines + fileMacros
    for line in macroLines:
        if not includeOptional:
            req = check_required(line.split('=')[0])
            if req:
                setupFile.write(line)
        else:
            setupFile.write(line)
    setupFile.close()



# Function responsible for parsing the user's command line arguments.
# 
# usage: nsls2ADConfigSetup.py [-h] [-o] [-r] [-e EXT]
#
# Setup area detector configuration files
#
# optional arguments:
#  -h, --help         show this help message and exit
#  -g, --generate     Generate a macro setup file for future use.
#  -o, --opt          Substitute optional package macros
#  -r, --rem          Remove example files for other arches
#  -e EXT, --ext EXT  Use an eternal macro list
#
# After parsing calls the top level generate_config_files function
#
def parse_user_input():
    parser = argparse.ArgumentParser(description = 'Setup area detector configuration files')
    parser.add_argument('-g', '--generate', action = 'store_true', help = 'Add this flag to use current config files to generate a macro setup file for future use.')
    parser.add_argument('-o', '--opt', action = 'store_true', help = 'Substitute optional package macros (configuring), include opt macros in generated setup file (generating).')
    parser.add_argument('-r', '--rem', action = 'store_true', help = 'Remove example files for other arches')
    parser.add_argument('-e', '--ext', help = 'Use an eternal macro list')
    arguments = vars(parser.parse_args())
    if arguments["generate"] == True:
        generate_setup_file(arguments["opt"])
        print("Setup file has been generated and is named 'AD_SETUP_MACROS.")
    else:
        if arguments["ext"] is not None:
            generate_config_files(True, arguments["ext"], arguments["rem"], arguments["opt"])
        else:
            generate_config_files(False, None, arguments["rem"], arguments["opt"])


    
parse_user_input()
# generate_config_files()