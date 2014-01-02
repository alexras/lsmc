from server import db

class SAVFile(db.Model):
    __tablename__ = 'savfiles'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36))
    name = db.Column(db.String(255))
    date_uploaded = db.Column(db.DateTime(timezone=True))

class SAVFileProcessingProgress(db.Model):
    __tablename__ = 'processing_progress'

    id = db.Column(db.Integer, primary_key=True)
    sav_id = db.Column(db.Integer, db.ForeignKey("savfiles.id"), nullable=False)
    percent_complete = db.Column(db.Integer)
    status_message = db.Column(db.String(255))
    failed = db.Column(db.Boolean)
