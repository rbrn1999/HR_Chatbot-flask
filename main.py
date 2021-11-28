from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/start_work", methods=['GET'])
def start_work():
    return render_template('startWork.html')
  
@app.route("/end_work", methods=['GET'])
def end_work():
    return render_template('endWork.html')
