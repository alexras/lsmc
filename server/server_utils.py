import os, orm, db_utils, uuid, datetime

def has_extension(f, extension):
    return os.path.splitext(f.filename)[1] == extension

def get_uploaded_files(app, extension):

    return [f for f in db_utils.get_db().query(orm.SAVFile).all()]

def save_file(app, f, name):
    upload_dir = app.config["UPLOAD_DIR"]

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)

    # Create a unique folder in UPLOAD_DIR to hold the sav
    sav_obj = None

    db = db_utils.get_db()

    while sav_obj is None:
        sav_id = uuid.uuid4()

        if db.query(orm.SAVFile).filter(SAVFile.uuid(sav_id)).count() == 0:
            sav_obj = SAVFile(
                uuid=sav_id, name=name,
                date_uploaded = datetime.datetime.utcnow())

    directory_path = os.path.join(upload_dir, sav_obj.uuid)

    if not os.path.exists(directory_path):
        os.mkdir(directory_path)

    f.save(os.path.join(directory_path, "lsdj.sav"))

    db.commit()
