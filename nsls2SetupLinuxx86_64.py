# Python script for generating the required configuration files for area detector.
#
# Author: Jakub Wlodek
# Copyright (c): Brookhaven National Laboratory
# Created: September 28, 2018

import os
import shutil


# Global variables:

pathBase = "/epics/"
pathAD = "$(SUPPORT)/areaDetector-3-3-2"
pathAsyn = "$(SUPPORT)/asyn"
pathADSupport = "$(AREA_DETECTOR)/ADSupport"
pathADCore = "$(AREA_DETECTOR)/ADCore"
pathBusy = "$(SUPPORT)/busy"
path

def copy_macro_replace(oldPath, newPath, macro, value):
    oldFile = open(oldPath, "r+")
    newFile = open(newPath, "w+")

    line = oldFile.readline()
    while line:
        if line.startswith(macro):
            newFile.write("{}={}\n".format(macro,value))
        else:
            newFile.write(line)
        line = oldFile.readline()
    oldFile.close()
    shutil.move(oldPath, "EXAMPLE_FILES/{}".format(oldPath))
    newFile.close()


def copy_example_file(oldPath, newPath):
    shutil.copyfile(oldPath,      newPath)
    shutil.move(oldPath,          "EXAMPLE_FILES/{}".format(oldPath))

# Copies the generic example files that do not contain absolute paths.
# These do not require specific setup for copying.
def copy_generic_files():

    print("Copying CONFIG_SITE.local.Linux. The default config is to build everything in ADSupport. Edit this file to use external library packages")
    copy_example_file("EXAMPLE_CONFIG_SITE.local.Linux", "CONFIG_SITE.local.Linux")

    print("Copying CONFIG_SITE.local. This file conatins a list of libraries that AD drivers can be built with. Edit this file to enable/disable libraries.")
    copy_example_file("EXAMPLE_CONFIG_SITE.local", "CONFIG_SITE.local")

    print("Copying CONFIG_SITE.local.linux-x86_64. This file is a linux specific extention of the standard CONFIG_SITE.local. Edit this file to enable disable linux specific libs.")
    copy_example_file("EXAMPLE_CONFIG_SITE.local.linux-x86_64", "CONFIG_SITE.local.linux-x86_64")

    print("Copying the RELEASE.local file. In this file, uncomment the detectors you wish to build on all architectures.")
    copy_example_file("EXAMPLE_RELEASE.local", "RELEASE.local")

    print("Copying RELEASE.local.linux-x86_64. Add a line for each driver that should be built just for linux-x86_64")
    copy_example_file("EXAMPLE_RELEASE.local.linux-x86_64", "RELEASE.local.linux-x86_64")



# Removes remaining example files i.e. vxworks, windows etc.
def remove_examples():
    for file in os.listdir():
        if os.path.isfile(file):
            if file.startswith("EXAMPLE"):
                os.remove(file)


def generate_config_files():
    # first make a directory to house all of the example files so they don't clutter up the workspace
    if not os.path.exists("EXAMPLE_FILES"):
        os.makedirs("EXAMPLE_FILES")

    copy_generic_files()

    print("Copying RELEASE_SUPPORT.local. This contains the path to your Support directory and should be detected automatically")
    copy_macro_replace("EXAMPLE_RELEASE_SUPPORT.local", "RELEASE_SUPPORT.local", "SUPPORT", "/epics/synAppsRelease/synApps/support")
    print("Copying RELEASE_LIBS.local. Tis contains the paths to the core libs used by AD. Should be automatically detected")
    copy_macro_replace("EXAMPLE_RELEASE_LIBS.local", "EX2_RELEASE_LIBS.local", "EPICS_BASE", "/epics/base-7.0.1.1")
    

generate_config_files()