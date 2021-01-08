from flask import Flask, render_template, request, redirect, flash, url_for, g, session, jsonify
from flask_session import Session
from redis import StrictRedis
from datetime import datetime, timedelta
from jwt import encode
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import requests
from secrets import token_hex
import time

from os import getenv
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_PASS = getenv("REDIS_PASS")
SESSION_COOKIE_SECURE = getenv("SESSION_COOKIE_SECURE")
REDIS_DB = getenv("REDIS_DB")
JWT_SECRET = getenv("JWT_SECRET")
API_HOST = getenv("API_HOST")
JWT_EXP = 20
AUTH0_CALLBACK_URL = getenv("AUTH0_CALLBACK_URL")
AUTH0_CLIENT_ID = getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = getenv("AUTH0_DOMAIN")
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = getenv("AUTH0_AUDIENCE")


db = StrictRedis(REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASS, socket_connect_timeout=1)
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

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

def generate_sender_token(user):
    payload = {
        "iss":"paczkomatron authorization server",
        "sub":"sender",
        "usr":user,
        "aud":"paczkomatron api",
        "exp":datetime.utcnow() + timedelta(seconds = JWT_EXP)
    }
    token = encode(payload, JWT_SECRET, algorithm='HS256')
    #print(token, flush=True)
    return token

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

def get_user_notifications(login):
    notifs = db.zrevrange(f"notifications:{login}", 0, -1)
    dnotifs = []
    for notif in notifs:
        dnotifs.append(notif.decode())
    return dnotifs

def delete_user_notifications(login):
    db.delete(f"notifications:{login}")
    return

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
    is_oauth = session.get('oauth')
    session.clear()
    if is_oauth:
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    return redirect(url_for('index'))

@app.route('/sender/dashboard', methods=["GET"])
def sender_dashboard():
    if g.user is None:
        return redirect(url_for('sender_login'))
    user = g.user
    token = generate_sender_token(user)
    head = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(API_HOST + '/labels', headers=head).json()
    except:
        flash("Nie można połączyć się z api, spróbuj ponownie później")
        return redirect(url_for('index'))
    labels = response['_embedded']['labels']
    return render_template("sender_dashboard.html", labels=labels)

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
    label = {
        "name": name,
        "lockerid": lockerid,
        "size": size
    }
    token = generate_sender_token(user)
    head = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(API_HOST + '/labels', headers=head, json=label)
    except:
        flash("Nie można połączyć się z api, spróbuj ponownie później")
        return redirect(url_for('index'))
    if response.status_code != 200:
        flash("Błąd podczas dodawania etykiety")
    return redirect(url_for("sender_dashboard"))

@app.route('/sender/dashboard/<pid>', methods=["DELETE"])
def sender_dashboard_pid_delete(pid):
    if g.user is None:
        return "Unauthorized", 401
    user = g.user
    token = generate_sender_token(user)
    head = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(API_HOST + '/labels/'+pid, headers=head)
    except:
        flash("Nie można połączyć się z api, spróbuj ponownie później")
        return redirect(url_for('index'))
    if response.status_code != 200:
        return "Couldn't delete package", 400
    return "OK", 200

@app.route('/callback')
def callback():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    session["JWT_PAYLOAD"] = userinfo
    session["oauth"] = True
    session["login"] = userinfo['sub']
    if not is_user(session.get("login")):
        success = save_user("oauth", userinfo["nickname"], session["login"], userinfo["email"], token_hex(32), "oauthaddress")
        if not success:
            flash("Nie można utworzyć użytkownika, spróbuj później")
            session.clear()
            params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
            return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    return redirect('/sender/dashboard')

@app.route('/oauthlogin')
def oauth_login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/notifications')
def notifications():
    notifs = get_user_notifications(g.user)
    print(notifs, flush=True)
    if not notifs:
        return "", 204
    delete_user_notifications(g.user)
    return jsonify(notifs)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)