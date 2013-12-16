from server import db

class SAVFile(db.Model):
    __tablename__ = 'savfiles'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36))
    name = db.Column(db.String(255))
    date_uploaded = db.Column(db.DateTime(timezone=True))
