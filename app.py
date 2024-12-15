from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, User, Image
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def create_tables():
    db.create_all()

# Route: หน้า Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_home'))
        flash("Invalid username or password")
    return render_template('login.html')

# Route: หน้า Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']

        user = User(username=username, password=password, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Route: หน้า User Home
@app.route('/user/home', methods=['GET','POST'])
def user_home():
    if 'role' in session and session['role'] == 'user':
          if request.method == 'POST':
              if 'image' not in request.files:
                  flash('No file part')
                  return redirect(request.url)
              file = request.files['image']
              if file.filename == '':
                  flash('No selected file')
                  return redirect(request.url)
              if file and allowed_file(file.filename):
                  filename = secure_filename(file.filename)
                  file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                  image = Image(user_id = session['user_id'], image_path=os.path.join(UPLOAD_FOLDER, filename))
                  db.session.add(image)
                  db.session.commit()
                  flash('Image uploaded successfully')
                  return redirect(url_for('user_home'))
          images = Image.query.filter_by(user_id = session['user_id']).all()
          return render_template('user_home.html', images = images)

    return redirect(url_for('login'))

# Route: หน้า Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' in session and session['role'] == 'admin':
        users = User.query.all()
        return render_template('admin.html', users=users)
    return redirect(url_for('login'))

# Route: หน้าแก้ไขโปรไฟล์
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            user.email = request.form['email']
            new_password = request.form['new_password']

            if new_password:
                 user.password = generate_password_hash(new_password)

            db.session.commit()
            flash("Profile updated successfully")
        return render_template('profile.html', user=user)
    return redirect(url_for('login'))


# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)