import os
from line_api import PushMessage
from firestore_DAO import FirestoreDAO
from flask import Flask, request, render_template

image_folder = os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = image_folder

firestoreDAO = FirestoreDAO()

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
    # return jsonify(member)
    
# Start Work 
@app.route("/start_work", methods=['GET'])
def start_work():
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'start-work.png')
    return render_template('startWork.html', image=image)
  
# End Work 
@app.route("/end_work", methods=['GET'])
def end_work():
    image = os.path.join(app.config['UPLOAD_FOLDER'], 'end-work.png')
    return render_template('endWork.html', image=image)

# Leave Permission 
@app.route("/leave_permission", methods=['GET'])
def leave_permission():
    return render_template('leavePermission.html')
  
# Attendance 
@app.route("/attendance", methods=['GET'])
def attendance():
    return render_template('attendance.html')

# Personal Information 
@app.route("/personal_information", methods=['GET'])
def personal_information():
    return render_template('personalInformation.html')
  
# Company Information 
@app.route("/company_information", methods=['GET'])
def company_information():
    return render_template('companyInformation.html')

# Report 
@app.route("/report", methods=['GET'])
def report():
    return render_template('report.html')
