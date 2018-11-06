from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.urls import url_parse
import json

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User

@app.route("/")
def show_form():
    with open('dictionary.json', 'r') as infile:
        data = json.load(infile)
        print(data)
    return render_template('form.html', words=data)

@app.route("/", methods=['POST'])
def get_form():
    text = request.form['word']
    context = request.form['context']
    data = {"text": text, "context": context}
    with open('dictionary.json', 'w') as outfile:
        json.dump(data, outfile)
    flash('Got word {} in context {}'.format(text, context))
    return redirect(url_for('show_form'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('show_form')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_form'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to our club!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

if __name__ == '__main__':
    app.run(debug=True)
