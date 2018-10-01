# AD Configuration Setup

This is a script that allows for rapid configuration of the Area Detector build process.

Previously, this required copying and editing several files. THe script allows the user
to specify which macros should be replaced by which values (usually paths), simplifying
pre-compilation configuration. 

### Running the script

To run the script, place it in the top level configuration directory of AREA DETECTOR,
and run

```
python3 nsls2ADConfigSetup.py
```

### Some future additions may include:

* The ability to import a single macro - value pair file
* Support for other architectures
* Ability to comment/uncomment macros
* Some command line arguments to simplify script operation.