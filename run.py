#!env/bin/python3

from app import app
app.run(debug=True, host="localhost", port=8202)
