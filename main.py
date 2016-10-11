import os
from flask import Flask, request, jsonify, render_template , send_from_directory, abort,  redirect, url_for
import json
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

#setup the location of the database
client = MongoClient('mongodb://default:default@ds053216.mlab.com:53216/hackny')
db = client.hackny
collection = db.kits

#set up what files to save and where
app.config['UPLOAD_FOLDER'] = 'static/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

#shows all the kits
@app.route('/all')
def all():
    return render_template('renderall.html')

#allows specific tags to be searched 
# - searchbar could be imporved 
@app.route('/check')
def check():
    return render_template('testrender.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route
        return redirect(url_for('uploaded_file', filename=filename))


#allow user to add annotations 
# - bug: user will submit 2 copies to the db (one with and one without annotations)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
  return render_template('form.html', filename=url_for('static', filename=filename))

#an 'api' route to get all kits and query for kits using ?tags=yourtaghere
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
    return dumps(kits)

if __name__ == '__main__':
  app.run(port=5000,debug=True)
