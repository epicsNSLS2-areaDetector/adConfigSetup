# This is a script that can be used in combination with adConfigSetup
# to further automate the process of installing area detector.
#
# Author: Jakub Wlodek
# Copyright (c): Brookhaven National Laboratory
# Created on: October 15, 2018

#first install all of the dependant packages

sudo apt install libreadline-dev
sudo apt install libx11-dev
sudo apt install libboost-dev
sudo apt install libboost-test-dev
sudo apt install re2c
sudo apt install libxext-dev


# Next run the configure script

mv nsls2ADConfigSetup.py ../../.
cd ../..
python3 nsls2ADConfigSetup.py -r
cd ..

# Then compile ADSupport and AD Core

cd ADSupport
make -sj
cd ..

cd ADCore
make -sj
cd ..

# Then check the args for which driver to build
# NOTE: This will not install dependencies for specific drivers
for var in "$@"
do
    cd $var
    if[ $? -eq 0 ]; then
        make -sj
        cd ..
    else
        echo $var is not a valid AD driver
    fi

done
