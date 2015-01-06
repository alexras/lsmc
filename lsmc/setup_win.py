from distutils.core import setup
import py2exe
import os
import sys
from glob import glob

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
    }
)
