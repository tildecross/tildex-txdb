from app import mongo
import os
import hashlib

def sha256(seed=None):
    m = hashlib.sha256()
    if seed != None:
        m.update(seed)
    else:
        m.update(os.urandom(32))
    return m.hexdigest()
