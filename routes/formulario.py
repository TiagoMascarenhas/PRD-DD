from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, Processo
from datetime import datetime

formulario_bp = Blueprint('formulario', __name__)

CAMPOS = [
    'data_emissao','status_form','nome','matricula','cpf','rg','tipo_benef','cargo','orgao',
    'origem','destino','dt_saida','hr_saida','dt_chegada','hr_chegada','tipo_viagem','horas_viagem',
    'fund_legal','descricao','desl_24h','hosp_outra','alim_outra',
    'r_classe','r_tipo','banco','agencia','conta','un_orc','proj_atv','elem_desp','a2_obs',
]
CAMPOS_FLOAT  = ['r_valor','total_diaria','d_alim','d_transp','d_taxa','d_reparos','d_outros']
CAMPOS_INT    = ['r_qtd_int','r_qtd_meio']


def _proximo_num_form():
    ano = datetime.utcnow().year
    ultimo = (Processo.query
              .filter(Processo.num_form.like(f'%/{ano}'))
              .order_by(Processo.id.desc())
              .first())
    if ultimo:
        seq = int(ultimo.num_form.split('/')[0]) + 1
    else:
        seq = 1
    return f'{str(seq).zfill(3)}/{ano}'


def _preencher_processo(p, form):
    for campo in CAMPOS:
        setattr(p, campo, form.get(campo, '').strip() or None)
    for campo in CAMPOS_FLOAT:
        try:
            setattr(p, campo, float(form.get(campo, 0)))
        except (ValueError, TypeError):
            setattr(p, campo, 0.0)
    for campo in CAMPOS_INT:
        try:
            setattr(p, campo, int(form.get(campo, 0)))
        except (ValueError, TypeError):
            setattr(p, campo, 0)
    p.atualizado_em = datetime.utcnow()


@formulario_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        acao = request.form.get('acao', 'rascunho')
        p = Processo(
            num_form   = _proximo_num_form(),
            usuario_id = current_user.id,
            status     = 'submetido' if acao == 'submeter' else 'rascunho',
        )
        _preencher_processo(p, request.form)
        db.session.add(p)
        db.session.commit()
        flash(f'Processo {p.num_form} {"submetido para aprovação" if acao == "submeter" else "salvo como rascunho"}.', 'ok')
        return redirect(url_for('processos.listar'))

    num_form = _proximo_num_form()
    hoje = datetime.utcnow().strftime('%Y-%m-%d')
    return render_template('formulario.html', processo=None, num_form=num_form, hoje=hoje)


@formulario_bp.route('/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def editar(pid):
    p = Processo.query.get_or_404(pid)

    # preenchedor só edita os próprios rascunhos
    if current_user.perfil == 'preenchedor':
        if p.usuario_id != current_user.id:
            abort(403)
        if p.status not in ('rascunho',):
            flash('Não é possível editar um processo já submetido.', 'erro')
            return redirect(url_for('processos.listar'))

    if request.method == 'POST':
        acao = request.form.get('acao', 'rascunho')
        _preencher_processo(p, request.form)
        if acao == 'submeter':
            p.status = 'submetido'
        db.session.commit()
        flash(f'Processo {p.num_form} atualizado.', 'ok')
        return redirect(url_for('processos.listar'))

    return render_template('formulario.html', processo=p, num_form=p.num_form, hoje=p.data_emissao)
