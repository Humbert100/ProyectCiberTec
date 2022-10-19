from email.policy import default
from sqlalchemy import delete
from Models.shared import db
from sqlalchemy.orm import relationship
from Models.reservations import Reservations, reservationSchema
from marshmallow_sqlalchemy.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Content(db.Model):
    id                  =   db.Column(db.Integer, primary_key=True)
    name                =   db.Column(db.String(100), nullable=False, unique=True)
    type                =   db.Column(db.String(100), nullable=False)
    description         =   db.Column(db.String, nullable=False)
    available           =   db.Column(db.Integer, default=1)
    reservation         =   db.relationship('Reservations', backref='content',  cascade="all, delete")

    def updatedata(self):
        db.session.commit()

    def deletedata(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class contentSchema(SQLAlchemyAutoSchema):
    class Meta:
        field = ('id', 'name', 'type', 'available')
        model = Content
        load_instance = True