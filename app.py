from datetime import date, datetime,timedelta
import email
from importlib.resources import contents
import json
import jwt
from msilib.schema import Signature
from turtle import update
from flask import Flask, render_template, request, url_for, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone
from sqlalchemy import func, desc, true
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from Models.reservations import reservationSchema, Reservations
from Models.user import User, userSchema
from Models.content import Content, contentSchema
from flask_jwt import JWT, jwt_required, current_identity
from datetime import datetime, timedelta, timezone
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re

#Se crea la app en flaks
app = Flask(__name__)
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
#app.config['SQLALCHEMY_DATABASE_URI']  = 'postgresql://postgres:8412@localhost:5432/cybertecdb'
app.config['SQLALCHEMY_DATABASE_URI']  = 'postgresql://ijnatwzdlljnqr:4932ae038700539057441391fb51080a3a5c0151b3516b5690b06cecf923d49a@ec2-3-214-2-141.compute-1.amazonaws.com:5432/da670sf7r9h0kh'
#Creamos llave secreta
app.config['SECRET_KEY'] = 'COOLDUDE'
#Se inicializa la base de datos 
db = SQLAlchemy(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)

TheKey = app.config['SECRET_KEY']

mail_settings = {
    "MAIL_SERVER"
}


#Esta funcion sirve para reconocer que el usuario esta dado de alta
def authenticate(username, password):
    user = User.query.filter(User.email==username).first()
    if user and bcrypt.check_password_hash(user.pwd, password):
        return user

#obtenemos el id del usuario para saber su identidad

def creatJWT(jsnDict):
    return jwt.encode(jsnDict, app.config['SECRET_KEY'], algorithm="HS256")

def jwtValidated(token):
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithm="HS256")
    except jwt.InvalidTokenError:
        print("There was an attempt to use an invalid JWT Signature")
        return False
    except Exception as e:
        print(e)
        return False
    else:
        return True


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
        res = {"register":1}
        return json.dumps(res)
    else:
        res = {"register":"Exist"}
        return json.dumps(res)

@app.route("/user/login", methods=["PUT"])
def userLogin():
    body = request.get_json()
    resp = make_response()
    user = User.query.with_entities(User.id, User.email, User.admin, User.superAdmin, User.pwd, User.block).filter(User.email == body.get("email")).first()
    user_schema = userSchema()
    if (user != None):
        user = user_schema.dumps(user)
        user = json.loads(user)
        if(user["block"] == 1):
            user.pop("block")
            if(body.get("pwd") == user["pwd"]):
                user.pop("pwd")
                #user["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
                respbody = json.dumps({"authorized":1})
                resp.set_cookie("jwt", jwt.encode(user, TheKey, algorithm="HS256"))
            else:
                respbody = json.dumps({"authorized":"pwd"})
        else:
            respbody = json.dumps({"authorized":"available"})
    else:
        respbody = json.dumps({"authorized":"exist"})
    resp.set_data(respbody)
    return resp
            
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

@app.route("/app/delete/user/<id>", methods=["DELETE"])
def app_delete_user(id):
    user = User.query.filter_by(id=id).first()
    user_Schema = userSchema()
    user.deletedata()

    return "User successfully deleted"

@app.route("/getall/users", methods=["GET"])
def get_all_users():
    users = User.query.with_entities(User.id, User.name, User.email, User.admin, User.superAdmin, User.tecAssociate, User.block).filter(User.id == 1)
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

@app.route('/app/reservations/create', methods=["POST"])#Se crea una nueva reservacion con el ID del usuario y del objeto a reservar
def app_creat_reservation():
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

@app.route('/updateUser', methods=["PUT"])
def app_update_user_data():
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

'''RUTAS DE LA PAGINA PRINCIPAL'''
@app.route("/")
def index():
    if jwtValidated(request.cookies.get("jwt")):
        return redirect(url_for("homepage"))
    return render_template("index.html")

@app.route('/ajustes')
def ajustes():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("ajustes.html")
    return redirect(url_for("registro"))

@app.route('/ayuda')
def ayuda():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("ayuda.html")
    return redirect(url_for("registro"))

@app.route('/calender')
def calender():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("calender.html")
    return redirect(url_for("registro"))

@app.route('/codigo.html')
def codigo():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("codigo.html")
    return redirect(url_for("registro"))

@app.route('/confirmacion')
def confirmacion():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("confirmacion.html")
    return redirect(url_for("registro"))

@app.route('/error')
def error():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("error.html")
    return redirect(url_for("registro"))

@app.route('/historial')
def historial():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("historial.html")
    return redirect(url_for("registro"))

@app.route('/homepage')
def homepage():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("homepage.html")
    return redirect(url_for("registro"))

@app.route('/iniciosesion')
def iniciosesion():
    if jwtValidated(request.cookies.get("jwt")):
        return redirect(url_for("homepage"))
    return render_template("iniciosesion.html")

@app.route('/registro')
def registro():
    if jwtValidated(request.cookies.get("jwt")):
        return redirect(url_for("homepage"))
    return render_template("registro.html")

@app.route('/reservacionfis')
def reservacionfis():
    body = request.get_json()
    res = Reservations.query.filter(Reservations.startDate == body.get("Date")).filter(Reservations.contentId == body.get("content")).with_entities(Reservations.startHour, Reservations.endHour)
    reservation_schema = reservationSchema(many=True)
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("reservacionfis.html")
    return redirect(url_for("registro"))

@app.route('/reservacionhard')
def reservacionhard():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("reservacionhard.html")
    return redirect(url_for("registro"))

@app.route('/reservacionsoft')
def reservacionsoft():
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("reservacionsoft.html")
    return redirect(url_for("registro"))

@app.route('/reservahome')
def reservahome():
    cont = Content.query.all()
    content_schema = contentSchema(many=True)
    if jwtValidated(request.cookies.get("jwt")):
        return render_template("reservahome.html")
    return redirect(url_for("registro"))

if __name__ == '__main__':
    app.run