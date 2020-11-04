from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

auth = Blueprint('auth', __name__)
admin = 'cssp'

@auth.route('/login')
def login():
    return render_template('login.html',title='Login',admin=admin)

@auth.route('/login', methods=['POST'])
def login_post():
    #email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(name=name).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))

    login_user(user, remember=remember)

    return redirect(url_for('main.train'))

@auth.route('/signup')
def signup():
    data = db.session.query(User).all()
    return render_template('signup.html',title='Signup',admin=admin,output_data=data)

@auth.route('/signup', methods=['POST'])
@login_required
def signup_post():
    if request.form['submit_button'] == 'add':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user = User.query.filter_by(name=name).first()

        if user:
            flash('Name is already exists.')
            return redirect(url_for('auth.signup'))

        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
        
    elif request.form['submit_button'] == 'delete':
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')
            User.query.filter_by(name=name).delete()
            db.session.commit()
    else:
        pass
    return redirect(url_for('auth.signup'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))