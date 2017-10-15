# TODO: Use 

class TxDBCore:
    def __init__(self, *args, **kwargs):
        _type = args[0]
        if not (_type == "standard" 
             or _type == "structured" 
             or _type == "organized"):
            _type = "standard"
        
        headers = kwargs.get("headers", [])
        state = kwargs.get("state", [])
        unique = kwargs.get("unique", False)
        
        self.meta = {
            "standard": {
                "type": _type,
                "unique": unique
            },
            "structured": {
                "type": _type,
                "headers": headers
            },
            "organized": {
                "type": _type,
                "state": state
            }
        }.get(_type)
        
        
        
        self.db = [
            {"_meta": self.meta},
            list()
        ]
        
    def __repr__(self):
        return "<TxDBCore %s>" % self.db[0]["_meta"]["type"]
        
    def load(self, database):
        pass
    
    def parse(self):
        pass
        
    def dispatch(self, instructions):
        op, index, data = instructions
        
        run = {
            "add": lambda i, d: _add(d),
            "rem": lambda i, d: _rem(i),
            "set": lambda i, d: _set(i, d),
            "get": lambda i, d: _get(i, d),
            "___": lambda i, d: _err("Operation does not exist")
        }.get(op, "___")
        
        return run(index, data)
        
    def _err(self, message):
        return {
            "error": "Error: %s!" % message
        }
        
    def _add(self, data):
        # TODO: Add conditions for non-standard schemas
        pass
    
    def _rem(self, index):
        # TODO: Add conditions for non-standard schemas
        pass
    
    def _get(self, index, data):
        # TODO: Add conditions for non-standard schemas
        pass
    
    def _set(self, index, data):
        # TODO: Add conditions for non-standard schemas
        pass
