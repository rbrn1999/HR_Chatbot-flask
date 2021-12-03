import os
import config
# from line_api import PushMessage
from firestore_DAO import FirestoreDAO
from flask import Flask, request, render_template, jsonify, redirect, url_for

image_folder = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = image_folder

firestoreDAO = FirestoreDAO(logger=app.logger)

# Member Register 
@app.route("/register", methods=['POST'])
def register():
    memberData = request.get_json(force=True)
    member = firestoreDAO.setMember(memberData)
    # if "setMember" in member.keys():
    #     # - pubsub
    #     member["companyName"] = firestoreDAO.getCompanies({'companyId': config.companyId})[0]['name']
    #     publishThread = threading.Thread(target=publish_messages, args=({"member" : member},))
    #     publishThread.start()
    return jsonify(member)

#  ------------------------------------------------------------------------------------------ 
   
# Start Work 
@app.route("/start_work", methods=['GET', "POST"])
def start_work():
    # Member ID
    member_id = 107590061
    
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'start-work.png')
    return render_template('startWork.html', image=image, member_id=member_id)

@app.route("/submit/start", methods=['GET', 'POST'])
def submit_start_work():
    data = request.get_json()
    app.logger.info(data)
    is_valid = firestoreDAO.addBeginOfWorkRecord(data)
    
    if (is_valid):
        message = 'Successfully submit your start work log'
        return redirect(url_for('success', message=message))
    else:
        message = 'Fail submit your start work log'
        return redirect(url_for('error', message=message))
  
#  ------------------------------------------------------------------------------------------ 
  
# End Work 
@app.route("/end_work", methods=['GET', 'POST'])
def end_work():
    # Member ID
    member_id = 107590061
    
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'end-work.png')
    return render_template('endWork.html', image=image, member_id=member_id)

@app.route("/submit/end", methods=['POST'])
def submit_end_work():
    data = request.get_json()
    app.logger.info(data)
    is_valid = firestoreDAO.addBeginOfWorkRecord(data)
    
    if (is_valid):
        message = 'Successfully submit your end work log'
        return redirect(url_for('success', message=message))
    else:
        message = 'Fail submit your end work log'
        return redirect(url_for('error', message=message))

#  ------------------------------------------------------------------------------------------ 
 
# Leave Permission 
@app.route("/leave_permission", methods=['GET', 'POST'])
def leave_permission():
    # Member ID
    member_id = 107590061
    
    return render_template('leavePermission.html', member_id=member_id)

@app.route("/submit/leave", methods=['POST'])
def submit_leave_permission():
    data = request.get_json()
    firestoreDAO.addDayOffRecord(data)
    return ''

#  ------------------------------------------------------------------------------------------ 
  
# Attendance 
@app.route("/attendance", methods=['GET'])
def attendance():
    fake_data = [
        {
            'date': '2021-06-09',
            'start': '08:00',
            'end': '17:00',
            'total_time': '04:00',
            'location': 'longitude, latitude',
            'ask_for_leave': 'yes'
        },
        {
            'date': '2021-06-09',
            'start': '08:00',
            'end': '17:00',
            'total_time': '04:00',
            'location': 'longitude, latitude',
            'ask_for_leave': 'no'
        },
        {
            'date': '2021-06-09',
            'start': '08:00',
            'end': '17:00',
            'total_time': '04:00',
            'location': 'longitude, latitude',
            'ask_for_leave': 'no'
        },
    ]
    return render_template('attendance.html', attendances=fake_data)

#  ------------------------------------------------------------------------------------------ 

# Personal Information 
@app.route("/personal_information", methods=['GET', 'POST'])
def personal_information():
    return render_template('personalInformation.html')

@app.route("/save", methods=['POST'])
def save_user_data():
    data = request.get_json()
    firestoreDAO.updateMember(data)
    return ''

#  ------------------------------------------------------------------------------------------ 
  
# Company Information 
@app.route("/company_information", methods=['GET'])
def company_information():
    members = firestoreDAO.getMembers({'companyId': config.companyId})
    memberId = ''
    member = firestoreDAO.getMember({'companyId': config.companyId}, memberId)
    role = member['role'] if member is not None else None
    role = 'manager'
    fake_data = [
        {
           'member_id': 'qwertyuiop',
           'name': 'audi',
           'role': 'worker',
           'salary': 180,
        },
        {
           'member_id': 'assdfghjkl',
           'name': 'john',
           'role': 'manager',
           'salary': 180,
        }
    ]
    return render_template('companyInformation.html', companies=fake_data, role=role)

#  ------------------------------------------------------------------------------------------ 

# Report 
@app.route("/report", methods=['GET'])
def report():
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
