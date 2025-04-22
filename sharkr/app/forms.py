from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)]);
    password = PasswordField('Senha', validators=[DataRequired()]);
    confirm_password = PasswordField('Confirmar a senha', validators=[DataRequired(), EqualTo('Senha')]);
    submit = SubmitField('Registrar');

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=2, max=20)]);
    password = PasswordField('Senha', validators=[DataRequired()]);
    remember = BooleanField('Lembrar-me');
    submit = SubmitField('Entrar');


class StartupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slogan = StringField('Slogan', validators=[DataRequired()])
    founding_year = IntegerField('Founding Year', validators=[DataRequired()])
    submit = SubmitField('Save Changes')