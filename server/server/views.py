from server import app, async, db
import server.utils as utils

import orm

from flask import request, render_template, send_from_directory, g, \
    session, redirect

@app.route("/upload")
def upload():
    return render_template("upload.jinja2", page_title="Add a .sav")

@app.route("/processing_progress/<sav_id>")
def processing_progress(sav_id):
    head_script = 'window.onload = updateProgress("%s", 500);' % (sav_id)

    return render_template("upload_progress.jinja2", sav_id=sav_id,
                           head_script=head_script)

@app.route("/file_select", methods=["POST"])
def upload_file():
    f = request.files["inputFile"]

    if not utils.has_extension(f, ".sav"):
        return render_template(
            "error.jinja2", page_title="Error",
            short_error="Invalid filename",
            long_error="File '%s' is not the name of "
            "a valid .sav file" % (f.filename),
            go_back_url="/upload")

    sav_id = utils.save_file(app, f, request.form["name"])

    sav_progress = orm.SAVFileProcessingProgress(
        sav_id=sav_id, percent_complete=0, status_message="", failed=False)

    db.session.add(sav_progress)
    db.session.commit()

    async.process_savfile.delay(sav_id)

    return redirect('/processing_progress/' + sav_id)

@app.route('/')
def start():
    sav_files = utils.get_uploaded_files(app, ".sav")

    return render_template(
        "start.jinja2", page_title="Home", sav_files=sav_files)
