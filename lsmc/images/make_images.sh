#!/bin/bash

set -e
set -x

# wx needs a framework build of Python in order to access the screen. The fwpy
# script will use the virtualenv's packages, but use the framework Python as
# its executable. We only need to do this in macOS, as far as I can tell, so
# we'll fallback to normal python if fwpy doesn't exist.
# The fwpy script can be found here: https://wiki.wxpython.org/wxPythonVirtualenvOnMac
PYTHON=fwpy
command -v fwpy >/dev/null 2>&1 || PYTHON=python

# Compile images to Python to make them easier to import

IMAGES_FILE=images.py

rm -f ${IMAGES_FILE}

# Load a blank image to initialize img2py's catalog
$PYTHON -m wx.tools.img2py -n blank -c -i blank.gif ${IMAGES_FILE}

for img in `ls *.png *.gif | grep -v blank.gif`
do
    img_name=`echo $img | cut -f1 -d.`

    $PYTHON -m wx.tools.img2py -n ${img_name} -c -i -a ${img} ${IMAGES_FILE}
done
