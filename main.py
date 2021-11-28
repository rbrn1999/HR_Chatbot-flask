from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/start_work", methods=['GET'])
def start_work():
    return render_template('startWork.html')
  
@app.route("/end_work", methods=['GET'])
def end_work():
    return render_template('endWork.html')

@app.route("/leave_permission", methods=['GET'])
def leave_permission():
    return render_template('leavePermission.html')
  
@app.route("/attendance", methods=['GET'])
def attendance():
    return render_template('attendance.html')

@app.route("/personal_information", methods=['GET'])
def personal_information():
    return render_template('personalInformation.html')
  
@app.route("/company_information", methods=['GET'])
def company_information():
    return render_template('companyInformation.html')

@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')
