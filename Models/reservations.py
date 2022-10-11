import string
from sqlalchemy import Column
from Models.shared import db
from sqlalchemy.orm import relationship
from marshmallow_sqlalchemy.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Reservations(db.Model):
    id           =   db.Column(db.Integer , primary_key=True)
    startDate    =   db.Column(db.String  , nullable=False)
    endDate      =   db.Column(db.String  , nullable=False)
    userId       =   db.Column(db.Integer , db.ForeignKey("user.id"))
    contentId    =   db.Column(db.Integer , db.ForeignKey("content.id"))
    finish       =   db.Column(db.Integer , nullable=False, default=1)


    def save(self):
        db.session.add(self)
        db.session.commit()


class reservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservations
        load_instance = True