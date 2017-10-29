Tildex :: TxDB
==============

Version: **TxDB v0.0.1**

*Currently under development, has not yet MVP specs*

This project is meant to be fill the role of something similar to Google's 
Firebase. TxDB itself will be an interface to access and manipulate a database 
for a service that can be shared among other authorized services over HTTP 
and/or sockets. Data will be piped in real-time to subscribed clients using 
websockets or upon request using AJAX. 

**Disclaimer:** I'm aware this may be a bad idea in production for any serious 
projects, but this mainly exists to understand how a service like this works 
internally and simply just for fun!

Dependencies
------------

* python3
* mongodb

Setup
-----

Once source has been downloaded, follow these steps:
```bash
$ cd path/of/project
$ python3 -m venv env
$ . env/bin/activate
$ pip3 install flask flask_pymongo
$ cp txdb.default.conf txdb.mongodb.conf
```

At this point you will need to provide the connection details for mongodb in 
`txdb.mongodb.conf`

Changelog
---------

* v0.0.1
    * Basic Flask structure setup
    * Integrated with MongoDB
    * Has foundation of TxDB packages functionality started
    * Basic infrastructure of databases put into place
    * Future goals to aim for established
* v0.0.2
    * Deprecated txdb.parser in favor of plugins
    * txdb.plugins, starting with standard, structured, and organized
    * Minimal model for txdb.plugins.standard
    * Renamed app/views.py to app/routes.py
    * Removed app/models.py
* v0.0.3
    * Implemented all txdb operations into routes

------
&copy; Copyright 2017, Tildecross under [the 3-Clause BSD License](LICENSE).
