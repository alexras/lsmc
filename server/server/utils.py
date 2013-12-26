import os, uuid, datetime
import orm

from server import db

def has_extension(f, extension):
    return os.path.splitext(f.filename)[1] == extension

def get_uploaded_files(app, extension):

    return [f for f in orm.SAVFile.query.all()]

def save_file(app, f, name):
    upload_dir = app.config["UPLOAD_DIR"]

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)

    # Create a unique folder in UPLOAD_DIR to hold the sav
    sav_obj = None

    while sav_obj is None:
        sav_id = str(uuid.uuid4())

        if orm.SAVFile.query.filter_by(uuid=sav_id).count() == 0:
            sav_obj = orm.SAVFile(
                uuid=sav_id, name=name,
                date_uploaded = datetime.datetime.utcnow())

    directory_path = os.path.join(upload_dir, sav_obj.uuid)

    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    f.save(os.path.join(directory_path, "lsdj.sav"))

    db.session.add(sav_obj)
    db.session.commit()

    return sav_id
