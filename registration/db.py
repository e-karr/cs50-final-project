from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
Base = db.Model

def init_db(app):
    db.init_app(app)
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    Session = sessionmaker(bind=engine)

    # Reflect the existing tables from the database
    metadata = MetaData()
    Base.metadata.reflect(bind=engine)

    return engine, Session, metadata