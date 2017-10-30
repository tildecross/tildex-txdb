import json
import math
from time import time
from copy import deepcopy

class Standard:
    def __init__(self, modifier, cost=1):
        self.type = "standard"
        self.modifier = ("unique", modifier)
        self.modifier = {"name": "unique", "data": modifier}
        self.store = None
        self.cost = cost
        
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
        if query is None:
            entries = []
            database = self.store.find()
            for entry in database:
                entry.pop("_id", None)
                entries.append(entry)
            return entries
        else:
            del query["_id"]
            return query
            
    # type: obj -> str
    def _encode(self, data):
        return json.dumps(data)
    
    # type: str -> obj
    def _decode(self, data):
        return json.loads(data)
    
    def add(self, data):
        if self.store is None:
            return None, 0
        
        if not data:
            return None, 0
        
        _data = deepcopy(data)
        data["ref"] = str(math.floor(time() * 10**6))
        usage = 0
        
        if self.modifier["data"]:
            # NOTE: ref will cause data to always be different
            if self.store.find_one(_data) is None:
                usage = len(self._encode(data))
                self.store.insert_one(data)
            else:
                # NOTE: No punishment for non-unique entries
                usage = -self.cost
        else:
            usage = len(self._encode(data))
            self.store.insert_one(data)
        
        return self.parse(), usage + self.cost
    
    def rem(self, index):
        if self.store is None:
            return None, 0
        
        if not index:
            return None, 0
        
        usage = 0
        search = self.store.find_one({"ref": index})
        if search:
            usage = -1 * len(self._encode(self.parse(query=search)))
        
        self.store.find_one_and_delete({"ref": index})
        return self.parse(), usage + self.cost
    
    # TODO: Add filtering using data<?>
    def get(self, index, data):
        if self.store is None:
            return None, 0
        
        if not (index or data):
            return None, 0
        
        if index and data:
            query = self.store.find_one({"ref": index}, projection=data)
            search = self.parse(query=query)
            return search, self.cost
        
        if index:
            search = self.parse(query=self.store.find_one({"ref": index}))
            return search, self.cost
        
        if data:
            search = self.parse(query=self.store.find_one(data))
            return search, self.cost
        
        return self.parse(), self.cost
    
    def set(self, index, data):
        if self.store is None:
            return None, 0
        
        if not (index and data):
            return None, 0
        
        usage = len(self._encode(data))
        
        self.store.find_one_and_update({"ref": index}, {
            "$set": data
        })
        return self.parse(), usage + self.cost
