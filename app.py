import os, json
from dotenv import load_dotenv


from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)
load_dotenv()
## Init API Keys
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
      Timestamp: "",
      SurveyResult: [True,True,True,True,True],
      Temperature: "",
      Oxygen: "",
      QRCodeNameCheck: "True",
      ValidVaxx: "True"
  }
  '''
  try:
      db.collection('Users').add(request.json)
      return jsonify({"success": True}), 200
  except Exception as e:
      return f"An Error Occured: {e}"

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
        return f"An Error Occured: {e}"

@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    """
        delete() : Delete a document from Firestore collection.
    """
    try:
        # Check for ID in URL query
        todo_id = request.args.get('id')
        todo_ref.document(todo_id).delete()
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)