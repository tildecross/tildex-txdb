import json
import math
from time import time
from copy import deepcopy

class Standard:
    def __init__(self, modifier):
        self.type = "standard"
        self.modifier = ("unique", modifier)
        self.modifier = {"name": "unique", "data": modifier}
        self.store = None
        
        self.meta = {}
        self.meta["type"] = self.type
        self.meta[self.modifier["name"]] = self.modifier["data"]
        
        self.db = [
            {"_meta": self.meta},
            self.store
        ]
        
    def __call__(self, modifier):
        if self.modifier is not None:
            return self
        else:
            return None
    
    # NOTE: Displays length and last item
    def __repr__(self):
        return "<Standard <{}>: {}>".format(len(self.db[1]), self.db[1][-1])
    
    def load(self, store):
        self.store = store
        self.db[1] = self.store
    
    def parse(self, query=None):
        entries = []
        database = self.store.find() if query is None else query
        for entry in database:
            entry.pop("_id", None)
            entries.append(entry)
        return entries
        
    # type: obj -> str
    def _encode(self, data):
        return json.dumps(data)
    
    # type: str -> obj
    def _decode(self, data):
        return json.loads(data)
    
    def add(self, data):
        if self.store is None:
            return None
        
        # data is JSON string, jdata is object
        jdata = self._decode(data)
        _data = deepcopy(jdata)
        jdata["ref"] = math.floor(time() * 10**6)
        
        if self.modifier["data"]:
            # NOTE: ref will cause jdata to always be different
            if self.store.find_one(_data) is None:
                self.store.insert_one(jdata)
        else:
            self.store.insert_one(jdata)
            
        return self.parse()
    
    def rem(self, index):
        if self.store is None:
            return None
        
        if index > len(self.store.find()):
            return self.parse()
        
        self.store.find_one_and_delete({"ref": index})
        return self.parse()
    
    # TODO: Add filtering using data<?>
    def get(self, index, data):
        if self.store is None:
            return None
        
        # data is JSON string, jdata is object
        jdata = self._decode(data)
        
        if index > len(self.db[1]):
            return None
        
        return self.parse(self.store.find_one(jdata))
    
    def set(self, index, data):
        if self.store is None:
            return None
        
        # data is JSON string, jdata is object
        jdata = self._decode(data)
        
        if index > len(self.store.find()):
            return self.parse()
        
        self.store.find_one_and_replace({"ref": index}, {
            "$set": data
        })
        return self.parse()
