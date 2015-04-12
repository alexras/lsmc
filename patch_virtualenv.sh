#!/bin/bash

# Unfortunately, there's a bug in py2app that prevents app bundling from
# working in a virtualenv. This script patches that bug.

VIRTUALENV_PY2APP_RECIPE=`find $VIRTUAL_ENV -name virtualenv.py | grep recipes`

sed -ibak -e 's/mf.scan_code/mf._scan_code/g' $VIRTUALENV_PY2APP_RECIPE
sed -ibak -e 's/mf.load_module/mf._load_module/g' $VIRTUALENV_PY2APP_RECIPE
