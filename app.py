import os
import json
import datetime
import max30102
import hrcalc
from dotenv import load_dotenv

import grove_d6t
import pigpio
import time


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
        temp = getTempReadings()
        return jsonify({"temp": temp}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"success": 0}), 200
#############################################################


'''
Get Request for Sp O2 Sensor

'''


@app.route('/getOxy', methods=['GET'])
def readOxy():
    try:
        Oxy = getO2SensorData()
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
            if QRCodeJSON['firstName'] and QRCodeJSON['lastName'] and len(fullName) == 0:
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
                QRCodeJSON["totalValid"] = totalValid
            else:
                QRCodeJSON["totalValid"] = totalValid
            qrJSON = json.dumps(QRCodeJSON,indent=2)
        return qrJSON, 200
    except Exception as e:
        print("An Error Occured: \n ", e)
        return jsonify({"totalValid": "Fail"}), 200
#############################################################


'''
Get Request for ID Card OCR + Verifiction

'''


@app.route('/getID', methods=['GET'])
def readID():
    ocrValid = "Fail"
    try:
        
        ####
        '''
        Enter in Code to Grab ID via OCR from Camera, Parse, and Check name match.
        Global variable to Check and place name.
        '''
        ####
        count = 0
        ocrData = getOCR()
        for word in fullName:
            a = word
            a = a.lower()
            print(ocrData, "-----------------Data" + '\n')
            if a in ocrData:
                print("Name found")
                count += 1
        if count == 2:
            ocrValid = "Pass"

        return jsonify({"validID": ocrValid}), 200
    except Exception as e:
        print("An Error Occured: \n {e}")
        return jsonify({"validID": ocrValid}), 200



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



############
#  Internal Functions for Sensors
#
############
def getOCR():
    camera = PiCamera()
    camera.start_preview()
    # Camera warm-up time
    sleep(5)
    camera.capture('./Shrey_DL.png')

    camera.stop_preview()

    camera.close()
    img = cv2.imread('./Shrey_DL.png')

    # Adding custom options
    custom_config = r'--oem 3 --psm 6'
    resultData = pytesseract.image_to_string(img)
    print(resultData)
    resultData = resultData.lower()
    return resultData
    
def getO2SensorData():
    

    m = max30102.MAX30102()

    hr2 = 0
    sp2 = 0

    i = 0
    currValue = 0
    OxyRateList = []
    while i < 20:
        red, ir = m.read_sequential()
        
        hr,hrb,sp,spb = hrcalc.calc_hr_and_spo2(ir, red)

        if(hrb == True and spb == True and hr != -999):
            if int(sp) > 83:
                OxyRateList.append(int(sp))
        i+=1
    finalAverageSpO2 = sum(OxyRateList) // len(OxyRateList)
    return finalAverageSpO2

def getTempReadings():
    d6t = grove_d6t.GroveD6t()
    i = 0
    tempArray = []
    while i < 10:
            try:
                    tpn, tptat = d6t.readData()
                    if tpn != None:
                        tempArray.append(tpn[0])
                        ##print(tpn[0],"PTAT : %.1f" %tptat)
                        time.sleep(1.0)
                    else:
                        continue
                    i += 1
                
            except Exception as e:
                continue  
    ##print(tempArray)
    finalAvgTemp = sum(tempArray)//len(tempArray)
    return finalAvgTemp