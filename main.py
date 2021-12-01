import os
# from line_api import PushMessage
# from firestore_DAO import FirestoreDAO
from flask import Flask, request, render_template, jsonify

image_folder = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = image_folder

# firestoreDAO = FirestoreDAO()

# # Member Register 
# @app.route("/register", methods=['POST'])
# def register():
#     memberData = request.get_json(force=True)
#     member = firestoreDAO.setMember(memberData)
#     # if "setMember" in member.keys():
#     #     # - pubsub
#     #     member["companyName"] = firestoreDAO.getCompanies({'companyId': config.companyId})[0]['name']
#     #     publishThread = threading.Thread(target=publish_messages, args=({"member" : member},))
#     #     publishThread.start()
#     return jsonify(member)

#  ------------------------------------------------------------------------------------------ 
   
# Start Work 
@app.route("/start_work", methods=['GET', "POST"])
def start_work():
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'start-work.png')
    return render_template('startWork.html', image=image)

@app.route("/submit/start", methods=['POST'])
def submit_start_work():
    date = request.get_json()['date']
    longitude = request.get_json()['longitude']
    latitude = request.get_json()['latitude']
    print(date, longitude, latitude)
    return render_template('success.html')
  
#  ------------------------------------------------------------------------------------------ 
  
# End Work 
@app.route("/end_work", methods=['GET', 'POST'])
def end_work():
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'end-work.png')
    return render_template('endWork.html', image=image)

@app.route("/submit/end", methods=['POST'])
def submit_end_work():
    date = request.get_json()['date']
    longitude = request.get_json()['longitude']
    latitude = request.get_json()['latitude']
    return render_template('success.html')

#  ------------------------------------------------------------------------------------------ 
 
# Leave Permission 
@app.route("/leave_permission", methods=['GET', 'POST'])
def leave_permission():
    return render_template('leavePermission.html')

@app.route("/submit/leave", methods=['POST'])
def submit_leave_permission():
    date = request.get_json()['date']
    start_time = request.get_json()['startTime']
    end_time = request.get_json()['endTime']
    location = request.get_json()['location']
    ask_for_leave = request.get_json()['askForLeave']
    return render_template('success.html')

#  ------------------------------------------------------------------------------------------ 
  
# Attendance 
@app.route("/attendance", methods=['GET'])
def attendance():
    return render_template('attendance.html')

#  ------------------------------------------------------------------------------------------ 

# Personal Information 
@app.route("/personal_information", methods=['GET', 'POST'])
def personal_information():
    return render_template('personalInformation.html')

@app.route("/save", methods=['POST'])
def save_user_data():
    name = request.get_json()['name']
    email = request.get_json()['email']
    user_id = request.get_json()['id']
    role = request.get_json()['role']
    return render_template('success.html')

#  ------------------------------------------------------------------------------------------ 
  
# Company Information 
@app.route("/company_information", methods=['GET'])
def company_information():
    return render_template('companyInformation.html')

#  ------------------------------------------------------------------------------------------ 

# Report 
@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')

#  ------------------------------------------------------------------------------------------ 

port = int(os.environ.get('PORT', 8080))

if __name__ == '__main__':
    app.run(threaded=True, host='127.0.0.1', port=port)
