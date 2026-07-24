from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models import db, Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        senha       = request.form.get('senha', '')
        usuario = Usuario.query.filter_by(login=login_input, ativo=True).first()
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            return redirect(url_for('processos.listar'))
        flash('Login ou senha inválidos.', 'erro')
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
