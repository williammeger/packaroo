import os
from flask import Flask, request, jsonify, render_template , send_from_directory, abort,  redirect, url_for
import json
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

client = MongoClient('mongodb://default:default@ds053216.mlab.com:53216/hackny')
db = client.hackny
collection = db.kits



# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all')
def all():
    return render_template('renderall.html')

@app.route('/check')
def check():
    return render_template('testrender.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):

  return render_template('form.html', filename=url_for('static', filename=filename))

@app.route('/test', methods=['GET', 'POST'])
def get_summary():
  print request.json
  collection.insert_one(request.json)
  return '200'

@app.route('/kit', methods=['GET', 'POST'])
def query():
  qs = request.query_string
  if qs == '':
    kits =  collection.find()
    return dumps(kits)
  else:
    qtags = request.args.get('tags')
    print qtags
    kits =  collection.find({"tags":{"$in" :[qtags]}})
    #?tags=clown
    return dumps(kits)




if __name__ == '__main__':
  app.run(port=5000,debug=True)
