# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm, EditTable, CreateTask
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import Users, Tasklist
from flask import request, url_for
from werkzeug.urls import url_parse
from datetime import datetime, date, timedelta
import time
from flask import jsonify,make_response
import json
from dateutil.relativedelta import relativedelta 
from sqlalchemy import and_, or_, func, not_
from flask_paginate import Pagination, get_page_args
import os
import sys

import logging

from decimal import Decimal

logging.basicConfig(\
            format='[%(asctime)s] %(message)s',\
            datefmt='%d/%m/%Y %H:%M:%S',\
          level=logging.DEBUG)

fee = Decimal('0.9')

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    if current_user.role == 'sender':
        return redirect(url_for('senderTasks'))

    tasks = Tasklist.query.filter(and_(Tasklist.inwork == False,Tasklist.complete==False)).all()
    return render_template('index.html', title='Tasks', tasks=tasks)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(phone_number=form.phone_number.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный номер телефона или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, phone_number=form.phone_number.data, role=form.role.data, cash=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь добавлен')
        return redirect(url_for('index'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/users', methods=['GET','POST'])
@login_required
def users():
    if current_user.role=='admin':
        user = Users.query.all()
        form = RegistrationForm()
        if form.validate_on_submit():
            user = Users(username=form.username.data, phone_number=form.phone_number.data, role=form.role.data, cash=0)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Пользователь добавлен')
            return redirect(url_for('users'))
        return render_template('users.html', title='Register', user=user, form=form)
    else:
        return redirect(url_for('index'))

@app.route('/delete/<phone_number>')
@login_required
def delete(phone_number):
    user = Users.query.filter_by(phone_number=phone_number).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь удален')
    return redirect(url_for('users'))

@app.route('/user/<phone_number>', methods=['GET','POST'])
@login_required
def user(phone_number):
    user = Users.query.filter_by(phone_number=phone_number).first_or_404()
    form=EditTable()
    if form.validate_on_submit():
        user = Users.query.filter_by(phone_number=phone_number).first()
        if user.username!=form.username.data:
            user = Users.query.filter_by(username=form.username.data).first()
            if user is not None:
                flash('Используйте другое имя!')
                return redirect(url_for('user', phone_number=phone_number))
        user = Users.query.filter_by(phone_number=phone_number).first()
        user.username=form.username.data
        user.role=form.role.data
        if (form.password.data!='') and (form.password.data==form.password2.data):
            user.set_password(form.password.data)
            flash('Пароль изменен')
        elif form.password.data==form.password2.data:
            flash('Пароль не изменен')
        db.session.commit()
        flash('Данные пользователя изменены')
        return redirect(url_for('user', phone_number=phone_number))
    return render_template('user.html', user=user, form=form, phone_number=phone_number)

@app.route('/senderTasks', methods=['GET','POST'])
@login_required
def senderTasks():
    tasks = Tasklist.query.filter_by(owner_user_id = current_user.id).all()
    form=CreateTask()
    if form.validate_on_submit():
        task = Tasklist(\
            title=form.title.data, \
            timestamp=datetime.now(), \
            description=form.description.data, \
            address_from=form.address_from.data, \
            address_to=form.address_to.data,\
            user_id = current_user.id, \
            owner_user_id = current_user.id, \
            price = form.price.data, \
            inwork = False, complete = False)
        db.session.add(task)
        db.session.commit()
        flash('Задание добавлено')
        return redirect(url_for('senderTasks'))
    return render_template('senderTasks.html',  form=form, tasks=tasks)

@app.route('/deleteTask/<taskId>')
@login_required
def deleteTask(taskId):
    task = Tasklist.query.filter(and_(Tasklist.id==taskId, Tasklist.owner_user_id==current_user.id)).first_or_404()
    if task is not None:
        db.session.delete(task)
        db.session.commit()
        flash('Задание удалено')
    else:
        flash('Задание недоступно')
    return redirect(url_for('senderTasks'))

@app.route('/driverTasks')
@login_required
def driverTasks():
    tasks = Tasklist.query.filter(and_(Tasklist.user_id == current_user.id, Tasklist.inwork == True)).all()
    tasksInwork=0
    tasksComplete=0
    for task in tasks:
        if task.complete:
            tasksComplete=tasksComplete+1
        else:
            tasksInwork=tasksInwork+1

    user = Users.query.filter_by(id=current_user.id).first()

    return render_template('driverTasks.html', tasks=tasks, cash=user.cash, tasksInwork=tasksInwork, tasksComplete=tasksComplete)

@app.route('/acceptTask/<taskId>')
@login_required
def acceptTask(taskId):
    task = Tasklist.query.filter(and_(\
        Tasklist.id==taskId, \
        Tasklist.inwork==False, \
        Tasklist.complete==False)).first()
    if task is not None:
        userId = current_user.id
        task.inwork=True
        task.user_id=userId
        user = Users.query.filter_by(id=userId).first_or_404()
        user.cash = float(Decimal(str(user.cash))+Decimal(str(task.price))*fee)
        db.session.commit()
        flash('Задание получено!')
        return redirect(url_for('driverTasks'))
    flash('Задание недоступно')
    return redirect(url_for('index'))


@app.route('/completeTask/<taskId>')
@login_required
def completeTask(taskId):
    task = Tasklist.query.filter(and_(\
        Tasklist.id==taskId, \
        Tasklist.inwork==True, \
        Tasklist.complete==False, \
        Tasklist.user_id==current_user.id)).first()
    if task is not None:
        task.complete=True
        db.session.commit()
        flash('Задание выполнено!')
        return redirect(url_for('driverTasks'))
    flash('Задание недоступно')
    return redirect(url_for('index'))

@app.route('/createadmin', methods=['GET','POST'])
def createadmin():
    user = Users.query.all()
    user = Users(username='admin', phone_number='0123456789', role='admin', cash='0')
    user.set_password('131313')
    db.session.add(user)
    db.session.commit()
    flash('Пользователь добавлен')
    return redirect(url_for('index'))


@app.route('/createtasksfordriver', methods=['GET','POST'])
def createtasksfordriver():
    user = Users.query.filter_by(username='sender').first()
    if user is None:
        user = Users(username='sender', phone_number='1111111111', role='sender', cash='0')
        user.set_password('1111')
        db.session.add(user)
        db.session.commit()
        flash('Грузоотправитель добавлен')
    user2 = Users.query.filter_by(username='driver').first()
    if user2 is None:
        user2 = Users(username='driver', phone_number='2222222222', role='driver', cash='0')
        user2.set_password('1111')
        db.session.add(user2)
        db.session.commit()
        flash('Перевозчик добавлен')
    for i in range(1,11):
        task = Tasklist(\
            title="Задание "+str(i), \
            timestamp=datetime.now(), \
            description="Описание "+str(i), \
            address_from="Земля "+str(i), \
            address_to="Луна "+str(i),\
            user_id = user.id, \
            owner_user_id = user.id, \
            price = 325.77*i, \
            inwork = False, complete = False)
        db.session.add(task)
        db.session.commit()
    flash('Данные добавлены')
    flash('sender login/pass: 1111111111/1111')
    flash('driver login/pass: 2222222222/1111')
    return redirect(url_for('index'))