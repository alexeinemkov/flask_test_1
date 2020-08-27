# -*- coding: utf-8 -*-
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import locale
# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "Пожалуйста, войдите, чтобы открыть эту страницу."

from app import routes, models#, errors