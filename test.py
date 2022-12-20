from flask import Flask, render_template, request, jsonify, json
from flask_sqlalchemy import SQLAlchemy  
from wtforms import SelectField
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kvkl_registration.db'

db = SQLAlchemy(app)



