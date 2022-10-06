from datetime import date, datetime,timedelta
import email
from importlib.resources import contents
from msilib.schema import Signature
from turtle import update
from flask import Flask, render_template, request, url_for, make_response, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from Models.reservations import reservationSchema, Reservations
from Models.user import User, userSchema
from Models.content import Content, contentSchema
from flask_jwt import JWT, jwt_required, current_identity
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re

#Se crea la app en flaks
app = Flask(__name__)
Bootstrap(app)
app.config.from_pyfile('config.cfg')
'''
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'uisongoku5@gmail.com'
app.config['MAIL_PASSWORD'] = 'GokuLeGana123'
app.config['MAIL_PORT']     = 587
}'''

bcrypt = Bcrypt(app)

#Se agrega la base de datos
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:8412@localhost/ctdb.db'
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI']  = 'postgresql://postgres:8412@localhost:5432/cybertecdb'
#Creamos llave secreta
app.config['SECRET_KEY'] = 'COOLDUDE'
#Se inicializa la base de datos 
db = SQLAlchemy(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)

mail_settings = {
    "MAIL_SERVER"
}


#Esta funcion sirve para reconocer que el usuario esta dado de alta
def authenticate(username, password):
    user = User.query.filter(User.email==username).first()
    if user and bcrypt.check_password_hash(user.pwd, password):
        return user

#obtenemos el id del usuario para saber su identidad
def identity(payload):
    user_id = payload['identity']
    return User.query.filter(User.id==user_id).first()

jwt = JWT(app, authenticate, identity)

@app.route("/")
def index():
    return render_template("index.html")

'''
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return '<form action="/" method="POST"><input name="email"><input type="submit"></form>'
    else:
        email       = request.form['email']
        token       = s.dumps(email, salt='email-confirm')

        msg         = Message('Confirm Email', sender='peposmith117@gmail.com', recipients=[email])
        link        = url_for('emailConfirmation', token=token, external=True)
        
        msg.body    = 'Your link is: {}'.format(link)

        mail.send(msg)

        return '<h1>The email was {}. We send an email so you can confirm your account with:{}</h1>'.format(email, token)
'''


@app.route('/emailConfirmation/<token>')
def emailConfirmation(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=300)
    except SignatureExpired:
        return '<h1>The token has expired</h1>'
    except BadSignature:
        return '<h1>The token is incorrect</h1>'
    return 'The token works!'

@app.route("/set")
def setcookie():
    resp = make_response('setting cookie!')
    resp.set_cookie('framework', 'flask')
    return resp

@app.route("/get")
def getcookie():
    return ''

@app.route("/user/create", methods=['POST']) #Creamos al usuario de esta manera
def creat_user():
    tec = '@tec.mx'
    body = request.get_json()
    user = User.query.filter_by(email=body.get("email")).first()
    if (user == None):
        assos = re.search(tec, body.get("email"))
        if(assos != None):
            body["tecAssociate"] = 1
        else:
            body["tecAssociate"] = 0
        email = body.get("email")
        token = s.dumps(email, salt='email-confirm') 
        user_schema = userSchema()
        user = user_schema.load(body, session=db.session)
        user.save()
        return user_schema.dump(user)
    else:
        return "Exist"

@app.route("/user/login", methods=["PUT"])
def userLogin():
    body = request.get_json()
    user = User.query.filter_by(email=body.get("email")).first()
    user_schema = userSchema()
    if (user != None):
        if(user.block == 1):
            if(body.get("pwd") == user.pwd):
                return user_schema.dumps(user)
            else:
                return "Wrong password"
        else:
            return "User not available"
    else:
        return "User not exist"
            

@app.route("/content/create", methods=['POST']) #Se crea un nuevo contenido:
def creat_content():
    body = request.get_json()
    cont = Content.query.filter_by(name=body.get("name")).first()
    if (cont == None):
        content_schema = contentSchema()
        content = content_schema.load(body, session=db.session)
        content.save()
        return content_schema.dump(Content) 
    return "Exist"

@app.route("/delete/content/<id>", methods=["DELETE"])
def delete_cont(id):
    cont = Content.query.filter_by(id=id).first()
    content_schema = contentSchema()
    cont.deletedata()
    
    return "Content succssesfully deleted"

@app.route("/delete/user/<id>", methods=["DELETE"])
def delete_user(id):
    user = User.query.filter_by(id=id).first()
    user_Schema = userSchema()
    user.deletedata()

    return "User successfully deleted"

@app.route("/getall/users", methods=["GET"])
def get_all_users():
    users = User.query.with_entities(User.id, User.name, User.email, User.admin, User.superAdmin, User.tecAssociate, User.block)
    user_schema = userSchema(many=True)
    return  user_schema.dumps(users)

@app.route('/mostwanted/content', methods=["GET"])
def most_wanted_content():
    mostW  = db.session.query(func.count(Reservations.contentId)) 
    print(mostW)
    return "ñiajara"
    
@app.route('/reservations/create', methods=["POST"])#Se crea una nueva reservacion con el ID del usuario y del objeto a reservar
def creat_reservation():
    body    = request.get_json()
    userId    = User.query.filter_by(id=body.pop("user")).first()
    contentId = Content.query.filter_by(id=body.pop("content")).first()
    start = body.pop("startDate")
    end = body.pop("endDate")
    Reservation_Schema = reservationSchema()
    content_Schema = contentSchema()
    body = Reservations(user=userId, content=contentId, startDate=start, endDate=end)
    body.save()

    return Reservation_Schema.dumps(body)

@app.route('/reservation/end/<id>', methods=["PUT"])
def reservation_finish(id):
    reservation = Reservations.query.filter(Reservations.id==id).first()
    resercation_schema = reservationSchema()

    reservation.finish = 1
    reservation.updatedata()

    return "resercation_schema.dumps(reservation)"

@app.route('/getcontent/<type>', methods=["GET"])
def get_content(type):
    content = Content.query.filter(Content.type==type).all()
    content_schema = contentSchema(many=True)
    return content_schema.dumps(content)

@app.route('/content/reservation', methods=["POST"])
def content_reservations():
    body = request.get_json()
    res = Reservations.query.filter(Reservations.startDate == body.get("Date")).filter(Reservations.contentId == body.get("content")).with_entities(Reservations.startHour, Reservations.endHour)
    reservation_schema = reservationSchema(many=True)
    return reservation_schema.dumps(res)

@app.route('/content/reservation/Software', methods=["POST"])
def content_reservations_soft():
    body = request.get_json()
    res = Reservations.query.filter(Reservations.startDate == body.get("Date")).filter(Reservations.contentId == body.get("content")).with_entities(Reservations.startDate, Reservations.endDate)
    reservation_schema = reservationSchema(many=True)
    return reservation_schema.dumps(res)

@app.route("/getall/content", methods=['GET'])
def get_all_content():
    cont = Content.query.all()
    content_schema = contentSchema(many=True)
    return content_schema.dumps(cont)

@app.route('/updateUser', methods=["PUT"])
def update_user_data():
    tec = '@tec.mx'
    user_schema = userSchema()
    body = request.get_json()
    userId = body.pop("id")
    assos = re.search(tec, body.get("email"))
    user = User.query.filter_by(id=userId).first()
    if(assos != None):
        user.tecAssociate = 1
    else:
        user.tecAssociate = 0
    user.email = body.get("email")
    user.pwd=bcrypt.generate_password_hash(body["pwd"])
    print(user_schema.dumps(user))
    user.updatedata()
    return "Change has been comited"

@app.route('/protected')
@jwt_required()
def protected():
    user_Schema=userSchema()
    return '%s' % user_Schema.dump(current_identity)

if __name__ == '__main__':
    app.run