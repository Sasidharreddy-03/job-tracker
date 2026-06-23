from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Job
from dotenv import load_dotenv
from ai_extractor import extract_job_details
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

from urllib.parse import quote_plus

DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    total = len(jobs)
    applied = len([j for j in jobs if j.status == 'Applied'])
    test = len([j for j in jobs if j.status == 'Test'])
    interview = len([j for j in jobs if j.status == 'Interview'])
    offer = len([j for j in jobs if j.status == 'Offer'])
    rejected = len([j for j in jobs if j.status == 'Rejected'])
    return render_template('dashboard.html',
        jobs=jobs,
        total=total,
        applied=applied,
        test=test,
        interview=interview,
        offer=offer,
        rejected=rejected
    )

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        job = Job(
            company=request.form['company'],
            role=request.form['role'],
            skills=request.form['skills'],
            ctc=request.form['ctc'],
            location=request.form['location'],
            status=request.form['status'],
            notes=request.form['notes'],
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_job.html')

@app.route('/update/<int:job_id>', methods=['POST'])
@login_required
def update_status(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = request.form['status']
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:job_id>')
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/extract', methods=['POST'])
@login_required
def extract():
    data = request.get_json()
    job_description = data.get('job_description', '')
    result = extract_job_details(job_description)
    return jsonify(result)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)