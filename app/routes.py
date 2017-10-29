from flask import render_template, redirect, session, url_for, request, jsonify
import os
import sys
import json
import time
import math
from pprint import pprint
from app import app, mongo

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/txdb")

from app.txdb.parser import TxDBParser
from app.txdb.core import TxDBCore

database = TxDBCore("standard", modifier=True, plugins=[
    "standard", "structured", "organized"
])

# type: obj -> str
def encode(data):
    return json.dumps(data)

# type: str -> obj
def decode(data):
    return json.loads(data)

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

# NOTE: This exists purely for debugging purposes, remove in production
@app.route("/api/v1/services", methods=["GET", "POST"])
def handle_services():
    services = mongo.db.services
    values = request.values
    api_key = values["api_key"] if "api_key" in values else None
    service = None
    if api_key:
        s = services.find_one({"api_key": api_key})
        service = s["name"] if s else None
    
    return {
        "GET": jsonify({
            "name": "services",
            "data": [s["name"] for s in services.find()]
        }),
        "POST": jsonify({
            "name": "service",
            "data": service
        })
    }[request.method]

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
        if _name:            
            item = storage.find_one({"api_key": api_key,
                                     "service": service["name"],
                                     "name": _name})
            
            if item:
                service_name = item["service"]
                if service_name == "<internal>":
                    service_name = "internal"
                
                store_name = "{}_{}".format(service_name, _name)
                store = mongo.db[store_name]
                
                database.load(store)
                if _data:
                    _instructions = decode(_data)
                    iop = _instructions.get("op", None)
                    iindex = _instructions.get("index", None)
                    idata = _instructions.get("data", None)
                    instructions = (iop, iindex, idata)
                    
                result["name"] = item["name"]
                result["data"] = database.dispatch(instructions)
            else:
                if _data:
                    service_name = item["service"]
                    if service_name == "<internal>":
                        service_name = "internal"
                    
                    store_name = "{}_{}".format(service_name, _name)
                        
                    storage.insert({"api_key": api_key, 
                                    "service": service["name"],
                                    "name": _name})
                                    
                    store = mongo.db[store_name]
                    database.load(store)
                    
                    _instructions = decode(_data)
                    iop = _instructions.get("op", None)
                    iindex = _instructions.get("index", None)
                    idata = _instructions.get("data", None)
                    instructions = (iop, iindex, idata)
                    
                    result["name"] = item["name"]
                    result["data"] = database.dispatch(instructions)
                else:
                    result["name"] = "error"
                    result["data"] = "need data to initialize storage"
        else:
            result["name"] = "error"
            result["data"] = "no storage unit was specified"
    
    return jsonify({ "name": "storage", "data": result })
    
