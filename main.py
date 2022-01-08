import os
from config import companyId, liffId
from datetime import datetime
# from line_api import PushMessage
# from publish import publish_messages
from firestore_DAO import FirestoreDAO
from flask import Flask, request, render_template, jsonify, redirect, url_for
import threading
from datetime import datetime
from time import time

app = Flask(__name__)

firestoreDAO = FirestoreDAO(logger=app.logger)

user = {"is_logged_in": False, "id": "", "role": ""}

# Index
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        app.logger.info(user)
        return render_template("index.html", liffId = liffId)
    if request.method == 'POST':
        memberId = request.get_json(force=True)['id']
        app.logger.info(memberId)
        member = firestoreDAO.getMember({'companyId': companyId}, memberId)
        if member:
            user['is_logged_in'] = True
            user['id'] = member['id']
            user['role'] = member['role']
            app.logger.info(user)
        else:
            user['is_logged_in'] = False
            user['id'] = ""
            user['role'] = ""
        return render_template("index.html", liffId = liffId)

#  ------------------------------------------------------------------------------------------ 

# Sign Up 
@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        return render_template("signUp.html",liffId = liffId)
    if request.method == 'POST':
        try:
            return render_template("success.html", message="註冊成功")
        except:
            return render_template("error.html", message="註冊失敗") 

#  ------------------------------------------------------------------------------------------ 
# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html",liffId = liffId)
    if request.method == 'POST':
        try:
            return render_template("success.html", message="登入成功")
        except:
            return render_template("error.html", message="登入失敗") 

#  ------------------------------------------------------------------------------------------ 
# Binding 
@app.route("/binding", methods=['GET', 'POST'])
def binding():
    if request.method == 'GET':
        return render_template("binding.html",member = member,liffId = liffId)
    elif request.method == 'POST':
        return redirect(url_for('index'))
    
#  ------------------------------------------------------------------------------------------ 


# Member Register 
@app.route("/register/", methods=['POST'])
def register():
    memberData = request.get_json(force=True)
    member = firestoreDAO.addMember(memberData)
    # if "setMember" in member.keys():
    #     # - pubsub
    #     member["companyName"] = firestoreDAO.getCompanies({'companyId': companyId})[0]['name']
    #     publishThread = threading.Thread(target=publish_messages, args=({"member" : member},))
    #     publishThread.start()
    return jsonify(member)

#  ------------------------------------------------------------------------------------------ 
   
# Start Work 
@app.route("/start_work/<memberId>", methods=['GET', "POST"])
def start_work(memberId):
    return render_template('startWork.html', member_id=memberId)

@app.route("/submit/start", methods=['POST'])
def submit_start_work():
    data = request.get_json()
    app.logger.info(data)
    is_valid = firestoreDAO.addBeginOfWorkRecord(data)
    
    if is_valid:
        record = {
            'companyName': firestoreDAO.getCompanies({'companyId': companyId})[0]['name'],
            'memberId': data['memberId'],
            'location': f"{data['longitude']}, {data['latitude']}",
            'timestamp': datetime.utcfromtimestamp(time()+28800).strftime('%Y-%m-%d %H:%M:%S')
        }
        # publishThread = threading.Thread(target=publish_messages, args=({'startRecord': record},))
        # publishThread.start()
        message = 'Successfully submit your start work log'
        return redirect(url_for('success', message=message))
    else:
        message = 'Fail submit your start work log'
        return redirect(url_for('error', message=message))
  
#  ------------------------------------------------------------------------------------------ 
  
# End Work 
@app.route("/end_work/<memberId>", methods=['GET', 'POST'])
def end_work(memberId):
    return render_template('endWork.html', member_id=memberId)

@app.route("/submit/end", methods=['POST'])
def submit_end_work():
    data = request.get_json()
    app.logger.info(data)
    workTime = firestoreDAO.addEndOfWorkRecord(data)
    
    if workTime > 0:
        record = {
            'companyName': firestoreDAO.getCompanies({'companyId': companyId})[0]['name'],
            'memberId': data['memberId'],
            'location': f"{data['longitude']}, {data['latitude']}",
            'timestamp': datetime.utcfromtimestamp(time()+28800).strftime('%Y-%m-%d %H:%M:%S'),
            'workTime': workTime
        }
        # publishThread = threading.Thread(target=publish_messages, args=({'endRecord': record},))
        # publishThread.start()
        message = 'Successfully submit your end work log'
        return redirect(url_for('success', message=message))
    else:
        message = 'Fail submit your end work log'
        return redirect(url_for('error', message=message))

#  ------------------------------------------------------------------------------------------ 
 
# Leave Permission 
@app.route("/leave_permission/<memberId>", methods=['GET', 'POST'])
def leave_permission(memberId):
    return render_template('leavePermission.html', member_id=memberId)

@app.route("/submit/leave", methods=['POST'])
def submit_leave_permission():
    data = request.get_json()
    firestoreDAO.addDayOffRecord(data)
    return ''

#  ------------------------------------------------------------------------------------------ 
  
# Attendance 
@app.route("/attendance/<memberId>", methods=['GET'])
def attendance(memberId):
    beginOfWork, endOfWork, dayOff = firestoreDAO.getAttendenceRecords(memberId)
    app.logger.info(f"{beginOfWork}, {endOfWork}, {dayOff}")
    starts = []
    ends = []
    
    for begin in beginOfWork:
        iso_date = datetime.fromisoformat(begin['date'][:-1]) 
        date = iso_date.strftime("%Y-%m-%d")
        time = iso_date.strftime("%H:%M")
        starts.append(
            {
                "date": str(date),
                "time": str(time),
                "longitude": begin['longitude'],
                "latitude": begin['latitude'],
            }    
        )
    
    for end in endOfWork:
        iso_date = datetime.fromisoformat(end['date'][:-1]) 
        date = iso_date.strftime("%Y-%m-%d")
        time = iso_date.strftime("%H:%M")
        ends.append(
            {
                "date": str(date),
                "time": str(time),
                "longitude": end['longitude'],
                "latitude": end['latitude'],
            }    
        )
    return render_template('attendance.html', starts=starts, ends=ends, leaves=dayOff)

#  ------------------------------------------------------------------------------------------ 

# Personal Information 
@app.route("/personal_information/<memberId>", methods=['GET', 'POST'])
def personal_information(memberId):
    member = firestoreDAO.getMember({'companyId': companyId}, memberId)
    return render_template('personalInformation.html', member=member)

@app.route("/edit/<memberId>", methods=['GET', 'POST'])
def edit_user_data(memberId):
    member = firestoreDAO.getMember({'companyId': companyId}, memberId)
    return render_template('edit.html', member=member)

@app.route("/save", methods=['POST'])
def save_user_data():
    data = request.get_json()
    app.logger.info(data)
    firestoreDAO.updateMember(data)
    return ''

#  ------------------------------------------------------------------------------------------ 
  
# Company Information    
@app.route("/company_information/<memberId>", methods=['GET'])
def company_information(memberId):
    members = firestoreDAO.getMembers({'companyId': companyId})
    member = firestoreDAO.getMember({'companyId': companyId}, memberId)
    role = member['role'] if member is not None else None
    return render_template('companyInformation.html', companies=members, role=role)

#  ------------------------------------------------------------------------------------------ 

# Report 
@app.route("/report/<memberId>", methods=['GET'])
def report(memberId):
    member_id = memberId
    return render_template('report.html')

#  ------------------------------------------------------------------------------------------ 

# Success
@app.route("/success/<message>", methods=['GET'])
def success(message):
    return render_template('success.html', message=message)

#  ------------------------------------------------------------------------------------------ 

# Error
@app.route("/error/<message>", methods=['GET'])
def error(message):
    return render_template('error.html', message=message)

#  ------------------------------------------------------------------------------------------ 

port = int(os.environ.get('PORT', 8080))

if __name__ == '__main__':
    app.run(threaded=True, host='127.0.0.1', port=port)
