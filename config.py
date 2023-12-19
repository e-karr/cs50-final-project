import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY=os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(basedir, "kvkl_registration.db")
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    TEMPLATES_AUTO_RELOAD=True
    SESSION_PERMANENT=False
    SESSION_TYPE="filesystem"