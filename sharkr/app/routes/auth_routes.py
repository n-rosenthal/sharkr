"""
Routes para autenticação (login, register)

/login
/register
"""

from flask import request, redirect, url_for, flash, render_template, Blueprint
from app import app
from app.forms import LoginForm, RegistrationForm

#   Blueprint para autenticação
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login
    GET: Renderiza o template de login
    POST: Processa o formulário de login
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Processa o formulário de login
        flash('Login efetuado com sucesso!', 'success')
        return redirect(url_for('startup.index'))
    return render_template('auth/login.html', form=form, title='Login');

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota de registro
    GET: Renderiza o template de registro
    POST: Processa o formulário de registro
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # Processa o formulário de registro
        flash('Registro efetuado com sucesso!', 'success')
        return redirect(url_for('startup.index'))
    return render_template('auth/register.html', form=form, title='Register');

