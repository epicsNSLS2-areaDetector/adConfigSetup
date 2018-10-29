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
# Required Macro/Value pairs. You may add custom macro/value pairs here, if you would like them to be replaced on every run of the script.
# When using an external file and one of these pairs is missing from the file, the default value listed here is used.
epicsBase_pair       = ["EPICS_BASE",                        "/epics/base-7.0.1.1"]
support_pair         = ["SUPPORT",                           "/epics/synAppsRelease/synApps/support"]
ad_pair              = ["AREA_DETECTOR",                     "$(SUPPORT)/areaDetector-3-3-2"]
adSupport_pair       = ["ADSupport",                         "$(AREA_DETECTOR)/ADSupport"]
busy_pair            = ["BUSY",                              "$(SUPPORT)/busy"]
asyn_pair            = ["ASYN",                              "$(SUPPORT)/asyn"]
seq_pair             = ["SNCSEQ",                            "$(SUPPORT)/seq-2-2-5"]
sscan_pair           = ["SSCAN",                             "$(SUPPORT)/sscan"]
alive_pair           = ["ALIVE",                             "$(SUPPORT)/alive"]
autosave_pair        = ["AUTOSAVE",                          "$(SUPPORT)/autosave"]
calc_pair            = ["CALC",                              "$(SUPPORT)/calc"]
adCore_pair          = ["ADCORE",                            "$(AREA_DETECTOR)/ADCore"]
iocStats_pair        = ["DEVIOCSTATS",                       "$(SUPPORT)/iocStats"]
pva_pair             = ["PVA",                               "path to pva"]

# List containing macros and values to replace. List looks as follows: [ ["EPICS_BASE", pathToBase], ["SUPPORT", pathToSupport], ...]
required_macro_value_list = [epicsBase_pair, support_pair, ad_pair, adSupport_pair, busy_pair, asyn_pair, seq_pair, 
                sscan_pair, alive_pair, autosave_pair, calc_pair, adCore_pair,  
                iocStats_pair, pva_pair]
#######################################################################################################################################################



# MACROS FOR OPTIONAL PACKAGES (All of these values are set to defaults here to start)
#######################################################################################################################################################
# These macro/value pairs follow the same format as the required ones. To enable replacement of optional macros run the script with the -o flag
# You can also add macro value pairs that you wish to be optional here.
#
# NOTE: If the external tag is set to 'YES' and the with tag is set to 'YES', you must enter the generated CONFIG_SITE.local file and add paths to
#       the include and library paths of the external packages.

boost_pair           = ["WITH_BOOST",                        "NO"]           # Boost is used for AD unit tests

incPVA_pair          = ["WITH_PVA",                          "YES"]          # pva must be enabled for NDPluginPva, pvaDriver, and qsrv

qsrv_pair            = ["WITH_QSRV",                         "YES"]          #controls whether IOCs are built with QSRV

# Blosc is required for specific compressors in the HDF5 plugin
incBlosc_pair        = ["WITH_BLOSC",                        "YES"]
extBlosc_pair        = ["BLOSC_EXTERNAL",                    "NO"]

# GraphicsMagick is used by NDFileMagick and ADURL
incGFXMag_pair       = ["WITH_GRAPHICSMAGIK",                "YES"]
extGFXMag_pair       = ["GRAPHICSMAGICK_EXTERNAL",           "NO"]
prefixGFXMag_pair    = ["GRAPHICSMAGICK_PREFIX_SYMBOLS",     "YES"]

# HDF5 is required for HDF5 file processing as well as Nexus
incHDF5_pair         = ["WITH_HDF5",                         "YES"]
extHDF5_pair         = ["HDF5_EXTERNAL",                     "NO"]

# JPEG is required for jpg file processing
incJPG_pair          = ["WITH_JPEG",                         "YES"]
extJPG_pair          = ["JPEG_EXTERNAL",                     "NO"]

# NetCDF processing
incNCDF_pair         = ["WITH_NETCDF",                       "YES"]
extNCDF_pair         = ["NETCDF_EXTERNAL",                   "NO"]

# Nexus file processing
incNEX_pair          = ["WITH_NEXUS",                        "YES"]
extNEX_pair          = ["NEXUS_EXTERNAL",                    "NO"]

# Computer Vision ADCompVision ADPluginBar
incOpenCV_pair       = ["WITH_OPENCV",                       "NO"]
extOpenCV_pair       = ["OPENCV_EXTERNAL",                   "YES"]

# Required for HDF5 and Nexus.
incSzip_pair         = ["WITH_SZIP",                         "YES"]
extSzip_pair         = ["SZIP_EXTERNAL",                     "NO"]

# Tiff processing
incTIF_pair          = ["WITH_TIFF",                         "YES"]
extTIF_pair          = ["TIFF_EXTERNAL",                     "NO"]

# Required by ADCore, but can use external build.
extXML2_pair         = ["XML2_EXTERNAL",                     "NO"]

# Required for HDF5 and Nexus
incZlib_pair         = ["WITH_ZLIB",                         "YES"]
extZlib_pair         = ["ZLIB_EXTERNAL",                     "NO"]


# List containing all optional macro/value pairs. When adding a new pair, make sure to add it to this list.
optional_mcaro_value_pairs = [boost_pair, incPVA_pair, qsrv_pair, incBlosc_pair, extBlosc_pair, incGFXMag_pair, extGFXMag_pair, prefixGFXMag_pair, incHDF5_pair, extHDF5_pair,
                    incJPG_pair, extJPG_pair, incNCDF_pair, extNCDF_pair, incNEX_pair, extNEX_pair, incOpenCV_pair, extOpenCV_pair, incSzip_pair, extSzip_pair,
                    incTIF_pair, extTIF_pair, extXML2_pair, incZlib_pair, extZlib_pair]
#######################################################################################################################################################



# Function that removes all whitespace in a string
# Used prior to splitting a macro/value pair on the '=' symbol.
def remove_whitespace(line):
    line.strip()
    no_whitespace = line.replace(" ", "")
    return no_whitespace



# Function that prints macro value pairs. Used to test external config file support.
def print_pair_list(macro_value_pairs):
    for pair in macro_value_pairs:
        print("A value of '{}' will be assigned to the '{}' macro.\n".format(pair[1][:-1], pair[0]))



# Function that iterates over the configuration files that pertain to the current arch,
# identifies lines that contain the macros in the list, and replaces them. If not in the list 
# the line is copied as-is. upon completion, the old file is moved into a new "EXAMPLE_FILES"
# directory if it is needed again.
#
# @params: old_path                 -> path to the example configuration file
# @params: required_pairs           -> pairs macros and values that are guaranteed to be replaced
# @params: optional_pairs           -> pairs macros and values that can optionally be replaced
# @params: replace_optional_macros  -> flag to see if optional macros will be replaced
# @params: replace_commented        -> flag that decides if commented macros are to be replaced as well
# @return: void
#
def copy_macro_replace(old_path, required_pairs, optional_pairs, replace_optional_macros, replace_commented):
    old_file = open(old_path, "r+")
    # Every example file starts with EXAMPLE_FILENAME, so we disregard the first 8 characters 'EXAMPLE_' for the new name
    new_path = old_path[8:]
    new_file = open(new_path, "w+")

    # Iterate over the lines in the old file, replacing macros as you go
    line = old_file.readline()
    while line:
        # check if the line contains a macro
        was_macro = False
        for pair in required_pairs:
            # check if we want to replace the commented macro
            if replace_commented and line[0] == '#':
                line = line[1:]
            if line.startswith(pair[0]):
                new_file.write("{}={}\n".format(pair[0],pair[1]))
                was_macro = True
        # If it wasn't a required macro, check if it was an optional macro (if -o flag was used)
        if was_macro == False and replace_optional_macros == True:
            for pair in optional_pairs:
                if replace_commented and line[0] == '#':
                    line = line[1:]
                if line.startswith(pair[0]):
                    new_file.write("{}={}\n".format(pair[0],pair[1]))
                    was_macro = True
        # Otherwise just write line as-is
        if was_macro == False:
            new_file.write(line)
        line = old_file.readline()
    old_file.close()
    # Place the old file in a directory for future use.
    shutil.move(old_path, "EXAMPLE_FILES/{}".format(old_path))
    new_file.close()



# Removes unnecessary example files i.e. vxworks, windows etc.
# This cleans up the configuration directory, and only leaves necessary files.
#
# If building for multilple architectures, do not use the -r flag enabling this.
# In the future, a toggle between arches will be looked at.
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
# @params: required_pairs           -> recquired macro/value pairs
# @params: optrional_pairs          -> optional macro/value pairs
# @params: replace_optional_macros  -> flag to see if optional macro/value pairs should be replaced
# @params: replace_commented        -> flag that decides if commented macros can also be replaced
# @return: void
#
def process_examples(required_pairs, optional_pairs, replace_optional_macros, replace_commented):
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE"):
                copy_macro_replace(file, required_pairs, optional_pairs, replace_optional_macros, replace_commented)



# Simple function that checks if a macro is required for substitution
#
# @params: macro -> macro that is being substituted
# @return: True if macro is required False otherwise
#
def check_required(macro):
    for pair in required_macro_value_list:
        if macro == pair[0]:
            return True
    return False



# Function that adds required pairs that were not found in an external file and fills them with default values.
#
# @params: reqPairs -> required pair list taken from the external setup file
# @return: reqPairsFilled -> list of pairs from file + all missing required pairs.
#
def add_req_pairs(required_pairs):
    required_pairs_filled = []
    for pair in required_macro_value_list:
        is_external = False
        for external_pair in required_pairs:
            if external_pair[0] == pair[0]:
                required_pairs_filled.append(external_pair)
                is_external = True
        if not is_external:
            print("{} macro not found in external setup file. Assigning default value: {} to {}.".format(pair[0],pair[1],pair[0]))
            required_pairs_filled.append(pair)
    return required_pairs_filled



# Function that generates macro value pairs from an external file.
# Takes path to file as input, reads line by line breaking apart macros and values
# Checks if the macro is required or not, and if only required macros are being replaced,
# takes that into account.
#
# @params: path_to_extern -> path to external setup file.
# @return: reqPairsFilled -> list of macro/value pairs taken from the file + all remaining required pairs with default values
# @return: optPairs -> optional macro/value pairs taken from the external setup file
def generate_pairs_extern(path_to_extern):
    required_pairs = []
    optional_pairs = []
    external_file = open(path_to_extern, "r+")

    line = external_file.readline()

    while line:
        if line[0] != '#' and "=" in line:
            # print("{}".format(line))
            line_no_whitespace = remove_whitespace(line)
            pair = line_no_whitespace.split('=')
            if pair[1] == "":
                print("Bypassing macro {}, no value specified\n".format(pair[0]))
            else:
                req = check_required(pair[0])
                if req:
                    required_pairs.append(pair)
                else:
                    optional_pairs.append(pair)
        line = external_file.readline()
    required_pairs_filled = add_req_pairs(required_pairs)
    external_file.close()
    return required_pairs_filled, optional_pairs



# Top Level function of the configuration generator
# First makes a directory to house all of the example files so they don't clutter up the workspace
# Then if specified, removes all 'EXAMPLE' files not used for the current architecture.
# Next calls the process examples function either with the built in macro/value pairs, or with an
# external setup file. Such a setup file can also be automatically generated using this script with the -g flag.
#
# @params: use_external         -> flag to use external setup file set by '-e'
# @params: path_to_extern       -> path to external setup file, or None if using built in macro/val pairs
# @params: remove_other_arch    -> flag that decides if 'EXAMPLE' files of other arches are removed. Set by '-r'
# @params: replace_opt_macros   -> flag that decides if optional macros are also replaced. Set by '-o'
# @params: replace_commented    -> flag that decides if commented macros are to be replaced as well
# @return: void
#
def generate_config_files(use_external, path_to_extern, remove_other_arch, replace_opt_macros, replace_commented):
    if not os.path.exists("EXAMPLE_FILES"):
        os.makedirs("EXAMPLE_FILES")

    if remove_other_arch == True:
        remove_examples()
    
    if use_external == True:
        required_pairs, optional_pairs = generate_pairs_extern(path_to_extern)
        process_examples(required_pairs, optional_pairs, replace_opt_macros, replace_commented)
    
    else:
        process_examples(required_macro_value_list, optional_mcaro_value_pairs, replace_opt_macros, replace_commented)



# Function that checks a detected macro line against a list of discovered lines
#
# @params: macro_lines  -> list of discovered lines containing macros/values
# @params: line         -> current line being tested
# @return: true if the line was accounted for false otherwise
#
def counted_check(macro_lines, line):
    line_no_whitespace = remove_whitespace(line)
    macro = line_no_whitespace.split('=')[0]
    for l in macro_lines:
        if l.split('=')[0] == macro:
            return True
    return False



# Function that finds a list of all of the macros in a given file, with the caveat that duplicates are removed
#
# @params: file_path            -> path to file in which search is done.
# @params: counted_macros       -> list of macros already discovered.
# @params: include_commented    -> flag that decides if commented out macros are included
# @return: macroLines           -> list of all of the discovered macro lines
#
def find_macros(file_path, counted_macros, include_commented):
    file = open(file_path, "r+")
    macro_lines = []
    line = file.readline()
    while line:
        if include_commented:
            if "=" in line:
                if line[0] == '#':
                    line = line[1:]
                if not counted_check(counted_macros, line):
                    macro_lines.append(remove_whitespace(line))
        else:
            if "=" in line and line[0]!='#':
                if not counted_check(counted_macros, line):
                    macro_lines.append(remove_whitespace(line))
        line = file.readline()
    return macro_lines



# Core function used to generate setup file from existing files
# First, open a new file, then read all of the current files  searching for non-commented macros
# then write these lines with whitespace removed to the new setup file
#
# @params: includeOptional -> decides whether all macros are added, or just required ones. (Set with -o default is false)
# @return: void
#
def generate_setup_file(include_optional, include_commented):
    setup_file = open("AD_SETUP_MACROS", "w+")
    setup_file.write("# Autogenerated setup file for Area Detector for use with configuration script.\n")
    setup_file.write("\n")
    macro_lines = []
    for file in os.listdir():
        if os.path.isfile(file) and file != "nsls2ADConfigSetup.py":
            file_macros = find_macros(file, macro_lines, include_commented)
            macro_lines = macro_lines + file_macros
    for line in macro_lines:
        if not include_optional:
            req = check_required(line.split('=')[0])
            if req:
                setup_file.write(line)
        else:
            setup_file.write(line)
    setup_file.close()



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
#  -c, --commented    Include commented out macro/value pairs in setup file generation
#  -e EXT, --ext EXT  Use an eternal macro list
#
# After parsing calls the top level generate_config_files function
#
def parse_user_input():
    parser = argparse.ArgumentParser(description = 'Setup area detector configuration files')
    parser.add_argument('-g', '--generate',     action = 'store_true', help = 'Add this flag to use current config files to generate a macro setup file for future use.')
    parser.add_argument('-o', '--opt',          action = 'store_true', help = 'Substitute optional package macros (configuring), include opt macros in generated setup file (generating).')
    parser.add_argument('-r', '--rem',          action = 'store_true', help = 'Remove example files for other arches')
    parser.add_argument('-c', '--commented',    action = 'store_true', help = 'Replace macros even if they are commented out in the config files')
    parser.add_argument('-e', '--ext', help = 'Use an eternal macro list')
    arguments = vars(parser.parse_args())
    if arguments["generate"] == True:
        generate_setup_file(arguments["opt"], arguments["commented"])
        print("Setup file has been generated and is named 'AD_SETUP_MACROS.")
    else:
        if arguments["ext"] is not None:
            generate_config_files(True, arguments["ext"], arguments["rem"], arguments["opt"], arguments["commented"])
        else:
            generate_config_files(False, None, arguments["rem"], arguments["opt"], arguments["commented"])


    
parse_user_input()
# generate_config_files()
