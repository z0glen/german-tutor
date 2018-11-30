from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
import json

from app import app, db
from app.forms import LoginForm, RegistrationForm, WordForm
from app.models import User, Word

@app.route("/")
def splash():
    return render_template('splash.html')

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
            next_page = url_for('user', username=user.username)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('splash'))

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

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = WordForm()
    if form.validate_on_submit():
        word = Word(word=form.word.data, translation=form.translation.data, context = form.context.data, note=form.note.data, user=current_user)
        db.session.add(word)
        db.session.commit()
        flash('Your word has been added!')
        return redirect(url_for('user', username=current_user.username))
    user = User.query.filter_by(username=username).first_or_404()
    posts = current_user.words.all()
    return render_template('user.html', user=user, posts=posts, form=form)

@app.route('/practice')
@login_required
def practice():
    words = current_user.words.all()
    return render_template('practice.html', user=user, words=words)

if __name__ == '__main__':
    app.run(debug=True)
