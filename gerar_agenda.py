import csv
from datetime import date, datetime
from workalendar.america import BrazilCeara
import os

# Configuração
hoje = date.today()
ANO = hoje.year
MES = hoje.month
NOME_SITE = "Agenda Tributária – Avançar Contadores"

cal = BrazilCeara()

# Dicionários para tradução
MESES = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}
DIAS_SEMANA = {
    'Monday': 'segunda-feira', 'Tuesday': 'terça-feira', 'Wednesday': 'quarta-feira',
    'Thursday': 'quinta-feira', 'Friday': 'sexta-feira', 'Saturday': 'sábado', 'Sunday': 'domingo'
}

# Função para último dia útil
def ultimo_dia_util(calendario, ano, mes):
    import calendar
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data = date(ano, mes, ultimo_dia)
    while data.month == mes and not calendario.is_working_day(data):
        data = date.fromordinal(data.toordinal() - 1)
    return data

# Carregar obrigações
obrigacoes = []
if os.path.exists('obrigatorios.csv'):
    with open('obrigatorios.csv', encoding='utf-8') as f:
        for linha in csv.DictReader(f):
            obrigacoes.append(linha)
else:
    print("❌ Arquivo 'obrigatorios.csv' não encontrado!")
    exit()

# Gerar agenda e alertas
agenda = []
alertas = []

for item in obrigacoes:
    try:
        dia = int(item['dia_fixo'])
        data = date(ANO, MES, dia)
    except ValueError:
        continue

    descricao = item['imposto']
    agenda.append({'data': data, 'descricao': descricao, 'fonte': item['fonte']})

    if not cal.is_working_day(data):
        nome_dia_en = data.strftime('%A')
        nome_dia_pt = DIAS_SEMANA.get(nome_dia_en, nome_dia_en.lower())
        feriados = [f[0] for f in cal.holidays(ANO) if f[0] == data]
        motivo = "feriado" if feriados else nome_dia_pt
        alertas.append({'data': data, 'imposto': descricao, 'motivo': motivo})

# Adicionar último dia útil
ultimo_util = ultimo_dia_util(cal, ANO, MES)
agenda.append({'data': ultimo_util, 'descricao': 'IRPJ / CSLL', 'fonte': 'federal'})
agenda.append({'data': ultimo_util, 'descricao': 'Parcelamento REFIS (Federal)', 'fonte': 'federal'})
agenda.append({'data': ultimo_util, 'descricao': 'ICMS Combustíveis (Indústria)', 'fonte': 'estadual'})
agenda.append({'data': ultimo_util, 'descricao': 'Parcelamento REFIS (SEFAZ)', 'fonte': 'estadual'})

agenda.sort(key=lambda x: x['data'])

# Preparar dados para JS
dados_js = ",\n            ".join([
    f'{{"data": "{item["data"].strftime("%d/%m/%Y")}", "descricao": "{item["descricao"]}"}}'
    for item in agenda
])

# ========== GERAR index.html COM DESIGN MODERNO ==========
mes_nome = MESES[MES]
html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{NOME_SITE} – {mes_nome}/{ANO}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --cor-primaria: #1e40af;
            --cor-primaria-clara: #3b82f6;
            --cor-alerta: #f59e0b;
            --cor-sucesso: #10b981;
            --cor-fundo: #f8fafc;
            --cor-texto: #1e293b;
            --cor-cinza: #e2e8f0;
            --sombra: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--cor-fundo);
            color: var(--cor-texto);
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            text-align: center;
            padding: 30px 0;
            margin-bottom: 25px;
            background: white;
            border-radius: 16px;
            box-shadow: var(--sombra);
        }}
        .logo {{
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--cor-primaria);
            margin-bottom: 8px;
        }}
        .subtitulo {{
            color: #64748b;
            font-size: 1.1rem;
            font-weight: 500;
        }}
        .btn-mensagem {{
            display: block;
            width: 100%;
            background: var(--cor-sucesso);
            color: white;
            padding: 16px;
            font-size: 1.1rem;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            margin: 25px 0;
            box-shadow: var(--sombra);
            transition: all 0.2s;
        }}
        .btn-mensagem:hover {{
            background: #0da271;
            transform: translateY(-2px);
        }}
        .btn-mensagem:active {{
            transform: translateY(0);
        }}
        #painel-mensagem {{
            display: none;
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: var(--sombra);
            margin: 20px 0;
        }}
        .painel-titulo {{
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: var(--cor-primaria);
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .obrigacao {{
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--cor-cinza);
        }}
        .obrigacao:last-child {{
            border-bottom: none;
        }}
        .obrigacao input {{
            margin-right: 12px;
            width: 18px;
            height: 18px;
        }}
        .obrigacao label {{
            font-size: 1rem;
            cursor: pointer;
        }}
        textarea {{
            width: 100%;
            min-height: 160px;
            padding: 16px;
            font-size: 1rem;
            margin-top: 20px;
            font-family: 'Inter', monospace;
            border: 1px solid var(--cor-cinza);
            border-radius: 12px;
            resize: vertical;
        }}
        .alerta {{
            background: #fffbeb;
            border-left: 4px solid var(--cor-alerta);
            padding: 20px;
            border-radius: 0 12px 12px 0;
            margin: 25px 0;
            box-shadow: var(--sombra);
        }}
        .alerta h3 {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: #b45309;
            margin-bottom: 12px;
            font-size: 1.2rem;
        }}
        .alerta ul {{
            padding-left: 20px;
        }}
        .alerta li {{
            margin: 8px 0;
            color: #92400e;
        }}
        table {{
            width: 100%;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--sombra);
            margin-top: 10px;
        }}
        th, td {{
            padding: 16px 20px;
            text-align: left;
        }}
        th {{
            background: var(--cor-primaria);
            color: white;
            font-weight: 600;
            font-size: 1.05rem;
        }}
        tr:nth-child(even) {{
            background-color: #f1f5f9;
        }}
        tr:hover {{
            background-color: #dbeafe;
        }}
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .tag-federal {{
            background: #dbeafe;
            color: #1d4ed8;
        }}
        .tag-estadual {{
            background: #dcfce7;
            color: #166534;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            color: #64748b;
            font-size: 0.95rem;
            border-top: 1px solid var(--cor-cinza);
        }}
        @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}
            header {{
                padding: 20px 0;
            }}
            .logo {{
                font-size: 1.8rem;
            }}
            th, td {{
                padding: 12px 15px;
                font-size: 0.95rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">📅 {NOME_SITE}</div>
            <div class="subtitulo">Agenda de {mes_nome} / {ANO}</div>
        </header>

        <button class="btn-mensagem" onclick="togglePainel()">💬 Gerar Mensagem Personalizada para Clientes</button>
        
        <div id="painel-mensagem">
            <div class="painel-titulo">📝 Selecione os impostos e copie sua mensagem</div>
            <div id="lista-obrigacoes"></div>
            <textarea id="saida" placeholder="Sua mensagem personalizada aparecerá aqui. Clique nas opções acima para atualizar."></textarea>
        </div>

"""

if alertas:
    html += '        <div class="alerta">\n            <h3>⚠️ Atenção – Datas em Finais de Semana ou Feriados</h3>\n            <p>As seguintes obrigações caem em dias não úteis. Confira no site oficial se houve alteração:</p>\n            <ul>\n'
    for a in alertas:
        html += f'                <li><strong>{a["data"].strftime("%d/%m/%Y")}</strong> ({a["motivo"]}) → {a["imposto"]}</li>\n'
    html += '            </ul>\n        </div>\n'

html += """        <table>
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Obrigação</th>
                    <th>Fonte</th>
                </tr>
            </thead>
            <tbody>
"""

for item in agenda:
    tag = 'tag-federal' if item['fonte'] == 'federal' else 'tag-estadual'
    tag_texto = 'Federal' if item['fonte'] == 'federal' else 'Estadual (CE)'
    html += f"""                <tr>
                    <td>{item['data'].strftime('%d/%m/%Y')}</td>
                    <td>{item['descricao']}</td>
                    <td><span class="tag {tag}">{tag_texto}</span></td>
                </tr>\n"""

html += """            </tbody>
        </table>

        <footer>
            <p>Atualizado em """ + datetime.now().strftime('%d/%m/%Y às %H:%M') + """ • Dados gerados com base em regras do escritório Avançar Contadores</p>
        </footer>
    </div>

    <script>
        const obrigacoes = [
            // ⚠️ DADOS DINÂMICOS AQUI ⚠️
        ];

        function togglePainel() {
            const painel = document.getElementById('painel-mensagem');
            painel.style.display = painel.style.display === 'block' ? 'none' : 'block';
            if (painel.style.display === 'block' && !painel.innerHTML.includes('<div class="obrigacao">')) {
                renderizarCheckboxes();
            }
        }

        function renderizarCheckboxes() {
            const container = document.getElementById('lista-obrigacoes');
            container.innerHTML = '';
            obrigacoes.forEach((item, i) => {
                const div = document.createElement('div');
                div.className = 'obrigacao';
                div.innerHTML = `
                    <label>
                        <input type="checkbox" data-index="${i}" checked> 
                        ${item.descricao} – ${item.data}
                    </label>
                `;
                container.appendChild(div);
            });
            gerarMensagem();
        }

        document.addEventListener('change', function(e) {
            if (e.target.matches('input[type="checkbox"]')) {
                gerarMensagem();
            }
        });

        function gerarMensagem() {
            const selecionados = [];
            document.querySelectorAll('#lista-obrigacoes input:checked').forEach(el => {
                const idx = parseInt(el.dataset.index);
                selecionados.push(obrigacoes[idx]);
            });

            let texto = `Sua Agenda Tributária – Avançar Contadores\\nNão esqueça do envio dos seus impostos. Os prazos são:\\n\\n`;
            const meses = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
            
            selecionados.forEach(item => {
                const [dia, mesNum] = item.data.split('/');
                const mes = meses[parseInt(mesNum) - 1];
                texto += `• ${item.descricao} – ${dia} de ${mes}\\n`;
            });

            texto += `\\nFaça o pagamento das guias antes dessas datas e conte conosco para evitar multas e atrasos.`;
            document.getElementById('saida').value = texto.replace(/\\\\n/g, '\\n');
        }
    </script>
</body>
</html>"""

# Injetar os dados reais
html = html.replace('// ⚠️ DADOS DINÂMICOS AQUI ⚠️', f'{dados_js}')

# Salvar
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Mensagem final
print("\n" + "="*60)
print(f"✅ index.html gerado com design moderno e profissional!")
print(f"   Mês: {mes_nome} / {ANO}")
print(f"   Abra 'index.html' e aproveite o novo visual!")
if alertas:
    print(f"\n⚠️  {len(alertas)} alerta(s) de feriado/fim de semana.")
print("="*60)