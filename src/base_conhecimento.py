"""Base de conhecimento do assistente de dúvidas do site (web/api/_base.js).

    python src/base_conhecimento.py

Gera, a partir de web/public/dados.json (que já sai do pipeline) e das premissas do README:
- BASE: texto em Markdown com todos os números que o assistente pode citar. O assistente só responde a partir dela,
  e a função confere se cada número da resposta aparece aqui (guardrail de aterramento).
- FAQ: respostas prontas para as perguntas sugeridas, servidas sem chamar a IA (rápido e sem gastar cota).

Sem embeddings: a base inteira cabe no contexto do modelo, o que é mais preciso do que recuperar trechos.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402

DADOS = cfg.ROOT / "web" / "public" / "dados.json"
SAIDA = cfg.ROOT / "web" / "api" / "_base.js"
NIVEL = {"Qualificação até 200h": "até 200h", "Qualificação acima de 200h": "acima de 200h",
         "Técnico": "técnico", "Superior": "superior"}


def n(v: float, casas: int = 1) -> str:
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def i(v: float) -> str:
    return n(v, 0)


def s(v: float, casas: int = 0) -> str:
    return ("+" if v > 0 else "") + n(v, casas)


def premissas() -> str:
    txt = (cfg.ROOT / "README.md").read_text(encoding="utf-8")
    bloco = txt.split("## Premissas e limites", 1)[1].split("\n## ", 1)[0]
    return re.sub(r"`", "", bloco.strip())


def montar() -> tuple[str, list[dict]]:
    d = json.loads(DADOS.read_text(encoding="utf-8"))
    t = next(x for x in d["segmentos"] if x["segmento"] == "Transformação")
    t_sem = next(x for x in d["segmentos_sem_alimentador"] if x["segmento"] == "Transformação")
    cons = next(x for x in d["segmentos"] if x["segmento"] == "Construção")
    ia = d["ia"]
    grupos = sorted(d["grupos"], key=lambda g: -g["kpi1"])
    micros = sorted(d["microrregioes"], key=lambda m: -m["kpi1"])
    macros = sorted([m for m in d["macrofamilias"] if m["kpi1_ok"]], key=lambda m: -m["kpi1"])
    sal = {x["grupo"]: x for x in d["salario_grupo"]}
    q = d["quadrantes"]
    cont = {}
    for p in q["pontos"]:
        cont[p["quadrante"]] = cont.get(p["quadrante"], 0) + 1
    esc = {(e["tipo"], e["faixa"]): e["pct"] for e in d["escolaridade"]}
    part_alim = 100 * (1 - t_sem["movimentos"] / t["movimentos"])

    L = []
    L.append("# Raio-X do Mercado de Trabalho Industrial de Santa Catarina — base de conhecimento\n")
    L.append("Projeto de uma equipe do Datathon CDIA 2026 (Bacharelado em Ciência de Dados e IA, UniSENAI). "
             "A equipe atua como consultoria de dados para a indústria catarinense (cliente: FIESC; quem executa formação: SENAI-SC). "
             "Pergunta central do desafio: quais regiões e setores industriais de SC enfrentam apagão de mão de obra ou expansão acelerada, "
             "e como renda e escolaridade explicam esses gargalos?\n")
    L.append(f"Fonte: {d['meta']['fonte']}. População: {d['meta']['populacao']}. Regiões: microrregiões e mesorregiões do IBGE.\n")

    L.append("## Tese\n")
    L.append("O apagão da indústria catarinense aparece como rotatividade, não como falta de gente. "
             "Num estado com desemprego baixo, muita gente pedindo demissão é sinal de mercado apertado: o trabalhador sai porque tem opção. "
             "Escolaridade não explica o gargalo; o que aparece associado é retenção e salário de reposição menor.\n")

    L.append("## Indicadores (KPIs) e definições\n")
    L.append("- KPI 1, % de saídas a pedido: desligamentos a pedido do trabalhador ÷ total de desligamentos. Adaptação da taxa de quits do JOLTS (EUA).")
    L.append("- KPI 2, saldo por 10 mil habitantes: (admissões − desligamentos em 12 meses) ÷ população do Censo 2022 × 10.000.")
    L.append("- KPI 3, prêmio de contratação: mediana do salário de admissão ÷ mediana do salário de desligamento, na mesma ocupação (CBO) e microrregião, ponderada. Abaixo de 1 = quem entra ganha menos que quem sai. É hipótese da equipe, sinal fraco.")
    L.append("- KPI 4, descasamento de escolaridade: % com superior completo ou mais entre admitidos − entre desligados, em pontos percentuais, na mesma ocupação e microrregião.")
    L.append("- Quadrantes: cada combinação microrregião × setor com volume suficiente cai num de quatro quadrantes, pelas medianas do KPI 2 (eixo x) e do KPI 1 (eixo y): "
             "Expansão sob pressão (cresce e perde gente, sinal mais próximo de apagão), Retenção problemática (não cresce e perde gente), "
             "Expansão saudável (cresce e retém), Estagnado (baixa dinâmica).\n")

    L.append("## Números do estado (indústria de transformação, 12 meses)\n")
    L.append(f"- Movimentações: {i(t['movimentos'])} ({i(t['admissoes'])} admissões e {i(t['desligamentos'])} desligamentos).")
    L.append(f"- Saldo: {s(t['saldo'])} vagas em 12 meses ({n(t['kpi2'])} por 10 mil habitantes). O setor gira muito e quase não cresce.")
    L.append(f"- Saídas a pedido: {n(t['kpi1'])}% dos desligamentos.")
    L.append(f"- Prêmio de contratação: {n(t['kpi3'], 3)}; quem entra ganha {n(100 * (1 - t['kpi3']))}% menos que quem sai na mesma ocupação e região (cobertura {n(t['kpi3_cob'], 0)}% dos movimentos).")
    L.append(f"- Descasamento de escolaridade: {n(t['kpi4'], 2)} pontos percentuais (cobertura {n(t['kpi4_cob'], 0)}%): quem entra tem praticamente a mesma escolaridade de quem sai.")
    L.append(f"- Construção (segmento separado): {i(cons['movimentos'])} movimentações, saldo {s(cons['saldo'])}, {n(cons['kpi1'])}% de saídas a pedido.")
    L.append(f"- Alimentador de linha de produção (CBO 784205): uma única ocupação responde por {n(part_alim, 0)}% das movimentações da transformação. "
             f"Sem ela, o saldo da transformação seria {s(t_sem['saldo'])} em vez de {s(t['saldo'])}.\n")

    L.append("## Setores da transformação (grupos setoriais, 12 meses)\n")
    L.append("| Setor | % saídas a pedido | Saldo (vagas) | Saldo por 10 mil hab. | % a pedido sem o alimentador de linha | Salário mediano de quem entra | de quem sai | Prêmio de contratação |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for g in grupos:
        sg = sal.get(g["grupo"], {})
        L.append(f"| {g['grupo']} | {n(g['kpi1'])}% | {s(g['saldo'])} | {s(g['kpi2'], 1)} | {n(g['kpi1_sem'])}% | "
                 f"R$ {i(sg.get('admitidos', 0))} | R$ {i(sg.get('desligados', 0))} | {n(g['kpi3'], 3) if g.get('kpi3') else 'n/d'} |")
    L.append(f"\nMédia de SC na transformação: {n(t['kpi1'])}% de saídas a pedido. Em todos os setores, o salário mediano de quem entra é menor que o de quem sai.\n")

    L.append("## Microrregiões (transformação, 12 meses)\n")
    L.append("| Microrregião | Mesorregião | % saídas a pedido | Saldo (vagas) | Saldo por 10 mil hab. | Movimentações | Prêmio de contratação |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for m in micros:
        L.append(f"| {m['nome']} | {m['meso']} | {n(m['kpi1'])}% | {s(m['saldo'])} | {s(m['kpi2'], 1)} | {i(m['movimentos'])} | {n(m['kpi3'], 3) if m.get('kpi3') else 'n/d'} |")
    top2 = sorted(micros, key=lambda m: -m["kpi2"])
    L.append(f"\nMaior expansão: {top2[0]['nome']} ({s(top2[0]['kpi2'], 1)} por 10 mil hab.). Maior encolhimento: {top2[-1]['nome']} ({s(top2[-1]['kpi2'], 1)}). "
             "Leitura: o Oeste (agroindústria) cresce e perde gente; o Vale do Itajaí (têxtil) encolhe e perde gente.\n")

    L.append("## Quadrantes (microrregião × setor)\n")
    L.append("Contagem: " + "; ".join(f"{k}: {v}" for k, v in cont.items()) + ".")
    for quad in ["Expansão sob pressão", "Retenção problemática"]:
        pts = sorted([p for p in q["pontos"] if p["quadrante"] == quad], key=lambda p: -p["movimentos"])[:10]
        L.append(f"\nMaiores em {quad}: " + "; ".join(
            f"{p['micro']} · {p['grupo']} ({n(p['kpi1'])}% a pedido, saldo {s(p['saldo'])})" for p in pts) + ".")
    L.append("")

    L.append("## Macrofamílias de ocupação (classificadas pela IA)\n")
    L.append(f"Método: o {ia['modelo']} (Google Gemini) classificou as {i(ia['cbos_llm'])} ocupações (CBOs) que cobrem 95% das movimentações da indústria "
             f"em {ia['areas']} áreas e {ia['niveis']} níveis de formação (Qualificação até 200h, Qualificação acima de 200h, Técnico, Superior), "
             "com lista fechada de categorias imposta por esquema JSON, temperatura 0 e revisão humana. "
             f"{i(ia['cbos_heranca'])} ocupações herdaram a classificação pela família da CBO; {i(ia['cbos_outros'])} pequenas (2,4% dos movimentos) ficaram como Outros. "
             "Zero respostas fora da lista fechada; 8 ocupações foram para revisão humana. "
             "O modelo inicial (gemini-3.8-flash) atingiu o limite do plano gratuito; a equipe refez toda a classificação num único modelo para manter a consistência.\n")
    L.append("| Área | Nível | % saídas a pedido | Desligamentos | Saldo | Prêmio de contratação |")
    L.append("| --- | --- | --- | --- | --- | --- |")
    for m in macros:
        L.append(f"| {m['area']} | {NIVEL.get(m['nivel'], m['nivel'])} | {n(m['kpi1'])}% | {i(m['desligamentos'])} | {s(m['saldo'])} | {n(m['kpi3'], 3) if m.get('kpi3') else 'n/d'} |")
    L.append("")

    L.append("## Escolaridade de quem entra × quem sai (transformação)\n")
    for f in ["Até fundamental", "Médio", "Superior incompleto", "Superior ou mais"]:
        L.append(f"- {f}: admitidos {n(esc.get(('Admitidos', f), 0))}% · desligados {n(esc.get(('Desligados', f), 0))}%")
    L.append("")

    L.append("## Recomendações (aprovadas pela equipe)\n")
    for k, r in enumerate(d["recomendacoes"], 1):
        ind = r.get("indicador_de_acompanhamento") or {}
        L.append(f"{k}. {r['acao']}. Onde: {r['regiao']}. Para quem: {r['macrofamilia']}. Por quê: {r['porque']}. "
                 f"Quem executa: {r['quem_executa']}. Como medir: {ind.get('kpi')}, linha de base {ind.get('linha_de_base')} "
                 f"({ind.get('unidade', '')}), fonte {ind.get('fonte')}.")
    L.append("")

    L.append("## Testes de validação\n")
    for x in d["testes"]:
        L.append(f"- {x['teste']} ({x['grupo']}): obtido {x['obtido']}; critério {x['criterio']}; resultado {x['resultado']}.")
    L.append("- T1 compara o saldo jan–mai/2026 com o boletim da FIESC: diferença de 0,01% na transformação. "
             "T3 reprovado: o ranking muda sem o alimentador de linha, por isso o diagnóstico mostra os dois cenários. "
             "T6 (concordância da IA com revisores humanos) ainda pendente.\n")

    L.append("## Premissas e limites\n")
    L.append(premissas())
    L.append("")

    L.append("## Sobre o site e o assistente\n")
    L.append("O site mostra a análise em cinco partes: Onde (mapa), Setores (quadrantes), Por quê, O que fazer (3 recomendações) e Método. "
             "Os números vêm de um pipeline em Python (Polars) que lê os microdados do Novo CAGED, filtra a indústria, cruza com IBGE e calcula os KPIs. "
             "Este assistente responde dúvidas usando só esta base, com o Google Gemini.")
    base = "\n".join(L)

    faq = [
        {"pergunta": "O que vocês chamam de apagão?",
         "resposta": f"O CAGED mede fluxo de contratações e demissões, não vagas abertas. Por isso inferimos o apagão por sinais indiretos. "
                     f"O principal: {n(t['kpi1'])}% dos desligamentos da indústria de transformação são a pedido do trabalhador, "
                     f"enquanto o saldo do ano foi de só {s(t['saldo'])} vagas. O setor gira muito e quase não cresce: o apagão aparece como rotatividade."},
        {"pergunta": "Onde está o maior problema?",
         "resposta": f"No Oeste catarinense, que cresce e perde gente ao mesmo tempo: {micros[0]['nome']} tem {n(micros[0]['kpi1'])}% das saídas a pedido "
                     f"e {micros[1]['nome']}, {n(micros[1]['kpi1'])}%. {top2[0]['nome']} é o maior polo de expansão ({s(top2[0]['kpi2'], 1)} vagas por 10 mil habitantes). "
                     f"Já o Vale do Itajaí, puxado pelo têxtil, encolhe e também perde gente."},
        {"pergunta": "Por que as pessoas pedem demissão?",
         "resposta": f"Os dados não mostram causa, mas mostram dois sinais associados. Quem entra ganha {n(100 * (1 - t['kpi3']))}% menos que quem sai, "
                     f"na mesma ocupação e região (prêmio {n(t['kpi3'], 3)}). E a escolaridade de quem entra é praticamente igual à de quem sai "
                     f"({n(t['kpi4'], 2)} ponto percentual). Ou seja: o gargalo não é falta de formação, é retenção e salário de reposição."},
        {"pergunta": "Como vocês usaram IA?",
         "resposta": f"O Google Gemini ({ia['modelo']}) agrupou as {i(ia['cbos_llm'])} ocupações que cobrem 95% das movimentações em "
                     f"{ia['areas']} áreas e {ia['niveis']} níveis de formação. Usamos lista fechada de categorias, temperatura 0 e revisão humana: "
                     "zero respostas fora da lista. É isso que liga as recomendações a grupos de ocupação, e não a cargos soltos."},
        {"pergunta": "Quais são as recomendações?",
         "resposta": " ".join(f"{k}) {r['acao']} em {r['regiao'].split(' (')[0]}." for k, r in enumerate(d["recomendacoes"], 1))
                     .replace("em Oeste", "no Oeste")
                     + " Cada uma tem uma linha de base para acompanhar todo mês no Novo CAGED."},
        {"pergunta": "Os dados são confiáveis?",
         "resposta": "O saldo da transformação calculado pela equipe bate com o boletim oficial da FIESC com 0,01% de diferença (jan–mai/2026). "
                     "Rodamos 7 testes de robustez; o que reprovou está declarado. Um exemplo: uma única ocupação, o alimentador de linha, pesa muito, "
                     "e por isso mostramos os resultados com e sem ela."},
    ]
    return base, faq


def main() -> Path:
    base, faq = montar()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    js = ("// Gerado por src/base_conhecimento.py — não editar à mão.\n"
          f"export const BASE = {json.dumps(base, ensure_ascii=False)};\n"
          f"export const FAQ = {json.dumps(faq, ensure_ascii=False, indent=1)};\n")
    SAIDA.write_text(js, encoding="utf-8")
    print(f"{SAIDA.relative_to(cfg.ROOT)}: {len(base):,} caracteres (~{len(base) // 4:,} tokens) · {len(faq)} perguntas prontas")
    return SAIDA


if __name__ == "__main__":
    main()
