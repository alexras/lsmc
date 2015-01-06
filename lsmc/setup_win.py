from distutils.core import setup
import py2exe
import os
import sys
from glob import glob

DATA_FILES = []

for filename in os.listdir('images/'):
    filename = os.path.abspath(filename)

    if os.path.isfile(filename):
        DATA_FILES.append(('images', [filename]))

setup(
    windows=[{
        "script": "LSMC",
        "dest_name": "LSMC"
    }],
    options={
        'py2exe': {
            'bundle_files': 1,
            'packages': ['wx.lib.pubsub']
        }
    },
    data_files=DATA_FILES
)
