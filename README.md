# AD Configuration Setup

This is a script that allows for rapid configuration of the Area Detector build process.

Previously, this required copying and editing several files. THe script allows the user
to specify which macros should be replaced by which values (usually paths), simplifying
pre-compilation configuration. 

### Installation:

The script is written with python3 in mind, so python3 must be installed to run the script. 
To prepare the script for use, place it into the 'configure' directory in the top level of
area detector. Place any external setup files here as well. An example external setup file can
be found in this repository as well.

## Running the script:

The script has two primary functions.
* Generate an external setup file
* Apply the external setup file to the area detector configuration

Generating a setup file could be useful if a certain configuration of area detector is desired for use on mutiple machines.

### Help:

To see the help message run:
```
python3 nsls2ADConfigSetup.py -h
```

### Generating a setup file:

When generating a setup file you have two options:

1) Generate a file with only required macros
2) Generate a file with all discovered macros

For the first case run:
```
python3 nsls2ADConfigSetup.py -g
```
and for the second case:
```
python3 nsls2ADConfigSetup.py -g -o
```
Both of these will generate a file called 'AD_SETUP_MACROS'. You may change the macro values directly in the file as well.

### Applying macros to the configuration files:

When applying macros to the configuration files, you have several options:

1. The '-r' flag will remove EXAMPLE files of different architectures from the workspace.
2. The '-o' flag will substitute the optional macros in addition to the required macros
3. The '-e' flag specifies if an external setup file is to be used.

Some example uses of the program are:
```
python3 nsls2ADConfigSetup -r -o -e EXTERNAL_FILE

python3 nsls2ADConfigSetup -o

python3 nsls2ADConfigSetup -r -e EXTERNAL_FILE
```

### Using the autoSetupAD.sh script:

The autoSetupAD.sh script allows for using the base functionality of the script and building area detector in one script call. To use the script, call it followed by the names of the drivers you wish to build. For example:
```
bash autoSetupAD.sh ADSpinnaker ADUVC ADProsilica.
```
The script will run the config setup with the default parameters, and
will remove non-pertinent example files from different architectures. After the configure directory is set up, the script will build ADSupport, then ADCore, and then whichever drivers or plugins were selected.

NOTES: 
* The names passed to the script must match the names of the directories the driver code is stored in.
* The script runs the python file in default mode, meaning that it is required to edit the python file itself to change the macros. (This may change in the future)

### Some future additions may include:

* Support for other architectures
* Ability to comment/uncomment macros