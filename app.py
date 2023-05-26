import os
import secrets
from flask import Flask, flash, redirect, request, render_template
from pdfminer.high_level import extract_text
from werkzeug.utils import secure_filename

from controllers.summary_controller import getSummary

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# root api direct to index.html (home page)


@app.route('/')
def home():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/summarize', methods=['POST'])
def summarize():

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

 # Extract text
    screenplay_text = extract_text(os.path.join(
        app.config['UPLOAD_FOLDER'], filename))
    if screenplay_text:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #print(screenplay_text)
    output = getSummary(screenplay_text, flash)
    if isinstance(output, dict):
        movie_summary = output.get('movie_summary')
    else:
        movie_summary = ""
        # use the flash function to display the error message to the user
        flash(output)

    return render_template('index.html', movie_summary=movie_summary)


if __name__ == "__main__":
    app.run(debug=True)
