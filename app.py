import email
import json
import jwt
from flask import Flask, render_template, request, url_for, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, table, true, desc
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from Models.reservations import reservationSchema, Reservations
from Models.user import User, userSchema
from Models.content import Content, contentSchema
from datetime import datetime, timedelta, timezone
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import re
import hashlib

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
        jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
    except jwt.InvalidTokenError:
        print("There was an attempt to use an invalid JWT Signature")
        return False
    except Exception as e:
        print(e)
        return False
    else:
        return True

def getHours(date1, date2):
    date_obj1 = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S.%f")
    date_obj2 = datetime.strptime(date2, "%Y-%m-%d %H:%M:%S.%f")

    date_dif = date_obj2 - date_obj1
    date_dif = date_dif.total_seconds() / 60 ** 2
    return date_dif

@app.route('/emailConfirmagetion/<token>')
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
    userpwd = bytes(str(body["pwd"]), 'utf8')
    body["pwd"] = (hashlib.sha256((userpwd))).hexdigest()
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
        res = {"register":"exist"}
        return json.dumps(res)

@app.route("/user/create/app", methods=['POST']) #Creamos al usuario de esta manera
def creat_user_app():
    tec = '@tec.mx'
    body = request.get_json()
    user = User.query.filter_by(email=body.get("email")).first()
    print(user)
    userpwd = bytes(str(body["pwd"]), 'utf8')
    body["pwd"] = (hashlib.sha256((userpwd))).hexdigest()
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
        #user.save()
        res = {"register":"true"}
        return json.dumps(res)
    else:
        res = {"register":"exist"}
        return json.dumps(res)

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("jwt", expires=0)
    return resp

@app.route("/user/login", methods=["PUT"])
def userLogin():
    body = request.get_json()
    resp = make_response()
    user = User.query.with_entities(User.id, User.email, User.admin, User.superAdmin, User.pwd, User.block, User.verified).filter(User.email == body.get("email")).first()
    user_schema = userSchema()
    if (user != None):
        user = user_schema.dumps(user)
        user = json.loads(user)
        if(user["verified"] == 1):
            user.pop("block")
            user.pop("verified")
            userpwd = bytes(str(body["pwd"]), 'utf8')
            body["pwd"] = (hashlib.sha256((userpwd))).hexdigest()
            if(body.get("pwd") == user["pwd"]):
                user.pop("pwd")
                user["exp"] = datetime.now(timezone.utc) + timedelta(days=1)
                respbody = json.dumps({"authorized":1})
                resp.set_cookie("jwt", jwt.encode(user, TheKey, algorithm="HS256"), expires= datetime.now(timezone.utc) + timedelta(days=7))
            else:
                respbody = json.dumps({"authorized":"pwd"})
        else:
            respbody = json.dumps({"authorized":"available"})
    else:
        respbody = json.dumps({"authorized":"exist"})
    resp.set_data(respbody)
    return resp

@app.route("/user/login/app", methods=["POST"])
def user_login_app():
    body = request.get_json()
    user = User.query.filter(User.email == body.get("email")).first()
    user_schema = userSchema()
    if (user != None):
        user = user_schema.dumps(user)
        user = json.loads(user)
        if(user["verified"] == 1 or user["block"] == 0):
            user.pop("block")
            user.pop("verified")
            userpwd = bytes(str(body["pwd"]), 'utf8')
            body["pwd"] = (hashlib.sha256((userpwd))).hexdigest()
            if(body.get("pwd") == user["pwd"]):
                user.pop("pwd")
                JWT = jwt.encode(user, TheKey, algorithm="HS256")
                respbody = json.dumps({"authorized":"True", "JWT":JWT})
            else:
                respbody = json.dumps({"authorized":"pwd"})
        else:
            if(user["verified"] == 0):
                respbody = json.dumps({"authorized":"verified"})
            else:
                respbody = json.dumps({"authorized":"block"})
    else:
        respbody = json.dumps({"authorized":"user"})
    return respbody

@app.route("/doubleJSON", methods=["POST"])
def JSONTEST():
    body = request.get_json()
    JWT = jwt.encode(body, TheKey, algorithm="HS256")
    respbody = json.dumps({"nil":0, "JWT":JWT.decode()})
    return respbody

            
@app.route("/content/create", methods=['POST']) #Se crea un nuevo contenido:
def creat_content():
    body = request.get_json()
    cont = Content.query.filter(Content.name == body.get("name")).first()
    if (cont == None):
        content_schema = contentSchema()
        print("valido")
        content = content_schema.load(body, session=db.session)
        content.save()
        return content_schema.dump(content)
    return "Exist"

@app.route("/delete/content/<id>", methods=["DELETE"])
def delete_cont(id):
    cont = Content.query.filter_by(id=id).first()
    content_schema = contentSchema()
    cont.deletedata()
    
    return "Content succssesfully deleted"

@app.route("/delete/user", methods=["POST"])
def user_remove():
    body = request.get_json()
    body["userId"] = int(body["userId"])
    user = User.query.filter(User.id == body.get("id")).first()
    user.deletedata()
    return json.dumps({"confirmation": "True"})

@app.route("/update/user/data", methods=["POST"])
def update_user_info():
    body = request.get_json()
    resp = {}
    getUser = User.query.filter(User.id == body.get("id")).first()
    userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
    print(body["admin"] == "True")
    if (userdata["superAdmin"] == 1):
        if(body["admin"] == "True"):
            resp["admin"] = 1
            body["admin"] = 1
        else:
            resp["admin"] = 1
            body["admin"] = 0
    else:
        resp["admin"] = 0
        body["admin"] = 0
    if (body["block"] == "True"):
        body["block"] = 1
    else:
        body["block"] = 0
    resp["result"] = "done"
    getUser.admin = body["admin"]
    print(body["admin"])
    getUser.block = body["block"]
    getUser.updatedata()
    return json.dumps(resp)

@app.route("/getall/users", methods=["POST"])
def get_all_users():
    users = db.session.query(User).with_entities(User.id, User.email, User.name, User.admin, User.superAdmin, User.tecAssociate, User.block, User.verified).all()
    the_users ={}
    counter = 0
    for i in users:
        the_users[f"user_{counter}"] = {"id":           i["id"],
                                        "email":        i["email"],
                                        "name":         i["name"],
                                        "admin":        i["admin"],
                                        "superAdmin":   i["superAdmin"],
                                        "tecAssociate": i["tecAssociate"],
                                        "block":        i["block"],
                                        "verified":     i["verified"]
        }
        counter += 1
    return  the_users

@app.route('/mostwanted/content', methods=["GET"])
def most_wanted_content():
    mostW  = db.session.query(func.count(Reservations.contentId)) 
    print(mostW)
    return "ñiajara"
    
@app.route('/reservations/create', methods=["POST"])#Se crea una nueva reservacion con el ID del usuario y del objeto a reservar
def creat_reservation():
    body    = request.get_json()
    userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
    userId    = User.query.filter(User.id == userdata["id"]).first()
    contentId = Content.query.filter_by(id=body.pop("content")).first()
    start = body.pop("startDate")
    end = body.pop("endDate")
    Reservation_Schema = reservationSchema()
    content_Schema = contentSchema()
    body = Reservations(user=userId, content=contentId, startDate=start, endDate=end)
    print(body)
    body.save()

    return Reservation_Schema.dumps(body)

@app.route('/app/reservations/create', methods=["POST"])#Se crea una nueva reservacion con el ID del usuario y del objeto a reservar
def app_creat_reservation():
    body    = request.get_json()
    userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
    userId    = User.query.filter(User.id == userdata["id"]).first()
    contentId = Content.query.filter_by(id=body.pop("content")).first()
    start = body.pop("startDate")
    end = body.pop("endDate")
    Reservation_Schema = reservationSchema()
    body = Reservations(user=userId, content=contentId, startDate=start, endDate=end)
    body.save()

    return Reservation_Schema.dumps(body)

@app.route('/reservation/end/<id>', methods=["PUT"])
def reservation_finish(id):
    reservation = Reservations.query.filter(Reservations.id==id).first()
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

'''
@app.route('/updateUser', methods=["PUT"])
def update_user_data():
    if jwtValidated(request.cookies.get("jwt")):
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
        if (body["block"] == "True")
            user.block = 1
    
        user.email = body.get("email")
        userpwd = bytes(str(body["pwd"]), 'utf8')
        body["pwd"] = (hashlib.sha256((userpwd))).hexdigest()
        user.pwd= body["pwd"]
        
        print(user_schema.dumps(user))
        user.updatedata()
        return "Change has been comited"
'''
@app.route("/update/user/admin", methods=["PUT"])
def update_user_data_admin():
    body     = request.get_json()
    user = User.query.filteR(User.id == body["id"])
    userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
    if(userdata["superAdmin"] == 1):
        if (body["admin"] == "True"):
            user.admin = 1
    if(body["block"] == "True"):
        user.block = 1
    user.updatedata()
    return json.dumps({"confirmation": "True"})


@app.route("/historial/app/<id>", methods=["GET"])
def app_historial(id):
    userReservations = Reservations.query.filter(Reservations.userId == id).filter(Reservations.finish == 1)
    reservation_schema = reservationSchema(many=True)
    reservation_schema = reservation_schema.dumps(userReservations)
    reser = json.loads(reservation_schema)
    content_schema = contentSchema()
    for i in reser:
        content = Content.query.filter(Content.id == i["id"]).first()
        i.pop("id")
        contn = json.loads(content_schema.dumps(content))
        i["contentname"] = str(contn["name"])
        totalhours = getHours(i["startDate"], i["endDate"])
        i.pop("endDate")
        i.pop("finish")
        i["total"] = int(totalhours)
    print(reser)
    return(reser)


headings = {"Fecha de inicio", "Descripción", "Tiempo usado"}
@app.route('/pruebas')
def pruebas():
    if jwtValidated(request.cookies.get("jwt")):
        reser = [{'startDate': '2022-10-11 00:00:00.0', 'contentname': 'Microsoft de Word', 'total': 72}, {'startDate': '2022-10-09 12:00:00.0', 'contentname': 'Microsoft de PowerPoint', 'total': 6}, {'startDate': '2022-10-07 11:00:00.0', 'contentname': 'Licencia de Cisco Packet Tracer', 'total': 8}]
        return render_template("historial.html", headings=headings, data=reser)
    return redirect(url_for("homepage"))


'''
@app.route('/pruebas')
def pruebas():
    if jwtValidated(request.cookies.get("jwt")):
        data = []
        test = db.session.query(func.count(Reservations.id).label('qty')).group_by(Reservations.contentId).order_by(desc('qty'))
        print(test[1])
        #return render_template("pruebas.html")
        return "Hola"
    return redirect(url_for("index"))

@app.route('/pruebas')
def pruebas():
    contentFis  = Content.query.filter(Content.type == "EF").with_entities(Content.name, Content.description, Content.type)
    contenthard = Content.query.filter(Content.type == "hardware").with_entities(Content.name, Content.description, Content.type)
    contentsoft = Content.query.filter(Content.type == "software").with_entities(Content.name, Content.description, Content.type)
    content_schema = contentSchema(many=True)
    contentFis = content_schema.dumps(contentFis)
    contenthard = content_schema.dumps(contenthard)
    contentsoft = content_schema.dumps(contentsoft)
    data = []
    allcont = [json.loads(contentFis), json.loads(contenthard), json.loads(contentsoft)]
    for i in allcont:
        for j in i:
            data.append([(j["name"], j["type"], j["description"])])

    print(data)
    return render_template("pruebas.html")'''


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

@app.route('/crud/users')
def user_crud():
    if jwtValidated(request.cookies.get("jwt")):
        userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
        if (userdata["admin"] == 1):
            return render_template("adminUsers.html")
        return "<h1>Sorry, this view is only for admins</h1>"
    return redirect(url_for("index"))
        
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
        userdata = jwt.decode(request.cookies.get('jwt'), TheKey, algorithms="HS256")
        userReservations = Reservations.query.filter(Reservations.userId == userdata["id"]).filter(Reservations.finish == 1)
        reservation_schema = reservationSchema(many=True)
        reservation_schema = reservation_schema.dumps(userReservations)
        reser = json.loads(reservation_schema)
        content_schema = contentSchema()
        for i in reser:
            content = Content.query.filter(Content.id == i["id"]).first()
            i.pop("id")
            contn = json.loads(content_schema.dumps(content))
            i["contentname"] = str(contn["name"])
        print(reser)
        return render_template("historial.html", data=reser)
    return redirect(url_for("registro"))

@app.route('/homepage')
def homepage():
    print(jwt.decode(request.cookies.get("jwt"), app.config['SECRET_KEY'], algorithms="HS256"))
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
    res = Reservations.query.filter(Reservations.startDate == body.get("Date")).filter(Reservations.contentId == body.get("content")).with_entities(Reservations.startHour, Reservations.endHour, Content.name)
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
        contentFis  = Content.query.filter(Content.type == "EF")
        contenthard = Content.query.filter(Content.type == "hardware")
        contentsoft = Content.query.filter(Content.type == "software")
        content_schema = contentSchema(many=True)
        contentFis = content_schema.dumps(contentFis)
        contenthard = content_schema.dumps(contenthard)
        contentsoft = content_schema.dumps(contentsoft)
        allcont = [json.loads(contentFis), json.loads(contenthard), json.loads(contentsoft)]
    return redirect(url_for("registro"))

if __name__ == '__main__':
    app.debug = True
    app.run()