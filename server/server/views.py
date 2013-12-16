from server import app
import server.utils as utils

from flask import request, render_template, send_from_directory, g, \
    session, redirect

@app.route("/upload")
def upload():
    return render_template("upload.jinja2", page_title="Add a .sav")

@app.route("/file_select", methods=["POST"])
def upload_file():
    print request, request.form, request.files
    f = request.files["inputFile"]

    if not utils.has_extension(f, ".sav"):
        return render_template(
            "error.jinja2", page_title="Error",
            short_error="Invalid filename",
            long_error="File '%s' is not the name of "
            "a valid .sav file" % (f.filename),
            go_back_url="/upload")

    utils.save_file(app, f, request.form["name"])

    return redirect('/')

@app.route('/')
def start():
    sav_files = utils.get_uploaded_files(app, ".sav")

    return render_template(
        "start.jinja2", page_title="Home", sav_files=sav_files)
