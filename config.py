import configparser
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# For mongodb
config = configparser.ConfigParser()
config.read("txdb.mongodb.conf")
MONGO_URI = "mongodb://{}:{}@{}:{}/{}".format(
    config.get("DB", "user"),
    config.get("DB", "password"),
    config.get("DB", "host"),
    config.get("DB", "port"),
    config.get("DB", "db"))
MONGO_DBNAME = config.get("DB", "db")
