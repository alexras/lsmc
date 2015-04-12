lsmc
----

Little Sound MC - a multitool for LSDJ .sav files

## Under Heavy Construction

This is almost done, but shouldn't be used for "production" purposes just yet.

Installing
==========

First, install lsmc's dependencies (you probably want to do this in a
virtualenv) by running the following from top-of-tree:

     pip install --upgrade -r requirements.txt \
       --allow-external wxPython \
       --allow-unverified wxPython \
       --allow-external ObjectListView \
       --allow-unverified ObjectListView



Now, you can build the app itself. On OS X, run:

    cd lsmc
    make build-mac

On Windows, run:

    cd lsmc
    make build-win

You may run into problems building inside a virtualenv on OS X (see
http://stackoverflow.com/questions/25394320/py2app-modulegraph-missing-scan-code). If
this is the case, run `patch_virtualenv.sh`.
