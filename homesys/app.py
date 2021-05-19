from homesys import app, system
from flask import Flask, render_template, Response


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/live")
def livefeed():
    return Response(system.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
