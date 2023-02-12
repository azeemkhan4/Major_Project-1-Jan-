from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

import os

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now)

    def __str__(self):
        return f'{self.username}({self.id})'

def check_imagetype(filename):
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['png', 'jpg', 'jpeg', 'gif']):
        return True
    else:
        return False

def check_videotype(filename):
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in set(['mp4']):
        return True
    else:
        return False

def save_thumbnail(file):
    if check_imagetype(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['THUMBNAIL_FOLDER'], filename))
        return filename
    else:
        return False

def save_video(file):
    if check_videotype(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['VIDEO_FOLDER'], filename))
        return filename
    else:
        return False

class Parking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    location = db.Column(db.String(80), unique=True, nullable=False)
    addr = db.Column(db.String(120), unique=True, nullable=False)
    total_count = db.Column(db.Integer, nullable=False)
    thumbnail = db.Column(db.String(120), unique=True, nullable=False)
    video = db.Column(db.String(120), unique=True, nullable=False)

    def __str__(self):
        return f'{self.name}({self.id})'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.sqlite'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['THUMBNAIL_FOLDER'] = 'static/thumbnails'
    app.config['VIDEO_FOLDER'] = 'static/videos'
    app.config['UPLOAD_MAX_SIZE'] = 1024 * 1024 * 10
    app.secret_key = 'supersecretkeythatnooneknows'
    db.init_app(app)
    return app

app = create_app()

def create_login_session(user: User):
    session['id'] = user.id
    session['username'] = user.username
    session['email'] = user.email
    session['is_logged_in'] = True

def destroy_login_session():
    if 'is_logged_in' in session:
        session.clear()

@app.route('/')
def index():
    return render_template('index.html')

# froute
@app.route('/login',  methods=['GET','POST'])
def login():
    errors = {}
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("LOGGIN IN",email, password)
        if password and email:
            if len(email) < 11 or '@' not in email:
                errors['email'] = 'Email is Invalid'
            if len(errors) == 0:
                user = User.query.filter_by(email=email).first()
                if user is not None:
                    print("user account found", user)
                    if user.password == password:
                        create_login_session(user)
                        flash('Login Successfull', "success")
                        return redirect('/')
                    else:
                        errors['password'] = 'Password is invalid'
                else:
                    errors['email']= 'Account does not exists'
        else:
            errors['email'] = 'Please fill valid details'
            errors['password'] = 'Please fill valid details'
    return render_template('login.html', errors = errors)

@app.route('/register', methods=['GET','POST'])
def register():
    errors = []
    if request.method == 'POST': # if form was submitted
        username = request.form.get('username')
        email = request.form.get('email')
        pwd = request.form.get('password')
        cpwd = request.form.get('confirmpass')
        if username and email and pwd and cpwd:
            if len(username)<2:
                errors.append("Username is too small")
            if len(email) < 11 or '@' not in email:
                errors.append("Email is invalid")
            if len(pwd) < 6:
                errors.append("Password should be 6 or more chars")
            if pwd != cpwd:
                errors.append("passwords do not match")
            if len(errors) == 0:
                user = User(username=username, email=email, password=pwd)
                db.session.add(user)
                db.session.commit()
                flash('user account created','success')
                return redirect('/login')
        else:
            errors.append('Fill all the fields')
            flash('user account could not be created','warning')
    return render_template('register.html', error_list=errors)

@app.route('/logout')
def logout():
    destroy_login_session()
    flash('You are logged out','success')
    return redirect('/')

@app.route('/addparking',methods=['GET','POST'])
def addparking():
    errors = []
    if request.method == 'POST': # if form was submitted
        parking = request.form.get('addparking')
        location = request.form.get('parkinglocation')
        address = request.form.get('parkingaddress')
        totalspace_count = request.form.get('totalparkingspace')
        thumbnail = request.files.get('thumbnail')
        video = request.files.get('video')
        print(request.files)
        print(request.form)
        print(parking, location, address, totalspace_count, thumbnail, video)
        if parking and location and address and totalspace_count and thumbnail and video:
            if len(parking) < 3:
                errors.append("Parking name is too small")
            if len(location) < 3:
                errors.append("Location is invalid")
            if len(address) < 3:
                errors.append("Address should be 6 or more chars")
            video_path = save_video(video)
            thumbnail_path = save_thumbnail(thumbnail)
            if thumbnail_path is None:
                errors.append("Thumbnail is invalid")
            if video_path is None:
                errors.append("Video is invalid")
            if len(errors) == 0:
                parking = Parking(title=parking, location=location, addr=address, 
                    total_count=totalspace_count, thumbnail=thumbnail_path, video=video_path)
                db.session.add(parking)
                db.session.commit()
                flash('Parking added successfully','success')
                return redirect('/parkinglisting')
        else:
            errors.append('Fill all the fields')
            flash('Parking could not be added','warning')
    return render_template('addparking.html', error_list=errors)

@app.route('/parkinglisting')
def parkinglisting():
    return render_template('parkinglisting.html')

@app.route('/parkingdetails')
def parkingdetails():
    return render_template('parkingdetails.html')
 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)

