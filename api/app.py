from flask import Flask, request, g
from redis import StrictRedis
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link
from jwt import decode, encode
import json
import uuid
import time
import pika
from pika import credentials


from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_PASS = getenv("REDIS_PASS")
REDIS_DB = getenv("REDIS_DB")
JWT_SECRET = getenv("JWT_SECRET")
COUR_CLIENT_ID = getenv("COUR_CLIENT_ID")
COUR_PUBLIC_KEY = getenv("COUR_PUBLIC_KEY")
COUR_JWT_EXP = 3600
AUTH0_DOMAIN = getenv("AUTH0_DOMAIN")
AUTH0_ISSUER = 'https://' + AUTH0_DOMAIN +'/'
AUTH0_API_AUDIENCE = getenv("AUTH0_API_AUDIENCE")
MQ_HOST = getenv("MQ_HOST")
MQ_VH = getenv("MQ_VH")
MQ_LOGIN = getenv("MQ_LOGIN")
MQ_PASS = getenv("MQ_PASS")
credentials = pika.PlainCredentials(MQ_LOGIN, MQ_PASS)
parameters = pika.ConnectionParameters(MQ_HOST, 5672, MQ_VH, credentials)

db = StrictRedis(REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASS, socket_connect_timeout=1)
try:
    db.ping()
except:
    print("couldn't connect to database", flush=True)

app = Flask(__name__)
app.config.from_object(__name__)
app.debug = False

def save_label(user, name, lockerid, size):
    pid = str(uuid.uuid4())
    db.sadd(f"packages:{user}", pid)
    db.hset(f"package:{pid}", "name", name)
    db.hset(f"package:{pid}", "lockerid", lockerid)
    db.hset(f"package:{pid}", "size", size)
    db.hset(f"package:{pid}", "sender", user)
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

def get_all_labels():
    keys = db.keys("package:*")
    labels = []
    for key in keys:
        key = key.decode()
        s = key.split(":")
        labels.append(s[1])
    return labels

def get_all_packages():
    keys = db.keys("sentpkg:*")
    packages = []
    for key in keys:
        key = key.decode()
        s = key.split(":")
        packages.append(s[1])
    return packages

def get_packages_info(packages):
    packagesinfo = {}
    for package in packages:
        packagesinfo[package] = db.hgetall(f"sentpkg:{package}")
        packagesinfo[package] = {k.decode() : v.decode() for k,v in packagesinfo[package].items()}
    return packagesinfo

def create_package(pid):
    db.hset(f"sentpkg:{pid}", "pid", pid)
    db.hset(f"sentpkg:{pid}", "status", "w drodze")
    return True

def update_package_status(pid, status):
    db.hset(f"sentpkg:{pid}", "status", status)
    return True

def is_package(pid):
    return db.hexists(f"sentpkg:{pid}", "status")

def add_notif(pid, user, status):
    db.zadd(f"notifications:{user}", {f"Status paczki {pid} został zmieniony na: {status}":time.time()})
    return

def log_auth_error():
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='logs', exchange_type='topic')
    channel.basic_publish(exchange='logs', routing_key='api.error', body=f"({datetime.utcnow()}) Authorization error from IP: {request.remote_addr}")
    connection.close()
    return

def log_new_package(package):
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='invoices')
    channel.basic_publish(exchange='', routing_key='invoices', body=f"{json.dumps(package)}")
    connection.close()
    return

@app.before_request
def check_db():
    try:
        db.ping()
    except:
        return "Couldn't connect to database", 500

@app.before_request
def before_request_func():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    try:
      g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'], audience="paczkomatron api")
    except Exception:
      g.authorization = {}

@app.route('/', methods=['GET'])
def index():
    links = []
    links.append(Link('labels', '/labels'))
    links.append(Link('packages', '/packages'))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/labels', methods=['GET'])
def labels_list():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    if user is None or sub is None:
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    if sub == "sender":
        labels = get_sender_labels(user)
    elif sub == "courier":
        labels = get_all_labels()
    else:
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    labelsinfo = get_labels_info(labels)
    links = []
    links.append(Link('find', '/labels/{pid}', templated=True))
    items = []
    for label in labels:
        pid = label
        name = labelsinfo[pid]["name"]
        lockerid = labelsinfo[pid]["lockerid"]
        size = labelsinfo[pid]["size"]
        ilinks = []
        link = Link('self', '/labels/'+pid)
        ilinks.append(link)
        if (is_package(pid)):
            link = Link('package', '/packages/'+pid)
            ilinks.append(link)
        data = {'pid':pid, 'name':name, 'lockerid':lockerid, 'size':size}
        items.append(Embedded(data = data, links=ilinks))
    document = Document(embedded={'labels':Embedded(data=items)})
    return document.to_json()

@app.route('/labels', methods=['POST'])
def post_label():
    user = g.authorization.get('usr')
    if user is None:
        log_auth_error()
        return {"error":'Unauthorized'}, 401 
    label = request.json
    if label is None:
        return {"error":"No JSON label representation"}, 400
    try:
        name = label["name"]
        lockerid = label["lockerid"]
        size = label["size"]
    except:
        return {"error":"Incorrect JSON label representation"}, 400
    if len(name) == 0:
        return {"error":"No receipient name provided"}, 400
    if len(lockerid) == 0:
        return {"error":"No locker ID provided"}, 400
    if len(size) == 0:
        return {"error":"No package size provided"}, 400
    success = save_label(user, name, lockerid, size)
    if not success:
        return {"error":"Couldn't add label"}, 400
    links = []
    links.append(Link('labels', '/labels'))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/labels/<pid>', methods=['DELETE'])
def remove_label(pid):
    user = g.authorization.get('usr')
    if user is None:
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    if pid not in get_all_labels():
        return {"error":'No label with given id'}, 400
    if is_package(pid):
        return {"error":'Cannot delete label if package was created'}, 400
    success = delete_label(g.authorization.get('usr'), pid)
    if not success:
        return {"error":"Couldn't delete label"}, 400
    links = []
    links.append(Link('labels', '/labels'))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/packages', methods=['GET'])
def package_list():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    if user is None or sub is None or sub != "courier":
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    packages = get_all_packages()
    packagesinfo = get_packages_info(packages)
    links = []
    links.append(Link('find', '/packages/{pid}', templated=True))
    items = []
    for package in packages:
        pid = package
        status = packagesinfo[package].get("status")
        link = Link('self', '/packages/'+package)
        data = {'pid':pid, 'status':status}
        items.append(Embedded(data = data, links=[link]))
    document = Document(embedded={'packages':Embedded(data=items)})
    return document.to_json()

@app.route('/packages', methods=['POST'])
def add_package():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    if user is None or sub is None or sub != "courier":
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    package = request.json
    if package is None:
        return {"error":"No JSON package representation"}, 400
    try:
        pid = package["pid"]
    except:
        return {"error":"Incorrect JSON package representation"}, 400
    if len(pid) == 0:
        return {"error":"No package id provided"}, 400
    if pid not in get_all_labels():
        return {"error":"No label with provided id"}, 400
    if pid in get_all_packages():
        return {"error":"Package was already created"}, 400
    success = create_package(pid)
    log_new_package(get_labels_info([pid])[pid])
    add_notif(pid, get_labels_info([pid])[pid].get("sender"), "w drodze")
    if not success:
        return {"error":"Couldn't add package"}, 400
    links = []
    links.append(Link('packages', '/packages'))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/packages/<pid>', methods=['PUT'])
def update_package(pid):
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    if user is None or sub is None or sub != "courier":
        log_auth_error()
        return {"error":'Unauthorized'}, 401
    package = request.json
    if package is None:
        return {"error":"No JSON package representation"}, 400
    try:
        jpid = package["pid"]
        status = package["status"]
    except:
        return {"error":"Incorrect JSON package representation"}, 400
    if len(pid) == 0:
        return {"error":"No package id provided"}, 400
    if jpid != pid:
        return {"error":"Incorrect package id"}, 400
    if pid not in get_all_packages():
        return {"error":"No package with provided id"}, 400
    if status not in ["dostarczona", "odebrana"]:
        return {"error":"Incorrect status provided"}, 400
    packagesinfo = get_packages_info([pid])
    if packagesinfo[pid].get("status") == "odebrana" and status == "dostarczona":
        return {"error":"Cannot change status of received package"}, 400
    success = update_package_status(pid, status)
    add_notif(pid, get_labels_info([pid])[pid].get("sender"), status)
    if not success:
        return {"error":"Couldn't update package status"}, 400
    links = []
    links.append(Link('packages', '/packages'))
    document = Document(data = {}, links=links)
    return document.to_json()

def generate_courier_token(user):
    payload = {
        "iss":"paczkomatron authorization server",
        "sub":"courier",
        "usr":user,
        "aud":"paczkomatron api",
        "exp":datetime.utcnow() + timedelta(seconds = COUR_JWT_EXP)
    }
    token = encode(payload, JWT_SECRET, algorithm='HS256')
    #print(token, flush=True)
    return token

@app.route('/courier/jwt')
def courier_jwt():
    auth0accesstoken = request.headers.get('Authorization','').replace('Bearer ','')
    auth0idtoken = request.headers.get('IDToken','').replace('Bearer ','')
    try:
        decodedaccesstoken = decode(auth0accesstoken, COUR_PUBLIC_KEY, algorithms=['RS256'], audience=AUTH0_API_AUDIENCE, issuer=AUTH0_ISSUER)
        asub = decodedaccesstoken.get("sub")
    except Exception as e:
        log_auth_error()
        return "Bad access token", 400
    try:
        decodedidtoken = decode(auth0idtoken, COUR_PUBLIC_KEY, algorithms=['RS256'], audience=COUR_CLIENT_ID, issuer=AUTH0_ISSUER)
        isub = decodedidtoken.get("sub")
        if asub != isub or decodedaccesstoken.get("azp") != COUR_CLIENT_ID:
            return "Mismatched tokens", 400
        couriertoken = generate_courier_token(decodedidtoken.get("nickname"))
        return couriertoken, 200
    except Exception as e:
        log_auth_error()
        return "Bad ID token", 400
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)