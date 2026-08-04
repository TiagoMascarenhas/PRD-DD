import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, Usuario
from auth import auth_bp
from routes.formulario import formulario_bp
from routes.processos import processos_bp
from routes.importar import importar_bp

# ── Admin routes ────────────────────────────────────────────────────────────
from flask import render_template, request, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import PERFIS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']           = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///diarias.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view     = 'auth.login'
    login_manager.login_message  = 'Faça login para continuar.'
    login_manager.login_message_category = 'erro'

    @login_manager.user_loader
    def load_user(uid):
        return Usuario.query.get(int(uid))

    app.jinja_env.globals['enumerate'] = enumerate

    def fmt_brl(v):
        try:
            v = float(v or 0)
        except (TypeError, ValueError):
            v = 0.0
        inteiro, decimal = f'{v:,.2f}'.split('.')
        inteiro = inteiro.replace(',', '.')
        return f'R$ {inteiro},{decimal}'

    app.jinja_env.filters['brl'] = fmt_brl

    def fmt_data(s):
        if not s:
            return ''
        try:
            y, m, d = s.split('-')
            return f'{d}/{m}/{y}'
        except Exception:
            return s

    app.jinja_env.filters['data'] = fmt_data

    app.register_blueprint(auth_bp)
    app.register_blueprint(formulario_bp, url_prefix='/formulario')
    app.register_blueprint(processos_bp,  url_prefix='/processos')
    app.register_blueprint(importar_bp,   url_prefix='/processos')

    # ── Admin: gerenciar usuários ────────────────────────────────────────────
    @app.route('/admin/usuarios')
    @login_required
    def admin_usuarios():
        if current_user.perfil != 'admin':
            abort(403)
        usuarios = Usuario.query.order_by(Usuario.nome).all()
        return render_template('admin_usuarios.html', usuarios=usuarios, perfis=PERFIS)

    @app.route('/admin/usuarios/novo', methods=['POST'])
    @login_required
    def admin_novo_usuario():
        if current_user.perfil != 'admin':
            abort(403)
        nome   = request.form.get('nome', '').strip()
        login  = request.form.get('login', '').strip()
        senha  = request.form.get('senha', '').strip()
        perfil = request.form.get('perfil', 'preenchedor')
        if not nome or not login or not senha:
            flash('Preencha todos os campos.', 'erro')
            return redirect(url_for('admin_usuarios'))
        if Usuario.query.filter_by(login=login).first():
            flash('Login já existe.', 'erro')
            return redirect(url_for('admin_usuarios'))
        u = Usuario(nome=nome, login=login, perfil=perfil)
        u.set_senha(senha)
        db.session.add(u)
        db.session.commit()
        flash(f'Usuário {nome} criado.', 'ok')
        return redirect(url_for('admin_usuarios'))

    @app.route('/admin/usuarios/<int:uid>/toggle', methods=['POST'])
    @login_required
    def admin_toggle_usuario(uid):
        if current_user.perfil != 'admin':
            abort(403)
        u = Usuario.query.get_or_404(uid)
        if u.id == current_user.id:
            flash('Não é possível desativar sua própria conta.', 'erro')
        else:
            u.ativo = not u.ativo
            db.session.commit()
            flash(f'Usuário {"ativado" if u.ativo else "desativado"}.', 'ok')
        return redirect(url_for('admin_usuarios'))

    @app.route('/admin/usuarios/<int:uid>/resetar_senha', methods=['POST'])
    @login_required
    def admin_resetar_senha(uid):
        if current_user.perfil != 'admin':
            abort(403)
        u = Usuario.query.get_or_404(uid)
        nova = request.form.get('nova_senha', '').strip()
        if not nova:
            flash('Informe a nova senha.', 'erro')
        else:
            u.set_senha(nova)
            db.session.commit()
            flash(f'Senha de {u.nome} redefinida.', 'ok')
        return redirect(url_for('admin_usuarios'))

    @app.route('/')
    @login_required
    def index():
        return redirect(url_for('processos.listar'))

    # ── Init DB + admin padrão ───────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(login='admin').first():
            admin = Usuario(nome='Administrador', login='admin', perfil='admin')
            admin.set_senha('admin123')
            db.session.add(admin)
            db.session.commit()
            print('[diarias] Usuário admin criado. Login: admin / Senha: admin123')
            print('[diarias] TROQUE A SENHA IMEDIATAMENTE após o primeiro login.')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=2525, debug=False)
