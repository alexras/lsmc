from distutils.core import setup
import py2exe
from glob import glob
import sys

sys.path.append(r'C:\\Program Files\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT')

setup(
    windows=[{
        "script": "LSMC",
        "dest_name": "LSMC"
    }],
    options={
        'py2exe': {
            'bundle_files': 1,
            'packages': ['wx.lib.pubsub', 'pylsdj']
        }
    }
)
