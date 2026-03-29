from flask import Flask, jsonify, render_template

def init():
	global app

	app = Flask(__name__)

	@app.route("/")
	def index():
		return render_template("index.html")

def run():
	app.run(host="0.0.0.0", port=5000, debug=True)
