
# in the other stereo-formatting script
# check that JPG (all caps) works. I had to change the deleting -0/-1 files and add lower in line 287
# check that files with spaces in names work
# error handling with try/except for subprocesses
# also modify so it handles png

import datetime
import subprocess
from flask import Flask, render_template, request, redirect, url_for
import os
import zipfile
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'static/sf-workspace'
SF_FILE = 'stereo-formatting.py'
DEVICES_FILE = 'devices.txt'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/index")
@app.route("/index.html")
@app.route("/")
def root():
    err = request.args.get('err')
    if err == '1':
        error = "No file uploaded"
    elif err == '2':
        error = "No device selected"
    elif err == '3':
        error = "File must be jpg, png, or zip"
    elif err == '4':
        error = "An error occurred while working with the file."
    else:
        error = ""

    file = request.args.get('file')
    file = UPLOAD_FOLDER + '/' + file if file else ""

    return render_template("index.html", devices=get_devices(), error=error, file=file)


@app.route("/upload", methods=["POST"])
def upload():

    remove_old_files()

    # get file
    file = request.files['file']
    if not file:
        return redirect(url_for('root', err=1))

    # save file and file type
    file_split = file.filename.rsplit('.', 1)
    base_name = file_split[0]
    file_type = file_split[1].lower()

    count = 1
    while os.path.exists(UPLOAD_FOLDER + '/' + base_name + '.' + file_type):
        base_name = base_name + str(count)
        count += 1

    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    # get device
    device = request.form['devices']
    if not device:
        return redirect(url_for('root', err=2))

    if file_type == 'jpg':
        run_image(UPLOAD_FOLDER + '/' + file.filename,
                  device, base_name + '.' + file_type)
    elif file_type == 'png':
        file_type = 'jpg'
        run_image(UPLOAD_FOLDER + '/' + file.filename,
                  device, base_name + '.' + file_type)
    elif file_type == 'zip':
        run_zip(file.filename, device, base_name)
    else:
        return redirect(url_for('root', err=3))

    new_file = base_name+'.' + file_type

    if not os.path.exists(UPLOAD_FOLDER + '/' + new_file):
        return redirect(url_for('root', err=4))

    return redirect(url_for('root', file=new_file))


def get_devices():
    DEVICES = {}
    with open(UPLOAD_FOLDER + '/' + DEVICES_FILE, 'r') as f:
        for line in f:
            line = line.strip('\n')
            line = line.split(', ')
            if len(line) != 5:
                continue
            DEVICES[line[0]] = {
                'name': line[0],
                'dev_width': int(line[1]),
                'dev_height': int(line[2]),
                'eff_width': int(line[3]),
                'eff_height': int(line[4]),
            }

    return DEVICES


def run_image(file, device, output_fname):
    script = UPLOAD_FOLDER + "/" + SF_FILE

    res = subprocess.check_output([
        'python3',
        script,
        '-f',
        file,
        device,
        output_fname
    ])

    # NEED TO CHECK FOR ERRORS HERE
    res = res.decode()
    if not res.startswith("Your new image is:"):
        return redirect(url_for('root', err=4))


def run_zip(file, device, fname):

    # unzip
    new_dir = UPLOAD_FOLDER + '/' + fname
    os.makedirs(new_dir, exist_ok=True)
    with zipfile.ZipFile(UPLOAD_FOLDER + '/' + file, 'r') as zip_ref:
        zip_ref.extractall(new_dir)

    # format images
    for root, dirs, files in os.walk(new_dir):
        for file in files:
            if file.lower().endswith('.jpg') or file.lower().endswith('.png'):
                run_image(new_dir + '/' + file, device, fname + '/' + file)

    # zip folder
    with zipfile.ZipFile(new_dir + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(new_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, new_dir))

    # remove unzipped folder
    shutil.rmtree(new_dir)


def remove_old_files():
    now = datetime.datetime.now()
    minutes_ago = now - datetime.timedelta(minutes=10)

    for fn in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, fn)
        file_modified_time = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path))

        if fn != SF_FILE and fn != DEVICES_FILE and file_modified_time < minutes_ago:
            os.remove(file_path)


if __name__ == '__main__':
    app.run(debug=True)
