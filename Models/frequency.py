from Models.shared import db
from sqlalchemy.orm import relationship
from marshmallow_sqlalchemy.fields import Nested
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class Frequency(db.Model):
    id                  =   db.Column(db.Integer , primary_key=True)
    userId              =   db.Column(db.Integer , db.ForeignKey("user.id"))
    dayReservations     =   db.Column(db.Integer , nullable=False)
    date                =   db.Column(db.DateTime, nullable=False)


    def save(self):
        db.session.add(self)
        db.session.commit()

class frequencySchema(SQLAlchemyAutoSchema):
    class Meta:
        field = ('id', 'userId', 'dayReservations', 'date')
        model = Frequency
        load_instance = True