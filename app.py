import os
import json
import datetime
from dotenv import load_dotenv

from flask_cors import CORS
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

from time import sleep
from picamera import PiCamera
import qrcode
import cv2
import pytesseract
queue = 0;
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

fullName = []
imageQ = 0
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
        VaxPass = False
        ValidQRCode = False
        QRCodeJSON = QRCodeCheck()
        totalValid = "Fail"

        ## Check Valid QR Code Names
        if len(QRCodeJSON) == 4:
            ValidQRCode = True
            if QRCodeJSON['firstName'] and QRCodeJSON['lastName']:
                fullName.append(QRCodeJSON['firstName'])
                fullName.append(QRCodeJSON['lastName'])
            ### Check Valid Vax Info
            if QRCodeJSON['firstVax'] and QRCodeJSON['secondVax']:
                ## Collect second Vax
                sv = QRCodeJSON["secondVax"].split('/')
                today = datetime.date.today()
                lastVax = datetime.date(int('20'+sv[2]),int(sv[0]),int(sv[1]))
                ## Add two weeks
                d = datetime.timedelta(days=14)
                t = d + lastVax;
                ## Check the second Vax is more than 2 weeks away
                if t != today:
                    VaxPass = True
        
            if (VaxPass and ValidQRCode):
                totalValid = "Pass"
        return jsonify({"validQR": totalValid}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"validQR": "Fail"}), 200
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



############
#  Internal Functions for Sensors
#
############
def QRCodeCheck():
    camera = PiCamera()
    
    camera.start_preview()
    # Camera warm-up time
    sleep(5)
    ##camera.capture('Shrey_DL.png')

    camera.stop_preview()
    camera.capture('./QRCode.png')
    camera.close()
    ## Import File 
    filename = "QRCode.png"
    image = cv2.imread(filename)
    detector = cv2.QRCodeDetector()
    data, vertices_array, binary_qrcode = detector.detectAndDecode(image)

    # Data which for you want to make QR code
    # Here we are using URL of MakeUseOf website
    key = 'VW5pdmVyc2l0eSBvZiBSZWdpbmEK'
    
    # if vertices_array is not None:
    #     print("QRCode encrypted data:")
    #     print(data)

    de_data = ""
    for element in range(0, len(data)):
        i = 0
        list1 = list(data)
        num_msg = ord(data[element])
        while (i < len(key)):
            i = i + 1
            if i == len(key):
                i = 0
            num_key = ord(key[i])
            break
        res = num_msg - num_key
        list1[element] = chr(res)
        data = ''.join(list1)
    qrCodeData = data.replace('\n','$');
    dataList = qrCodeData.split('$');
    cData = []
    for i in dataList:
        cData.append(i.split(' '));


    payload = {}
    payload['firstName'] = cData[0][1]
    payload["lastName"] = cData[0][2]
    payload["firstVax"] = cData[2][-1]
    payload["secondVax"] = cData[3][-1]
    return payload
