# lsmc

Little Sound MC - a multitool for LSDJ .sav files

## Installing

First, download and install wxPython 3.0 [from their website][wxpython-download].

Then, run the following:

### On OS X

     cd lsmc
     make install-deps-mac
     make build-mac

### On Windows

     cd lsmc
     make install-deps-win
     make build-win

You may run into problems building inside a virtualenv on OS X (see
http://stackoverflow.com/questions/25394320/py2app-modulegraph-missing-scan-code). If
this is the case, run `patch_virtualenv.sh`.

[wxpython-download]: https://www.wxpython.org/download.php
