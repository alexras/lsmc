#!/usr/bin/env python

import os, sys, server_utils, db_utils

from flask import Flask, request, render_template, send_from_directory, g, \
    session, redirect

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["UPLOAD_DIR"] = os.path.join(SCRIPT_DIR, "uploads")

@app.teardown_appcontext
def close_connection(exception):
    db_utils.close_db()

@app.route("/upload")
def upload():
    return render_template("upload.jinja2", page_title="Add a .sav")

@app.route("/file_select", methods=["POST"])
def upload_file():
    f = request.files["inputFile"]

    if not server_utils.has_extension(f, '.sav'):
        return render_template(
            "error.jinja2", page_title="Error",
            short_error="Invalid filename",
            long_error="File '%s' is not the name of "
            "a valid .sav file" % (f.filename),
            go_back_url="/upload")

    server_utils.save_file(app, f)

    return redirect('/')

@app.route('/')
def start():
    sav_files = server_utils.get_uploaded_files(app, ".sav")

    return render_template(
        "start.jinja2", page_title="Home", sav_files=sav_files)

if __name__ == "__main__":
    app.run(debug=True)
