from flask import Flask, render_template, request, redirect, flash, url_for, g, session, make_response
from flask_session import Session
from redis import StrictRedis
from datetime import datetime
import uuid

from os import getenv
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_PASS = getenv("REDIS_PASS")
SESSION_COOKIE_SECURE = True

db = StrictRedis(REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASS, socket_connect_timeout=1)
try:
    db.ping()
    SESSION_REDIS=db
    SESSION_TYPE = 'redis'
except:
    print("couldn't connect to database", flush=True)

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
ses = Session(app)
app.debug = False

from bcrypt import hashpw, gensalt, checkpw


def is_user(username):
    return db.hexists(f"user:{username}", "password")

def save_user(firstname, lastname, login, email, password, adress):
    hash = hashpw(password.encode(), gensalt(6))
    db.hset(f"user:{login}", "password", hash)
    db.hset(f"user:{login}", "firstname", firstname)
    db.hset(f"user:{login}", "lastname", lastname)
    db.hset(f"user:{login}", "email", email)
    db.hset(f"user:{login}", "adress", adress)
    return True

def authenticate_user(login, password):
    hash = db.hget(f"user:{login}", "password")
    if hash is None:
        return False
    return checkpw(password.encode(), hash)

def save_label(user, name, lockerid, size):
    pid = str(uuid.uuid4())
    db.sadd(f"packages:{user}", pid)
    db.hset(f"package:{pid}", "name", name)
    db.hset(f"package:{pid}", "lockerid", lockerid)
    db.hset(f"package:{pid}", "size", size)
    return True

def delete_label(user, pid):
    res1 = db.srem(f"packages:{user}", pid)
    res2 = db.delete(f"package:{pid}")
    if res1 == 0 or res2 == 0:
        return False
    return True

def get_sender_labels(user):
    labels = db.smembers(f"packages:{user}")
    labels = {label.decode() for label in labels}
    return labels

def get_labels_info(labels):
    labelsinfo = {}
    for label in labels:
        labelsinfo[label] = db.hgetall(f"package:{label}")
        labelsinfo[label] = {k.decode() : v.decode() for k,v in labelsinfo[label].items()}
    return labelsinfo

@app.before_request
def check_db():
    try:
        db.ping()
    except:
        return "Couldn't connect to database", 500

@app.before_request
def get_logged_login():
    g.user = session.get('login')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/checklogin/<login>', methods=["GET"])
def check_login(login):
    if (is_user(login)):
        return "unavailable", 200
    else:
        return "available", 200

@app.route('/sender/register', methods=["GET"])
def sender_signup():
    return render_template("sender_signup.html")

@app.route('/sender/register', methods=["POST"])
def sender_signup_post():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    login = request.form.get("login")
    email = request.form.get("email")
    password = request.form.get("password")
    adress = request.form.get("adress")
    if firstname is None:
        return "No first name provided", 400
    if lastname is None:
        return "No last name provided", 400
    if login is None:
        return "No login provided", 400
    if email is None:
        return "No email provided", 400
    if password is None:
        return "No password provided", 400
    if adress is None:
        return "No adress provided", 400
    if is_user(login):
        return "Username taken", 400
    
    success = save_user(firstname, lastname, login, email, password, adress)
    if not success:
        flash("Błąd podczas rejestracji użytkownika")
        return redirect(url_for('sender_signup'))
    return redirect(url_for('sender_login'))

@app.route('/sender/login', methods=["GET"])
def sender_login():
    return render_template("login.html")

@app.route('/sender/login', methods=["POST"])
def sender_login_post():
    login = request.form.get("login")
    password = request.form.get("password")
    
    if login is None:
        return "No login provided", 400
    if password is None:
        return "No password provided", 400
    
    if not authenticate_user(login, password):
        flash("Niepoprawny login lub hasło")
        return redirect(url_for('sender_login'))
    session["login"] = login
    session["login_time"] = datetime.utcnow()
    return redirect(url_for('index'))

@app.route('/sender/logout', methods=["GET"])
def sender_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/sender/dashboard', methods=["GET"])
def sender_dashboard():
    if g.user is None:
        return redirect(url_for('sender_login'))
    user = g.user
    labels = get_sender_labels(user)
    labelsinfo = get_labels_info(labels)
    return render_template("sender_dashboard.html", labels=labels, labelsinfo=labelsinfo)

@app.route('/sender/dashboard', methods=["POST"])
def sender_dashboard_post():
    if g.user is None:
        return "Unauthorized", 401
    user = g.user
    name = request.form.get("name")
    lockerid = request.form.get("lockerid")
    size = request.form.get("size")
    if name is None:
        return "No receipient name provided", 400
    if lockerid is None:
        return "No locker ID provided", 400
    if size is None:
        return "No package size provided", 400
    success = save_label(user, name, lockerid, size)
    if not success:
        flash("Błąd podczas dodawania etykiety")
    return redirect(url_for("sender_dashboard"))

@app.route('/sender/dashboard/<pid>', methods=["DELETE"])
def sender_dashboard_pid_delete(pid):
    if g.user is None:
        return "Unauthorized", 401
    user = g.user
    success = delete_label(user, pid)
    if not success:
        return "Couldn't delete package", 400
    return "OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)