# -*- coding: utf-8 -*-

from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class Tasklist(db.Model):
    __tablename__ = "tasklist"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    owner_user_id = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.fromtimestamp(int(datetime.now().timestamp())).strftime("%Y-%m-%d %H:%M:%S"), index=False, unique=False)
    title = db.Column(db.String(128), index=True, default='Empty Title')
    description = db.Column(db.String(256), index=True, default='Empty description')
    address_from = db.Column(db.String(256), default='Unknown address_from')
    address_to = db.Column(db.String(256), default='Unknown address_to')
    price = db.Column(db.String(128), default='1000')
    inwork = db.Column(db.Boolean(), default=False)
    complete = db.Column(db.Boolean(), default=False)

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    role = db.Column(db.String(10))
    password_hash = db.Column(db.String(128))
    cash = db.Column(db.String(128))

    def set_password(self, password):
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return Users.query.get(int(id))