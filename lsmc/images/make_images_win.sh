#!/bin/bash

set -e

PYTHON=c:/Python27/python

# Compile images to Python to make them easier to import

IMG2PY_SCRIPT=c:/Python27/Scripts/img2py
IMAGES_FILE=images.py

rm -f ${IMAGES_FILE}

# Load a blank image to initialize img2py's catalog
${IMG2PY_SCRIPT} -n blank -c -i blank.gif ${IMAGES_FILE}

for img in `ls *.png *.gif | grep -v blank.gif`
do
    img_name=`echo $img | cut -f1 -d.`

    $PYTHON ${IMG2PY_SCRIPT} -n ${img_name} -c -i -a ${img} ${IMAGES_FILE}
done
