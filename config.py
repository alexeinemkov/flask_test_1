# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjdsjsjfsfhhvhavhwehwq2397526afs'
    if os.environ.get('DATABASE_URL') is None:
    	SQLALCHEMY_DATABASE_URI = 'sqlite:///'+str(os.path.join(basedir,'app.db'))
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POSTS_PER_PAGE = 100
