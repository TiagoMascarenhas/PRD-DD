from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

PERFIS = {
    'preenchedor': 'Preenchedor',
    'aprovador':   'Aprovador (Controladoria)',
    'admin':       'Administrador',
}

STATUS = {
    'rascunho':   'Rascunho',
    'submetido':  'Submetido',
    'aprovado':   'Aprovado',
    'reprovado':  'Reprovado',
}


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id       = db.Column(db.Integer, primary_key=True)
    nome     = db.Column(db.String(120), nullable=False)
    login    = db.Column(db.String(60), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil   = db.Column(db.String(20), nullable=False, default='preenchedor')
    ativo    = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    processos = db.relationship('Processo', foreign_keys='Processo.usuario_id', backref='autor', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.login} [{self.perfil}]>'


class Processo(db.Model):
    __tablename__ = 'processos'

    id           = db.Column(db.Integer, primary_key=True)
    num_form     = db.Column(db.String(20), unique=True, nullable=False)
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    status       = db.Column(db.String(20), nullable=False, default='rascunho')
    criado_em    = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Identificação
    data_emissao = db.Column(db.String(10))
    status_form  = db.Column(db.String(40))

    # Beneficiário
    nome         = db.Column(db.String(120))
    matricula    = db.Column(db.String(40))
    cpf          = db.Column(db.String(20))
    rg           = db.Column(db.String(20))
    tipo_benef   = db.Column(db.String(60))
    cargo        = db.Column(db.String(80))
    orgao        = db.Column(db.String(120))

    # Deslocamento
    origem       = db.Column(db.String(80))
    destino      = db.Column(db.String(80))
    dt_saida     = db.Column(db.String(10))
    hr_saida     = db.Column(db.String(5))
    dt_chegada   = db.Column(db.String(10))
    hr_chegada   = db.Column(db.String(5))
    tipo_viagem  = db.Column(db.String(20))
    horas_viagem = db.Column(db.String(20))

    # Justificativa
    fund_legal   = db.Column(db.Text)
    descricao    = db.Column(db.Text)

    # Cálculo
    desl_24h     = db.Column(db.String(3))
    hosp_outra   = db.Column(db.String(3))
    alim_outra   = db.Column(db.String(3))
    r_classe     = db.Column(db.String(60))
    r_tipo       = db.Column(db.String(30))
    r_qtd_int    = db.Column(db.Integer)
    r_qtd_meio   = db.Column(db.Integer)
    r_valor      = db.Column(db.Float)
    total_diaria = db.Column(db.Float)

    # Pagamento
    banco        = db.Column(db.String(60))
    agencia      = db.Column(db.String(20))
    conta        = db.Column(db.String(30))
    un_orc       = db.Column(db.String(30))
    proj_atv     = db.Column(db.String(30))
    elem_desp    = db.Column(db.String(30))

    # Prestação de contas (Anexo II)
    d_alim       = db.Column(db.Float, default=0)
    d_transp     = db.Column(db.Float, default=0)
    d_taxa       = db.Column(db.Float, default=0)
    d_reparos    = db.Column(db.Float, default=0)
    d_outros     = db.Column(db.Float, default=0)
    a2_obs       = db.Column(db.Text)

    # Aprovação
    aprovado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    aprovado_em  = db.Column(db.DateTime, nullable=True)
    obs_aprovacao = db.Column(db.Text)

    @property
    def total_gastos(self):
        return sum(v or 0 for v in [self.d_alim, self.d_transp, self.d_taxa, self.d_reparos, self.d_outros])

    @property
    def saldo(self):
        return (self.total_diaria or 0) - self.total_gastos

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
