import json

class Standard:
    def __init__(self, modifier):
        self.type = "standard"
        self.modifier = ("unique", modifier)
        
        self.meta = {}
        self.meta["type"] = self.type
        self.meta[self.modifier[0]] = self.modifier[1]
        
        self.db = [
            {"_meta": self.meta},
            list()
        ]
        
    def __call__(self, modifier):
        if self.modifier is not None:
            return self
        else:
            return None
        
    def __repr__(self):
        return "<Standard {}>".format(self.db[1])
    
    def parse(self):
        pass
    
    def _add(self, data):
        pass
    
    def _rem(self, index):
        pass
    
    def _get(self, index, data):
        pass
    
    def _set(self, index, data):
        pass
