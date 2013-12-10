import os

def has_extension(f, extension):
    return os.path.splitext(f.filename)[1] == extension

def get_uploaded_files(app, extension):
    if not os.path.exists(app.config["UPLOAD_DIR"]):
        os.mkdir(app.config["UPLOAD_DIR"])

    return filter(lambda x: x[:-4] == extension,
                  os.listdir(app.config["UPLOAD_DIR"]))

def save_file(app, f):
    pass
