from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db=SQLAlchemy()
class Usuario(UserMixin,db.Model):
 id=db.Column(db.Integer,primary_key=True)
 nombre=db.Column(db.String(100))
 correo=db.Column(db.String(100),unique=True)
 password=db.Column(db.String(255))
 rol=db.Column(db.String(20),default='cliente')
