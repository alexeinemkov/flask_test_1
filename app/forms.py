# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, DateField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Users


class CreateTask(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    address_from = StringField('Откуда забрать', validators=[DataRequired()])
    address_to = StringField('Куда доставить', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    # username = StringField('Имя пользователя', validators=[DataRequired()])
    phone_number = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    # email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Номер телефона', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Роль', validators=[DataRequired()], choices=[("sender", "Грузоотправитель"),("driver", "Перевозчик")])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Используйте другое имя')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Используйте другой адрес')

    def validate_phone_number(form, phone_number):
        if (len(phone_number.data) > 10) or len(phone_number.data) < 10:
            raise ValidationError('Неправильный номер телефона!Только 10 цифр без кода страны 0123456789!')
        if not phone_number.data.isdigit():
        	raise ValidationError('Неправильный номер телефона!Только 10 цифр без кода страны 0123456789!')
        user = Users.query.filter_by(phone_number=phone_number.data).first()
        if user is not None:
            raise ValidationError('Используйте другой телефонный номер')

class EditTable(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    phone_number = StringField('Номер телефона')
    password = PasswordField('Пароль')
    password2 = PasswordField('Повторите пароль', validators=[EqualTo('password')])
    role = SelectField('Роль', validators=[DataRequired()], choices=[("sender", "Грузоотправитель"),("driver", "Перевозчик")])
    submit = SubmitField('Обновить')
