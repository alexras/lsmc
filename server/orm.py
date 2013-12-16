from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE = "sqlite://%s" % (os.path.join(SCRIPT_DIR, "database.db"))

engine = create_engine(DATABASE, echo=True)
db_session = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = db_session.query_property()

class SAVFile(Base):
    __tablename__ = 'savfiles'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(36))
    name = Column(String(255))
    date_uploaded = Column(DateTime(timezone=True))
