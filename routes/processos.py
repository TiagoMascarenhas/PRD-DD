from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from io import BytesIO
try:
    from xhtml2pdf import pisa
    HAS_PISA = True
except ImportError:
    HAS_PISA = False
from flask_login import login_required, current_user
from models import db, Processo, Usuario
from datetime import datetime, timedelta

processos_bp = Blueprint('processos', __name__)


def _pode_ver(p):
    if current_user.perfil in ('aprovador', 'admin'):
        return True
    return p.usuario_id == current_user.id


@processos_bp.route('/')
@login_required
def listar():
    q = Processo.query

    if current_user.perfil == 'preenchedor':
        q = q.filter_by(usuario_id=current_user.id)

    # filtros
    texto   = request.args.get('q', '').strip()
    status  = request.args.get('status', '')
    viagem  = request.args.get('viagem', '')

    if texto:
        like = f'%{texto}%'
        q = q.filter(
            db.or_(
                Processo.nome.ilike(like),
                Processo.num_form.ilike(like),
                Processo.destino.ilike(like),
                Processo.orgao.ilike(like),
            )
        )
    if status:
        q = q.filter_by(status=status)
    if viagem:
        q = q.filter_by(tipo_viagem=viagem)

    processos = q.order_by(Processo.criado_em.desc()).all()
    return render_template('processos.html', processos=processos,
                           filtros={'q': texto, 'status': status, 'viagem': viagem})


@processos_bp.route('/aprovar/<int:pid>', methods=['POST'])
@login_required
def aprovar(pid):
    if current_user.perfil not in ('aprovador', 'admin'):
        abort(403)
    p = Processo.query.get_or_404(pid)
    acao = request.form.get('acao')
    obs  = request.form.get('obs_aprovacao', '').strip()

    if acao == 'aprovar':
        p.status       = 'aprovado'
        p.aprovado_por = current_user.id
        p.aprovado_em  = datetime.utcnow()
        p.obs_aprovacao = obs
        flash(f'Processo {p.num_form} aprovado.', 'ok')
    elif acao == 'reprovar':
        p.status        = 'reprovado'
        p.aprovado_por  = current_user.id
        p.aprovado_em   = datetime.utcnow()
        p.obs_aprovacao = obs
        flash(f'Processo {p.num_form} reprovado.', 'erro')

    db.session.commit()
    return redirect(url_for('processos.listar'))


@processos_bp.route('/exportar/<int:pid>')
@login_required
def exportar(pid):
    p = Processo.query.get_or_404(pid)
    if not _pode_ver(p):
        abort(403)

    autor = Usuario.query.get(p.usuario_id)
    aprovador = Usuario.query.get(p.aprovado_por) if p.aprovado_por else None

    def fmt_brl(v):
        try:
            return f'R$ {float(v or 0):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        except Exception:
            return 'R$ 0,00'

    def fmt_date(s):
        if not s:
            return ''
        try:
            y, m, d = s.split('-')
            return f'{d}/{m}/{y}'
        except Exception:
            return s

    dt_limite = ''
    if p.dt_chegada:
        try:
            d = datetime.strptime(p.dt_chegada, '%Y-%m-%d') + timedelta(days=5)
            dt_limite = d.strftime('%d/%m/%Y')
        except Exception:
            pass

    total_gastos   = p.total_gastos
    adiantado      = p.total_diaria or 0
    complementar   = max(0, total_gastos - adiantado)
    devolver       = max(0, adiantado - total_gastos)
    tipo_viagem_label = 'Dentro do Estado' if p.tipo_viagem == 'no_estado' else 'Fora do Estado'

    html = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<title>Diária {p.num_form}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,sans-serif;font-size:11px;color:#222;padding:12px 16px}}
h1{{font-size:13px;color:#1a3f7a;text-align:center;margin-bottom:2px}}
.sub{{font-size:10px;color:#555;text-align:center;margin-bottom:8px}}
.section{{border:1px solid #ccc;margin-bottom:6px;page-break-inside:avoid}}
.sh{{background:#1a3f7a;color:#fff;padding:3px 8px;font-size:10px;font-weight:bold;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.sb{{padding:6px 8px}}
table.layout{{width:100%;border-collapse:collapse}}
table.layout td{{padding:2px 4px;vertical-align:top}}
.f label{{font-size:9px;color:#666;font-weight:bold;display:block;margin-bottom:1px}}
.f span{{display:block;padding:2px 5px;border:1px solid #ddd;background:#f9f9f9;min-height:18px;font-size:11px}}
.total{{background:#1a3f7a;color:#fff;padding:5px 10px;margin-top:5px;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.total strong{{font-size:14px;float:right}}
table.dados{{width:100%;border-collapse:collapse;font-size:11px}}
table.dados th{{background:#f0f2f5;padding:3px 6px;text-align:left;font-size:10px;font-weight:bold;border-bottom:1px solid #ccc}}
table.dados td{{padding:3px 6px;border-bottom:1px solid #eee}}
.bal table{{width:100%;border-collapse:collapse;font-size:11px;margin-top:4px}}
.bal td{{padding:2px 6px;border-bottom:1px solid #eee}}
.bal tr:last-child td{{font-weight:bold;border:none;padding-top:4px}}
.decl{{padding:5px 7px;background:#f5f7fa;border:1px solid #ddd;font-size:10px;color:#444;margin-top:5px}}
table.assin{{width:100%;border-collapse:collapse;margin-top:10px}}
table.assin td{{width:50%;padding:0 10px;text-align:center;vertical-align:top;font-size:10px;color:#555;border-top:1px solid #999;padding-top:4px}}
.page-break{{page-break-before:always;padding-top:12px}}
.rodape{{text-align:center;font-size:9px;color:#999;margin-top:10px}}
@media print{{body{{padding:6px 10px}}}}
</style></head><body>

<h1>Prefeitura Municipal de Dias d'Ávila</h1>
<p class="sub">Anexo I — Lei Nº 393/2013 &amp; Decreto Nº 1.313/2013 | Requisição de Diárias</p>

<div class="section"><div class="sh">Identificação</div><div class="sb">
<table class="layout"><tr>
  <td width="34%"><div class="f"><label>Requisição de Diárias Nº</label><span>{p.num_form}</span></div></td>
  <td width="33%"><div class="f"><label>Data de Emissão</label><span>{fmt_date(p.data_emissao)}</span></div></td>
  <td width="33%"><div class="f"><label>Status</label><span>{p.status_form or '—'}</span></div></td>
</tr></table>
</div></div>

<div class="section"><div class="sh">1. Informações do Beneficiário</div><div class="sb">
<table class="layout"><tr>
  <td width="55%"><div class="f"><label>Nome</label><span>{p.nome or '—'}</span></div></td>
  <td width="20%"><div class="f"><label>Matrícula</label><span>{p.matricula or '—'}</span></div></td>
  <td width="25%"><div class="f"><label>RG</label><span>{p.rg or '—'}</span></div></td>
</tr><tr>
  <td colspan="2"><div class="f"><label>Cargo / Função</label><span>{p.cargo or '—'}</span></div></td>
  <td><div class="f"><label>Tipo de Beneficiário</label><span>{p.tipo_benef or '—'}</span></div></td>
</tr><tr>
  <td colspan="3"><div class="f"><label>Órgão / Secretaria</label><span>{p.orgao or '—'}</span></div></td>
</tr></table>
</div></div>

<div class="section"><div class="sh">2. Deslocamento</div><div class="sb">
<table class="layout"><tr>
  <td width="30%"><div class="f"><label>Origem</label><span>{p.origem or '—'}</span></div></td>
  <td width="30%"><div class="f"><label>Destino</label><span>{p.destino or '—'}</span></div></td>
  <td width="20%"><div class="f"><label>Tipo de Viagem</label><span>{tipo_viagem_label}</span></div></td>
  <td width="20%"><div class="f"><label>Horas de Viagem</label><span>{p.horas_viagem or '—'}</span></div></td>
</tr><tr>
  <td><div class="f"><label>Data Saída</label><span>{fmt_date(p.dt_saida)}</span></div></td>
  <td><div class="f"><label>Hora Saída</label><span>{p.hr_saida or '—'}</span></div></td>
  <td><div class="f"><label>Data Retorno</label><span>{fmt_date(p.dt_chegada)}</span></div></td>
  <td><div class="f"><label>Hora Retorno</label><span>{p.hr_chegada or '—'}</span></div></td>
</tr></table>
</div></div>

<div class="section"><div class="sh">3. Justificativa</div><div class="sb">
<div class="f" style="margin-bottom:4px"><label>Fundamentação Legal</label><span style="white-space:pre-wrap">{p.fund_legal or '—'}</span></div>
<div class="f"><label>Descrição da Viagem</label><span style="white-space:pre-wrap">{p.descricao or '—'}</span></div>
</div></div>

<div class="section"><div class="sh">4. Cálculo das Diárias</div><div class="sb">
<table class="layout" style="margin-bottom:4px"><tr>
  <td width="34%"><div class="f"><label>Desl. &lt;24h c/ hospedagem?</label><span>{'Sim' if p.desl_24h == 'sim' else 'Não'}</span></div></td>
  <td width="33%"><div class="f"><label>Hospedagem outra instituição?</label><span>{'Sim' if p.hosp_outra == 'sim' else 'Não'}</span></div></td>
  <td width="33%"><div class="f"><label>Alimentação outra instituição?</label><span>{'Sim' if p.alim_outra == 'sim' else 'Não'}</span></div></td>
</tr></table>
<table class="dados">
  <thead><tr><th>Classe</th><th>Tipo</th><th>Qtd. Inteiras</th><th>Qtd. Meias</th><th>Valor Unit.</th></tr></thead>
  <tbody><tr><td>{p.r_classe or '—'}</td><td>{p.r_tipo or '—'}</td><td>{p.r_qtd_int or 0}</td><td>{p.r_qtd_meio or 0}</td><td>{fmt_brl(p.r_valor)}</td></tr></tbody>
</table>
<div class="total">Total a Receber: <strong>{fmt_brl(adiantado)}</strong></div>
</div></div>

<div class="section"><div class="sh">5. Pagamento</div><div class="sb">
<table class="layout"><tr>
  <td width="34%"><div class="f"><label>Banco</label><span>{p.banco or '—'}</span></div></td>
  <td width="33%"><div class="f"><label>Agência</label><span>{p.agencia or '—'}</span></div></td>
  <td width="33%"><div class="f"><label>Conta Corrente</label><span>{p.conta or '—'}</span></div></td>
</tr><tr>
  <td><div class="f"><label>Unidade Orçamentária</label><span>{p.un_orc or '—'}</span></div></td>
  <td><div class="f"><label>Projeto / Atividade</label><span>{p.proj_atv or '—'}</span></div></td>
  <td><div class="f"><label>Elemento de Despesa</label><span>{p.elem_desp or '—'}</span></div></td>
</tr><tr>
  <td colspan="2"><div class="f"><label>Fonte de Recurso</label><span>{p.fonte_recurso or '—'}</span></div></td>
  <td></td>
</tr></table>
<table class="assin"><tr>
  <td>Assinatura do Beneficiário<br><br>Nome: ______________________________</td>
  <td>Assinatura do Ordenador de Despesa<br><br>Cargo: _____________________________</td>
</tr></table>
</div></div>

<div class="page-break">
<h1>Prefeitura Municipal de Dias d'Ávila</h1>
<p class="sub">Anexo II — Decreto Executivo Regulamentar | Relatório de Prestação de Contas</p>

<div class="section"><div class="sh">Vínculo</div><div class="sb">
<table class="layout"><tr>
  <td width="34%"><div class="f"><label>Form. Nº</label><span>{p.num_form}</span></div></td>
  <td width="33%"><div class="f"><label>Data Limite p/ Entrega</label><span>{dt_limite}</span></div></td>
  <td width="33%"><div class="f"><label>Tipo de Beneficiário</label><span>{p.tipo_benef or '—'}</span></div></td>
</tr></table>
</div></div>

<div class="section"><div class="sh">6. Despesas Realizadas</div><div class="sb">
<table class="dados">
  <thead><tr><th>Item</th><th style="text-align:right">Valor (R$)</th></tr></thead>
  <tbody>
    <tr><td>Alimentação</td><td style="text-align:right">{fmt_brl(p.d_alim)}</td></tr>
    <tr><td>Transporte Interno / Urbano</td><td style="text-align:right">{fmt_brl(p.d_transp)}</td></tr>
    <tr><td>Taxas de Embarque / Desembarque</td><td style="text-align:right">{fmt_brl(p.d_taxa)}</td></tr>
    <tr><td>Reparos e Manutenções</td><td style="text-align:right">{fmt_brl(p.d_reparos)}</td></tr>
    <tr><td>Outros Gastos</td><td style="text-align:right">{fmt_brl(p.d_outros)}</td></tr>
  </tbody>
</table>
<div class="bal"><table>
  <tr><td>( A ) Total de Gastos:</td><td style="text-align:right">{fmt_brl(total_gastos)}</td></tr>
  <tr><td>( B ) Total Adiantado:</td><td style="text-align:right">{fmt_brl(adiantado)}</td></tr>
  <tr><td style="color:#1a6a2a">A Receber ( A &gt; B ):</td><td style="text-align:right;color:#1a6a2a">{fmt_brl(complementar)}</td></tr>
  <tr><td style="color:#c0392b">A Devolver ( B &gt; A ):</td><td style="text-align:right;color:#c0392b">{fmt_brl(devolver)}</td></tr>
</table></div>
</div></div>

<div class="section"><div class="sh">7. Observações</div><div class="sb">
<div class="f" style="margin-bottom:5px"><label>Obs.</label><span style="white-space:pre-wrap">{p.a2_obs or '—'}</span></div>
<div class="decl"><strong>Certidão de Conformidade:</strong> Certifico, para estritos fins de análise e validação técnica junto ao Órgão de Controle Interno do Município, a regular execução dos trabalhos, encontrando-se em conformidade com o Decreto Municipal nº 014/09.</div>
<div class="decl" style="margin-top:4px"><strong>Declaração de Responsabilidade:</strong> Declaro que assumo inteira responsabilidade civil, administrativa e penal pela veracidade das informações apresentadas.</div>
<table class="assin"><tr>
  <td>Apresentado pelo Beneficiário<br><br>Data: ____/____/_____</td>
  <td>Assinatura do Ordenador de Despesa<br><br>Cargo: _____________________________</td>
</tr></table>
</div></div>

<p class="rodape">Sistema de Diárias — Desenvolvido pela PMDD - TI</p>
</div>

</body></html>"""

    filename_base = f'diaria_{p.num_form.replace("/", "_")}'

    if HAS_PISA:
        buf = BytesIO()
        pisa_status = pisa.CreatePDF(html.encode('utf-8'), dest=buf, encoding='utf-8')
        if not pisa_status.err:
            buf.seek(0)
            return Response(
                buf.read(),
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename={filename_base}.pdf'}
            )
        # fallback para HTML se pisa falhar
    return Response(html, mimetype='text/html',
                    headers={'Content-Disposition': f'attachment; filename={filename_base}.html'})


@processos_bp.route('/excluir/<int:pid>', methods=['POST'])
@login_required
def excluir(pid):
    p = Processo.query.get_or_404(pid)
    # preenchedor só exclui próprios rascunhos; admin/aprovador exclui qualquer um
    if current_user.perfil == 'preenchedor':
        if p.usuario_id != current_user.id or p.status != 'rascunho':
            abort(403)
    num = p.num_form
    db.session.delete(p)
    db.session.commit()
    flash(f'Processo {num} excluído.', 'ok')
    return redirect(url_for('processos.listar'))
