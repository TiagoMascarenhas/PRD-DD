warning: in the working copy of 'routes/processos.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/routes/__pycache__/formulario.cpython-314.pyc b/routes/__pycache__/formulario.cpython-314.pyc[m
[1mindex e462cc8..292be77 100644[m
Binary files a/routes/__pycache__/formulario.cpython-314.pyc and b/routes/__pycache__/formulario.cpython-314.pyc differ
[1mdiff --git a/routes/__pycache__/importar.cpython-314.pyc b/routes/__pycache__/importar.cpython-314.pyc[m
[1mindex ef831d2..93aa46c 100644[m
Binary files a/routes/__pycache__/importar.cpython-314.pyc and b/routes/__pycache__/importar.cpython-314.pyc differ
[1mdiff --git a/routes/__pycache__/processos.cpython-314.pyc b/routes/__pycache__/processos.cpython-314.pyc[m
[1mindex 4e3c942..c25faec 100644[m
Binary files a/routes/__pycache__/processos.cpython-314.pyc and b/routes/__pycache__/processos.cpython-314.pyc differ
[1mdiff --git a/routes/processos.py b/routes/processos.py[m
[1mindex 923d75a..7eeb340 100644[m
[1m--- a/routes/processos.py[m
[1m+++ b/routes/processos.py[m
[36m@@ -148,11 +148,11 @@[m [mtd{{padding:4px 8px;border-bottom:1px solid #eee}}[m
 </style></head><body>[m
 [m
 <h1>Prefeitura Municipal de Dias d'Ávila</h1>[m
[31m-<p class="sub">Anexo I — Lei Nº 393/2013 &amp; Decreto Nº 014/09 | Requisição de Diárias e Autorização de Deslocamento</p>[m
[32m+[m[32m<p class="sub">Anexo I — Lei Nº 393/2013 &amp; Decreto Nº 1.313/2013 | Requisição de Diárias </p>[m
 [m
 <div class="section"><div class="sh">Identificação</div><div class="sb">[m
 <div class="row c3">[m
[31m-  <div class="f"><label>Formulário Nº</label><span>{p.num_form}</span></div>[m
[32m+[m[32m  <div class="f"><label>Requisição de Diárias Nº</label><span>{p.num_form}</span></div>[m
   <div class="f"><label>Data de Emissão</label><span>{fmt_date(p.data_emissao)}</span></div>[m
   <div class="f"><label>Status</label><span>{p.status_form or '—'}</span></div>[m
 </div></div></div>[m
[36m@@ -192,7 +192,7 @@[m [mtd{{padding:4px 8px;border-bottom:1px solid #eee}}[m
   <thead><tr><th>Classe</th><th>Tipo</th><th>Qtd. Inteiras</th><th>Qtd. Meias</th><th>Valor Unit.</th></tr></thead>[m
   <tbody><tr><td>{p.r_classe or '—'}</td><td>{p.r_tipo or '—'}</td><td>{p.r_qtd_int or 0}</td><td>{p.r_qtd_meio or 0}</td><td>{fmt_brl(p.r_valor)}</td></tr></tbody>[m
 </table>[m
[31m-<div class="total"><span>Total a Receber Adiantado:</span><strong>{fmt_brl(adiantado)}</strong></div>[m
[32m+[m[32m<div class="total"><span>Total a Receber:</span><strong>{fmt_brl(adiantado)}</strong></div>[m
 </div></div>[m
 [m
 <div class="section"><div class="sh">5. Pagamento</div><div class="sb">[m
[36m@@ -208,7 +208,7 @@[m [mtd{{padding:4px 8px;border-bottom:1px solid #eee}}[m
 </div>[m
 <div class="assin">[m
   <div class="ab">Assinatura do Beneficiário<br>CPF: ________________________</div>[m
[31m-  <div class="ab">Assinatura do Ordenador de Despesa<br>Responsável Autorizante</div>[m
[32m+[m[32m  <div class="ab">Assinatura do Ordenador de Despesa<br></div>[m
 </div>[m
 </div></div>[m
 [m
[1mdiff --git a/templates/formulario.html b/templates/formulario.html[m
[1mindex 987cf7e..b2055b6 100644[m
[1m--- a/templates/formulario.html[m
[1m+++ b/templates/formulario.html[m
[36m@@ -19,11 +19,11 @@[m
   <div class="card-header">Identificação do Formulário</div>[m
   <div class="card-body">[m
     <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">[m
[31m-      <div class="field"><label>Formulário Nº</label>[m
[32m+[m[32m      <div class="field"><label>Requisição de Diárias Nº</label>[m
         <input type="text" name="num_form" value="{{ num_form }}" readonly class="ro"></div>[m
       <div class="field"><label>Data de Emissão</label>[m
         <input type="date" name="data_emissao" value="{{ p.data_emissao if p else hoje }}" {{ 'readonly' if readonly }}></div>[m
[31m-      <div class="field"><label>Status</label>[m
[32m+[m[32m      <div class="field"><label>Vínculo[m
         <select name="status_form" {{ 'disabled' if readonly }}>[m
           {% for opt in ['Agente Político','Comissionado','Efetivo','Contratado','Convidado'] %}[m
           <option {{ 'selected' if p and p.status_form == opt }}>{{ opt }}</option>[m
[36m@@ -58,7 +58,7 @@[m
             ('Controlador Geral','Comissionado — Controlador Geral'),[m
             ('Procurador Geral','Comissionado — Procurador Geral'),[m
             ('Chefe de gabinete','Comissionado — Chefe de Gabinete'),[m
[31m-            ('Demais servidores','Efetivo / Contratado — Demais Servidores'),[m
[32m+[m[32m            ('Demais servidores','Demais Servidores'),[m
             ('Colaboradores eventuais','Convidado / Colaborador Eventual')[m
           ] %}[m
           <option value="{{ v }}" {{ 'selected' if p and p.tipo_benef == v }}>{{ l }}</option>[m
[36m@@ -107,7 +107,7 @@[m
     <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">[m
       <div class="field"><label>14. Tipo de Viagem</label>[m
         <select id="tipo_viagem" name="tipo_viagem" onchange="calcDiaria()" {{ 'disabled' if readonly }}>[m
[31m-          <option value="">Selecione...</option>[m
[32m+[m[32m          <option value="">Selecione...</option>sss[m
           <option value="no_estado"   {{ 'selected' if p and p.tipo_viagem=='no_estado' }}>Dentro do Estado</option>[m
           <option value="fora_estado" {{ 'selected' if p and p.tipo_viagem=='fora_estado' }}>Fora do Estado</option>[m
         </select>[m
[36m@@ -269,7 +269,7 @@[m
 <div class="btn-row no-print" style="display:flex;gap:10px;justify-content:flex-end;margin-top:16px">[m
   <a href="{{ url_for('processos.listar') }}" class="btn btn-secondary">Cancelar</a>[m
   <button type="submit" name="acao" value="rascunho" class="btn btn-secondary">💾 Salvar Rascunho</button>[m
[31m-  <button type="submit" name="acao" value="submeter" class="btn btn-primary">📤 Salvar e Submeter para Aprovação</button>[m
[32m+[m[32m  <button type="submit" name="acao" value="submeter" class="btn btn-primary">📤 Salvar e Submeter para Análise[m
 </div>[m
 {% else %}[m
 <div style="margin-top:16px;display:flex;gap:10px;justify-content:flex-end">[m
[36m@@ -290,13 +290,13 @@[m [minput[readonly],input.ro{background:#f0f2f5;color:#555}[m
 <script>[m
 const VALORES = {[m
   "Prefeito":               {no_estado:618.96, fora_estado:990.32},[m
[31m-  "Vice-Prefeito":          {no_estado:495.17, fora_estado:742.74},[m
[32m+[m[32m  "Vice-Prefeito":          {no_estado:495.17, fora_estado:990.32},[m
   "Secretário":             {no_estado:495.17, fora_estado:742.74},[m
   "Controlador Geral":      {no_estado:495.17, fora_estado:742.74},[m
   "Procurador Geral":       {no_estado:495.17, fora_estado:742.74},[m
   "Chefe de gabinete":      {no_estado:495.17, fora_estado:742.74},[m
[31m-  "Demais servidores":      {no_estado:371.38, fora_estado:200.00},[m
[31m-  "Colaboradores eventuais":{no_estado:105.25, fora_estado: 80.00}[m
[32m+[m[32m  "Demais servidores":      {no_estado:371.38, fora_estado:618,96.},[m
[32m+[m[32m  "Colaboradores eventuais":{no_estado:105.25, fora_estado: 175,42}[m
 };[m
 [m
 function fmtBRL(v){ return 'R$ ' + v.toFixed(2).replace('.',',').replace(/\B(?=(\d{3})+(?!\d))/g,'.'); }[m
