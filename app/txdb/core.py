from app.txdb.plugins import *

class TxDBCore:
    def __init__(self, *args, **kwargs):
        modifier = kwargs.get("modifier", None)
        plugins = kwargs.get("plugins", [])
        
        self.plugins = self._load_plugins(plugins)
        self.modifier = modifier
        self.type = args[0]
        
        if self.type in self.plugins:
            self.model = self.plugins[self.type](self.modifier)
            self.db = self.model.db
        else:
            print("Error! :(")
        
    def __repr__(self):
        return "<TxDBCore {}>".format(self.db[0]["_meta"]["type"])
    
    def _load_plugins(self, plugins):
        _plugins = {}
        for plugin in plugins:
            pname = "{}{}".format(plugin[0].upper(), plugin[1:])
            if pname in globals():
                _plugins[plugin] = globals()[pname]
        return _plugins
        
    def load(self, database):
        self.model.load(database)
    
    def parse(self):
        return self.model.parse()
        
    def dispatch(self, instructions):
        op, index, data = instructions
        
        run = {
            "add": lambda i, d: self._add(d),
            "rem": lambda i, d: self._rem(i),
            "set": lambda i, d: self._set(i, d),
            "get": lambda i, d: self._get(i, d),
            "___": lambda i, d: self._err("Operation does not exist")
        }.get(op, "___")
        
        return run(index, data)
        
    def _err(self, message):
        return {
            "error": "Error: %s!" % message
        }
        
    def _add(self, data):
        return self.model.add(data)
    
    def _rem(self, index):
        return self.model.rem(index)
    
    def _get(self, index, data):
        return self.model.get(index, data)
    
    def _set(self, index, data):
        return self.model.set(index, data)
