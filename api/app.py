from flask import Flask, request, g
from redis import StrictRedis
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link
from jwt import decode
import json
import uuid

from os import getenv
from dotenv import load_dotenv

load_dotenv()
REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = getenv("REDIS_PORT")
REDIS_PASS = getenv("REDIS_PASS")
REDIS_DB = getenv("REDIS_DB")
JWT_SECRET = getenv("JWT_SECRET")

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
def before_request_func():
    token = request.headers.get('Authorization','').replace('Bearer ','')
    try:
      g.authorization = decode(token, JWT_SECRET, algorithms=['HS256'], audience="paczkomatron api")
    except Exception:
      g.authorization = {}

@app.route('/', methods=['GET'])
def index():
    links = []
    links.append(Link('labels', '/labels', templated=True))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/labels', methods=['GET'])
def labels_list():
    user = g.authorization.get('usr')
    if user is None:
        return {"error":'Unauthorized'}, 401
    labels = get_sender_labels(user)
    labelsinfo = get_labels_info(labels)
    links = []
    links.append(Link('find', '/labels/{pid}', templated=True))
    items = []
    for label in labels:
        pid = label
        name = labelsinfo[pid]["name"]
        lockerid = labelsinfo[pid]["lockerid"]
        size = labelsinfo[pid]["size"]
        link = Link('self', '/labels/'+pid)
        data = {'pid':pid, 'name':name, 'lockerid':lockerid, 'size':size}
        items.append(Embedded(data = data, links=[link]))
    document = Document(embedded={'labels':Embedded(data=items)})
    return document.to_json()

@app.route('/labels', methods=['POST'])
def post_label():
    user = g.authorization.get('usr')
    if user is None:
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
    links.append(Link('labels', '/labels', templated=True))
    document = Document(data = {}, links=links)
    return document.to_json()

@app.route('/labels/<pid>', methods=['DELETE'])
def remove_label(pid):
    user = g.authorization.get('usr')
    if user is None:
        return {"error":'Unauthorized'}, 401 
    success = delete_label(g.authorization.get('usr'), pid)
    if not success:
        return {"error":"Couldn't delete label"}, 400
    links = []
    links.append(Link('labels', '/labels', templated=True))
    document = Document(data = {}, links=links)
    return document.to_json()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)