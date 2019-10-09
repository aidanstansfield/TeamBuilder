#!/usr/bin/env python3
from flask import Flask, request, render_template, redirect, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def test():
	return 'nani?'

@app.route('/ipw/')
def landing():
    return render_template('landing.html')

@app.route('/ipw/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/ipw/statistics')
def statistics():
    	# do fancy dbms stats and plots
	return render_template('stats.html')

if __name__ == "__main__":
	host = "0.0.0.0"
	port = 8080
	app.run(host, port, debug=True)

