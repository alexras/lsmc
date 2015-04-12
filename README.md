# lsmc

Little Sound MC - a multitool for LSDJ .sav files

## Under Heavy Construction

This is almost done, but shouldn't be used for "production" purposes just yet.

## Installing

### OS X

     cd lsmc
     make install-deps-mac
     make build-mac

### Windows

     cd lsmc
     make install-deps-win
     make build-win

You may run into problems building inside a virtualenv on OS X (see
http://stackoverflow.com/questions/25394320/py2app-modulegraph-missing-scan-code). If
this is the case, run `patch_virtualenv.sh`.
