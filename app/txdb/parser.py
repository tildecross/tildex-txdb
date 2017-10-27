import json
import core
from app.txdb.plugins import *

# NOTE: Replace self.valid checks and return False with exceptions

class TxDBParser:
    def __init__(self, db):
        if isinstance(db, TxDBCore):
            self.db = db
        else:
            self.db = None
        
    def _encode(self, data):
        return json.dumps(data)
    
    def _decode(self, data):
        return json.loads(data)
    
    def operation(self, jOp):
        pass
