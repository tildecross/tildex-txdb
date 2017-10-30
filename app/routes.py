from flask import render_template, redirect, session, url_for, request, jsonify
import re
import os
import sys
import json
import time
import math
import hashlib
from pprint import pprint
from app import app, mongo

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/txdb")

from app.txdb.parser import TxDBParser
from app.txdb.core import TxDBCore

# type: obj -> str
def encode(data):
    return json.dumps(data)

# type: str -> obj
def decode(data):
    return json.loads(data)

def sha256(seed=None):
    m = hashlib.sha256()
    if seed is not None:
        m.update(seed)
    else:
        m.update(os.urandom(32))
    return m.hexdigest()

def get_store(item, name):
    service_name = item["service"]
    if service_name == "<internal>":
        service_name = "internal"
    
    store_name = "{}_{}".format(service_name, name)
    store = mongo.db[store_name]
    return {
        "store": store,
        "name": store_name
    }
    
def inc_usage(services_tuple, storage_tuple, usage):
    services = services_tuple[0]
    api_key = services_tuple[1]
    
    storage = storage_tuple[0]
    name = storage_tuple[1]
    
    print(storage)
    
    storage.update({"name": name}, 
                   {"$inc": {"usage": usage}})
    services.update({"api_key": api_key}, 
                    {"$inc": {"usage": usage}})

@app.route("/")
def index():
    title = "Tildex :: Database"
    service = "TxDB v{}".format(app.config["VERSION"])
    return render_template("index.html", title=title, service=service)

@app.route("/api/v1", methods=["GET"])
def welcome():
    return jsonify({
        "name": "welcome-message",
        "data": {
            "message": "Welcome to TxDB v{}".format(app.config["VERSION"]),
            "method": request.method
        }
    })

@app.route("/api/v1/services", methods=["GET"])
def get_services():
    services = mongo.db.services
    values = request.values
    api_key = values["api_key"] if "api_key" in values else None
    service = None
    result = {"name": "warning", "data": "Invalid request"}
    
    if api_key:
        s = services.find_one({"api_key": api_key})
        if s is not None:
            service = s
    
    if service:
        # entries = []
        del service["_id"]
        # for entry in service:
        #     entry.pop("_id", None)
        #     entries.append(entry)
        result["name"] = "services",
        result["data"] = service#[s["api_key"] for s in services.find()]
    else:
        result["name"] = "error"
        result["data"] = "Service does not exist"
    
    return jsonify({
        "name": result["name"],
        "data": result["data"]
    })
    
@app.route("/api/v1/services", methods=["POST"])
def post_services():
    services = mongo.db.services
    values = request.values
    app_key = values["app_key"] if "app_key" in values else None
    _name = values["name"] if "name" in values else None
    service = None
    result = {"name": "warning", "data": "Invalid request"}
    
    # {"name" : "<internal>", "api_key" : "<key>", "usage" : 326, "meta" : 0, "stores" : [] }
    
    if app_key and _name:
        name_regex = re.compile(r"^[a-z0-9-]+$")
        name = _name.lower()
        if name_regex.match(name):
            if app_key == app.config["APP_KEY"]:
                s = services.find_one({"name": name})
                if s is None:
                    service = {
                        "name": name,
                        "api_key": sha256(),
                        "usage": 0,
                        "meta": 0,
                        "stores": []
                    }
                    services.insert(service)
                    del service["_id"]
                    result["name"] = "services"
                    result["data"] = ["created", service]
                else:
                    result["name"] = "error"
                    result["data"] = "Service already exists"
            else:
                result["name"] = "error"
                result["data"] = "Wrong app_key was provided"
    
    return jsonify({
        "name": result["name"],
        "data": result["data"]
    })

@app.route("/api/v1/storage", methods=["POST"])
def post_storage():
    storage = mongo.db.storage
    services = mongo.db.services
    values = request.values
    api_key = values["api_key"] if "api_key" in values else None
    _name = values["name"] if "name" in values else None
    _data = values["data"] if "data" in values else None
    service = None
    result = {"name": "warning", "data": "Invalid request"}
    
    if api_key:
        s = services.find_one({"api_key": api_key})
        service = s if s else None
    
    if service:
        name_regex = re.compile(r"^[a-z0-9-]+$")
        _name = _name.lower()
        if _name and name_regex.match(_name):
            usage = 0
            item = storage.find_one({"api_key": api_key,
                                     "service": service["name"],
                                     "name": _name})
            database = TxDBCore("standard", modifier=item["modifier"], 
                plugins=["standard", "structured", "organized"])
            
            if item:
                store_info = get_store(item, _name)
                store_name = store_info.get("name", None)
                store = store_info.get("store", None)
                
                if store and store_name:
                    database.load(store)
                    if _data:
                        _instructions = decode(_data)
                        iop = _instructions.get("op", None)
                        iindex = _instructions.get("index", None)
                        idata = _instructions.get("data", None)
                        instructions = (iop, iindex, idata)
                        
                        output, usage = database.dispatch(instructions)
                        inc_usage((services, api_key), (storage, _name), usage)
                        
                        if output is not None:
                            result["name"] = item["name"]
                            result["data"] = output
                    else:
                        usage = database.cost
                        inc_usage((services, api_key), (storage, _name), usage)
                        
                        result["name"] = item["name"]
                        result["data"] = database.parse()
            else:
                if _data:
                    store_info = get_store(item, _name)
                    store_name = store_info.get("name", None)
                    store = store_info.get("store", None)
                    
                    storage.insert({"api_key": api_key, 
                                    "service": service["name"],
                                    "name": _name})
                    
                    inc_usage((services, api_key), (storage, _name), usage)
                                    
                    database.load(store)
                    
                    _instructions = decode(_data)
                    iop = _instructions.get("op", None)
                    iindex = _instructions.get("index", None)
                    idata = _instructions.get("data", None)
                    instructions = (iop, iindex, idata)
                    
                    output, usage = database.dispatch(instructions)
                    inc_usage((services, api_key), (storage, _name), usage)
                    
                    if output is not None:
                        result["name"] = item["name"]
                        result["data"] = output
                else:
                    #inc_usage((services, api_key), (storage, _name), usage)
                    result["name"] = "error"
                    result["data"] = "need data to initialize storage"
        else:
            result["name"] = "error"
            result["data"] = "no storage unit was specified"
    
    return jsonify({ "name": "storage", "data": result })
    
