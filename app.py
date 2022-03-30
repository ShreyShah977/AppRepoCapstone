import os
import json
from dotenv import load_dotenv

from flask_cors import CORS
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
CORS(app)
load_dotenv()
# Init API Keys
GCP_JSON = os.getenv('PATH_SERVICE_ACC')

# Initialize Firestore DB
cred = credentials.Certificate(GCP_JSON)
default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('Users')


@app.route('/')
def hello_world():
    return 'Base Level Access'
##########################################################


@app.route('/add', methods=['POST'])
def create():
    '''
    create() : Adds a new document (random generated id#) to collection
    on Cloud Firestore. 
    Since we're not restricting type access. We want always follow the following
    scheme when building POST Requests:
    i.e 
    {
        name: "",
        SurveyResult: [True,True,True,True,True],
        Temperature: "",
        Oxygen: "",
        QRCodeNameCheck: "True",
        ValidVaxx: "True"
        Timestamp: "",
    }
    '''
    try:
        # <-- Add Santization of Inputs -->
        db.collection('Users').add(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


'''

#################################################
@app.route('/list', methods=['GET'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        todo_id = request.args.get('id')
        if todo_id:
            todo = todo_ref.document(todo_id).get()
            return jsonify(todo.to_dict()), 200
        else:
            all_todos = [doc.to_dict() for doc in todo_ref.stream()]
            return jsonify(all_todos), 200
    except Exception as e:
        return f"An Error Occured: {e}"


############################################################
@app.route('/update', methods=['POST', 'PUT'])
def update():
    """
        update() : Update document in Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        id = request.json['id']
        todo_ref.document(id).update(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": False}), 503
'''
#############################################################

'''
Get Request for Temperature

'''


@app.route('/getTemp', methods=['GET'])
def readTemp():
    try:
        temp = 34
        return jsonify({"temp": temp}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": False}), 503
#############################################################


'''
Get Request for Sp O2 Sensor

'''


@app.route('/getOxy', methods=['GET'])
def readOxy():
    try:
        Oxy = 99
        return jsonify({"oxy": Oxy}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": False}), 503
#############################################################


'''
Get Request for QR Code + Verifiction

'''


@app.route('/getQR', methods=['GET'])
def readQR():
    try:
        ####
        '''
        Enter in Code to Grab QR Code from Camera, Parse, and Check for double vax.
        '''
        ####
        doubleVax = True
        ValidQRCode = True

        totalValid = "Fail"
        if (doubleVax and ValidQRCode):
            totalValid = "Pass"

        return jsonify({"validQR": totalValid}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": False}), 503
#############################################################


'''
Get Request for ID Card OCR + Verifiction

'''


@app.route('/getID', methods=['GET'])
def readID():
    try:
        ####
        '''
        Enter in Code to Grab ID via OCR from Camera, Parse, and Check name match.
        Global variable to Check and place name.
        '''
        ####
        nameMatch = True
        ValidID = True

        totalValid = "Fail"
        if (nameMatch and ValidID):
            totalValid = "Pass"

        return jsonify({"validID": totalValid}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": False}), 503
