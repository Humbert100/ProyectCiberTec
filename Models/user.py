from email.policy import default
from tkinter import CASCADE
from Models.content import Content, contentSchema
from Models.reservations import Reservations, reservationSchema
from Models.frequency import frequencySchema, Frequency
from Models.shared import db
from sqlalchemy.orm import relationship
from marshmallow_sqlalchemy.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#Creacion del modelo de "User"
class User(db.Model):
    id          =   db.Column(db.Integer, primary_key=True)
    name        =   db.Column(db.String(100), nullable=False)
    email       =   db.Column(db.String(100), unique=True, nullable=False)
    pwd         =   db.Column(db.String(100), nullable=False)
    admin       =   db.Column(db.Integer, default=0)
    superAdmin  =   db.Column(db.Integer, default=0)
    tecAssociate=   db.Column(db.Integer)
    block       =   db.Column(db.Integer, default=0)
    verified    =   db.Column(db.Integer, default=1)
    Reservation =   db.relationship("Reservations", backref='user', cascade="all, delete")

    def updatedata(self):
        db.session.commit()

    def deletedata(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

#Se crea la clase Schema para poder crear "una  umna" para agregarla a la base de datos
class userSchema(SQLAlchemyAutoSchema):
    class Meta:
        model               = User
        load_instance       = True
        Reservation    = Nested(reservationSchema, many=True, allow_null=True, default=None)
        Frequen       = Nested(frequencySchema  , many=True, allow_null=True, default=None)