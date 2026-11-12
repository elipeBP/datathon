"""Base de busca do agente "Perguntar aos dados" (web/api/_dados.js).

    python src/dados_agente.py

O agente não recebe uma tabela gigante: a função da Vercel identifica na pergunta quais microrregiões, setores
e ocupações estão em jogo e entrega ao modelo só as linhas exatas desses recortes. Cada linha já traz o recorte
escrito por extenso ("Blumenau × Têxtil, confecção e calçados"), para o modelo não atribuir um número do estado
a uma região. Todos os números saem de data/processed/ (pipeline em Python) no formato brasileiro.
"""
import json
import sys
import unicodedata
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402

SAIDA = cfg.ROOT / "web" / "api" / "_dados.js"
TEXTO = {"cod_microrregiao": pl.Utf8, "cod_mesorregiao": pl.Utf8}
NIVEL = {"Qualificação até 200h": "até 200h", "Qualificação acima de 200h": "acima de 200h", "Técnico": "técnico", "Superior": "superior"}

APELIDOS_GRUPO = {
    "Alimentos e bebidas": ["alimento", "alimentos", "bebida", "bebidas", "frigorifico", "frigorificos", "agroindustria", "carne", "frango", "aves", "suinos", "laticinio", "laticinios"],
    "Têxtil, confecção e calçados": ["textil", "texteis", "confeccao", "confeccoes", "calcado", "calcados", "vestuario", "roupa", "roupas", "costura"],
    "Madeira e móveis": ["madeira", "moveis", "movel", "moveleiro", "moveleira", "serraria"],
    "Metalmecânica": ["metalmecanica", "metal", "metalurgia", "metalurgica", "maquinas", "automotivo", "veiculos", "autopecas", "siderurgia"],
    "Eletroeletrônica": ["eletroeletronica", "eletro", "eletronica", "eletrica", "motores", "eletrico"],
    "Plástico e borracha": ["plastico", "plasticos", "borracha"],
    "Papel, celulose e gráfica": ["papel", "celulose", "grafica", "embalagem"],
    "Minerais não metálicos e cerâmica": ["ceramica", "ceramicas", "minerais", "vidro", "cimento", "porcelanato", "revestimento"],
    "Química e farmacêutica": ["quimica", "quimico", "farmaceutica", "farma", "remedio", "medicamento"],
    "Outras da transformação": ["fumo", "tabaco", "joias", "brinquedos"],
    "Construção": ["construcao", "obra", "obras", "construcao civil"],
    "Extrativa": ["extrativa", "mineracao", "carvao"],
    "Utilidades": ["utilidades", "energia", "saneamento", "agua"],
}
APELIDOS_AREA = {
    "Operação de linha e montagem": ["alimentador", "linha de producao", "operacao de linha", "montador", "montagem", "embalador", "operador de maquina"],
    "Alimentos e bebidas": ["magarefe", "abate", "desossa", "acougueiro"],
    "Têxtil, confecção e calçados": ["costureira", "costureiro", "tecelao", "tecelagem", "fiacao"],
    "Metalmecânica e soldagem": ["soldador", "solda", "usinagem", "torneiro", "caldeireiro", "fresador"],
    "Manutenção industrial": ["manutencao", "mecanico", "eletricista", "eletromecanico"],
    "Eletroeletrônica e automação": ["automacao", "bobinador", "instrumentacao"],
    "Madeira e móveis": ["marceneiro", "marcenaria", "serrador"],
    "Plástico, borracha e química": ["injetora", "extrusora", "operador de processo"],
    "Cerâmica, vidro e minerais": ["ceramista", "vidreiro"],
    "Logística e movimentação": ["logistica", "motorista", "empilhadeira", "almoxarife", "conferente", "expedicao"],
    "Qualidade e controle": ["qualidade", "inspetor", "laboratorio", "seguranca do trabalho"],
    "Gestão, administrativo e comercial": ["administrativo", "gestao", "gerente", "supervisor", "vendedor", "comercial", "escritorio", "rh"],
    "Engenharia e P&D": ["engenheiro", "engenheira", "engenharia", "projetista", "pesquisa", "p&d"],
    "Serviços de apoio": ["limpeza", "faxineiro", "porteiro", "vigilante", "cozinha"],
    "Construção": ["pedreiro", "servente", "carpinteiro", "armador"],
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return " ".join("".join(c if c.isalnum() or c in " &" else " " for c in s).split())


def n(v, casas=1):
    if v is None or (isinstance(v, float) and v != v):
        return "n/d"
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def s(v, casas=0):
    return ("+" if v > 0 else "") + n(v, casas)


def ler(nome: str) -> pl.DataFrame:
    return pl.read_csv(cfg.PROCESSED / f"{nome}.csv", schema_overrides=TEXTO)


def linha_kpi(rotulo: str, r: dict, extra: str = "") -> str:
    aviso = "" if r.get("kpi1_suficiente") else " (amostra pequena: menos de 300 desligamentos, ler com cautela)"
    partes = [f"{n(r['kpi1_pct_a_pedido'])}% das saídas a pedido ({n(r['desligamentos'], 0)} desligamentos){aviso}",
              f"saldo {s(r['saldo'])} vagas", f"{n(r['movimentos'], 0)} movimentações"]
    if r.get("kpi2_saldo_10mil_hab") is not None and r.get("pop") and r["pop"] < 7_000_000:
        partes.insert(2, f"{s(r['kpi2_saldo_10mil_hab'], 1)} por 10 mil hab.")
    if r.get("kpi3_premio_contratacao") is not None and r["kpi3_premio_contratacao"] == r["kpi3_premio_contratacao"]:
        partes.append(f"prêmio de contratação {n(r['kpi3_premio_contratacao'], 3)}")
    return f"- [{rotulo}] " + " · ".join(partes) + (f" · {extra}" if extra else "")


def main() -> Path:
    reg = pl.read_csv(cfg.MUNICIPIOS_REGIOES_CSV, infer_schema_length=0)
    micro = ler("kpis_microrregiao").filter(pl.col("segmento") == "Transformação")
    mg = ler("kpis_micro_grupo")
    quad = ler("quadrantes").select("segmento", "microrregiao", "grupo_setorial", "quadrante")
    mg = mg.join(quad, on=["segmento", "microrregiao", "grupo_setorial"], how="left")
    sal = ler("perfil_salario_micro_grupo").filter(pl.col("segmento") == "Transformação")
    sal = sal.pivot(on="tipo", index=["microrregiao", "grupo_setorial"], values=["salario_mediano", "n"])
    mm = ler("kpis_micro_macrofamilia").filter((pl.col("segmento") == "Transformação") & pl.col("kpi1_suficiente"))
    gm = ler("kpis_grupo_macrofamilia").filter(pl.col("kpi1_suficiente"))

    micros = []
    for r in micro.sort("kpi1_pct_a_pedido", descending=True).iter_rows(named=True):
        micros.append({"nome": r["microrregiao"], "meso": r["mesorregiao"], "chave": norm(r["microrregiao"]),
                       "linha": linha_kpi(f"Microrregião de {r['microrregiao']} ({r['mesorregiao']}), toda a transformação", r)})
    apelidos_micro = {"smo": "São Miguel do Oeste", "lages": "Campos de Lages", "floripa": "Florianópolis", "sbs": "São Bento do Sul"}

    municipios = {}
    for r in reg.iter_rows(named=True):
        municipios[norm(r["municipio"])] = r["microrregiao"]

    micro_grupo = {}
    salarios = {(r["microrregiao"], r["grupo_setorial"]): r for r in sal.iter_rows(named=True)}
    for r in mg.sort("movimentos", descending=True).iter_rows(named=True):
        if r["movimentos"] < 100:
            continue
        sr = salarios.get((r["microrregiao"], r["grupo_setorial"]))
        extra = []
        if sr and sr.get("salario_mediano_Admitidos") and (sr.get("n_Admitidos") or 0) >= 50 and (sr.get("n_Desligados") or 0) >= 50:
            extra.append(f"salário mediano de quem entra R$ {n(sr['salario_mediano_Admitidos'], 0)}, de quem sai R$ {n(sr['salario_mediano_Desligados'], 0)}")
        if r.get("quadrante"):
            extra.append(f"quadrante: {r['quadrante']}")
        micro_grupo.setdefault(r["microrregiao"], {})[r["grupo_setorial"]] = linha_kpi(
            f"{r['microrregiao']} × {r['grupo_setorial']}", r, " · ".join(extra))

    micro_macro = {}
    for r in mm.sort("desligamentos", descending=True).iter_rows(named=True):
        micro_macro.setdefault(r["microrregiao"], []).append(
            {"area": r["area"], "linha": linha_kpi(f"{r['microrregiao']} × ocupações de {r['area']} ({NIVEL.get(r['nivel'], r['nivel'])})", r)})
    grupo_macro = {}
    for r in gm.sort("desligamentos", descending=True).iter_rows(named=True):
        grupo_macro.setdefault(r["grupo_setorial"], []).append(
            {"area": r["area"], "linha": linha_kpi(f"SC inteira, setor {r['grupo_setorial']} × ocupações de {r['area']} ({NIVEL.get(r['nivel'], r['nivel'])})", r)})

    dados = {
        "micros": micros, "apelidosMicro": apelidos_micro, "municipios": municipios,
        "grupos": [{"nome": g, "chaves": [norm(g), *a]} for g, a in APELIDOS_GRUPO.items()],
        "areas": [{"nome": g, "chaves": [norm(g), *a]} for g, a in APELIDOS_AREA.items()],
        "microGrupo": micro_grupo, "microMacro": micro_macro, "grupoMacro": grupo_macro,
    }
    SAIDA.write_text("// Gerado por src/dados_agente.py — não editar à mão.\n"
                     f"export const DADOS = {json.dumps(dados, ensure_ascii=False)};\n", encoding="utf-8")
    linhas = len(micros) + sum(len(v) for v in micro_grupo.values()) + sum(len(v) for v in micro_macro.values()) + sum(len(v) for v in grupo_macro.values())
    print(f"{SAIDA.relative_to(cfg.ROOT)}: {SAIDA.stat().st_size / 1e3:.0f} KB · {linhas} linhas de recorte · {len(municipios)} municípios")
    return SAIDA


if __name__ == "__main__":
    main()
