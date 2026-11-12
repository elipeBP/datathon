"""Exporta os agregados do pipeline para o site React (web/public/).

    python src/exportar_web.py

O site não calcula nada: ele só lê web/public/dados.json e web/public/sc_microrregioes.geojson,
gerados aqui a partir de data/processed/, data/reference/ e app/recomendacoes.yaml.
"""
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

import polars as pl
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402

SAIDA = cfg.ROOT / "web" / "public"
SEG = "Transformação"
TEXTO = {"cod_microrregiao": pl.Utf8, "cod_mesorregiao": pl.Utf8, "divisao_cnae": pl.Utf8}


def ler(nome: str) -> pl.DataFrame:
    return pl.read_csv(cfg.PROCESSED / f"{nome}.csv", schema_overrides=TEXTO)


def limpar(v):
    """NaN/inf viram null; floats arredondados para o JSON ficar pequeno."""
    if isinstance(v, float):
        return None if (math.isnan(v) or math.isinf(v)) else round(v, 4)
    return v


def registros(df: pl.DataFrame, colunas: dict[str, str]) -> list[dict]:
    """colunas = {nome_no_csv: nome_no_json}."""
    d = df.select([pl.col(c).alias(n) for c, n in colunas.items()])
    return [{k: limpar(v) for k, v in r.items()} for r in d.iter_rows(named=True)]


def testes() -> list[dict]:
    linhas = cfg.TESTES_MD.read_text(encoding="utf-8").splitlines()
    out = []
    for l in linhas:
        cel = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cel) == 7 and re.fullmatch(r"\d{4}-\d{2}-\d{2}", cel[0]):
            out.append(dict(zip(["data", "teste", "grupo", "obtido", "referencia", "criterio", "resultado"], cel)))
    return out


def modelo_web() -> dict | None:
    """Resumo do modelo das saídas a pedido (src/modelo.py) para o site."""
    resumo_p = cfg.PROCESSED / "modelo_pedido_resumo.json"
    efeitos_p = cfg.PROCESSED / "modelo_pedido_efeitos.csv"
    if not (resumo_p.exists() and efeitos_p.exists()):
        return None
    r = json.loads(resumo_p.read_text(encoding="utf-8"))
    ef = pl.read_csv(efeitos_p)
    m = r["mercado"]
    return {
        "mercado": {"celulas": m["celulas"], "desligamentos": m["desligamentos"], "efeito_sal10_pp": limpar(m["efeito_sal10_pp"]),
                    "p_sal": limpar(m["p_sal"]),
                    "efeitos": [{k: limpar(e[k]) for k in ("variavel", "nome", "efeito_1dp_pp", "p")} for e in m["efeitos"]],
                    "robustez": [{k: limpar(x[k]) for k in ("recorte", "celulas", "efeito_sal10_pp", "p_sal", "p_premio")} for x in m["robustez"]]},
        "perfil": {"n": r["n"], "taxa_pedido": limpar(r["taxa_pedido"]), "auc_logit": limpar(r["auc_logit"]), "auc_gbm": limpar(r["auc_gbm"]),
                   "efeitos": registros(ef, {"fator": "fator", "fator_nome": "fator_nome", "nivel": "nivel", "prob_prevista": "prob",
                                             "dif_pp_vs_ref": "dif_pp", "referencia": "ref", "n": "n", "p": "p"})},
    }


def geojson_compacto() -> dict:
    """Arredonda as coordenadas a 4 casas (~11 m): metade do tamanho, mesma forma."""
    geo = json.loads(cfg.GEOJSON_MICRO.read_text(encoding="utf-8"))

    def r(c):
        return [round(c[0], 4), round(c[1], 4)] if isinstance(c[0], (int, float)) else [r(x) for x in c]

    for f in geo["features"]:
        f["geometry"]["coordinates"] = r(f["geometry"]["coordinates"])
    return geo


def main() -> Path:
    SAIDA.mkdir(parents=True, exist_ok=True)
    k = ["movimentos", "admissoes", "desligamentos", "saldo"]
    base = {c: c for c in k} | {"kpi1_pct_a_pedido": "kpi1", "kpi2_saldo_10mil_hab": "kpi2",
                                 "kpi1_suficiente": "kpi1_ok", "kpi2_suficiente": "kpi2_ok"}
    celula = {"kpi3_premio_contratacao": "kpi3", "kpi3_cobertura_pct": "kpi3_cob",
              "kpi4_descasamento_sup_pp": "kpi4", "kpi4_cobertura_pct": "kpi4_cob"}

    seg = ler("kpis_segmento")
    seg_sem = ler("kpis_segmento_sem_cbo_dominante")
    grp = ler("kpis_grupo_setorial").filter(pl.col("segmento") == SEG)
    grp_sem = ler("kpis_grupo_setorial_sem_cbo_dominante").filter(pl.col("segmento") == SEG).select(
        "grupo_setorial", pl.col("kpi1_pct_a_pedido").alias("kpi1_sem_alimentador"),
        pl.col("saldo").alias("saldo_sem_alimentador"))
    mic = ler("kpis_microrregiao").filter(pl.col("segmento") == SEG)
    quad = ler("quadrantes").filter(pl.col("segmento") == SEG)
    macro = ler("kpis_macrofamilia").filter(pl.col("segmento") == SEG)
    esc = ler("perfil_escolaridade_grupo").filter(pl.col("segmento") == SEG)
    sal = ler("perfil_salario_grupo").filter(pl.col("segmento") == SEG)
    mf = pl.read_csv(cfg.MACROFAMILIAS_CSV, infer_schema_length=0)

    esc_tot = (esc.group_by("tipo", "faixa_escolaridade").agg(pl.col("n").sum())
               .with_columns((100 * pl.col("n") / pl.col("n").sum().over("tipo")).alias("pct")))
    sal_p = sal.pivot(on="tipo", index="grupo_setorial", values="salario_mediano")

    recs = yaml.safe_load(cfg.RECOMENDACOES_YAML.read_text(encoding="utf-8"))
    prompt = (cfg.ROOT / "prompts" / "macrofamilias_v1.md").read_text(encoding="utf-8")
    modelo = re.search(r"gemini-[\w.\-]+", prompt)

    dados = {
        "meta": {"gerado_em": f"{datetime.now():%Y-%m-%d %H:%M}", "segmento": SEG,
                 "fonte": "Novo CAGED (MTE), microdados de Santa Catarina, set/2025–ago/2026",
                 "populacao": "Censo 2022 (IBGE)", "regioes": "Microrregiões e mesorregiões do IBGE"},
        "segmentos": registros(seg, {"segmento": "segmento", **base, **celula}),
        "segmentos_sem_alimentador": registros(seg_sem, {"segmento": "segmento", **base}),
        "grupos": registros(grp.join(grp_sem, on="grupo_setorial", how="left"),
                            {"grupo_setorial": "grupo", **base, "kpi1_sem_alimentador": "kpi1_sem",
                             "saldo_sem_alimentador": "saldo_sem", **celula}),
        "microrregioes": registros(mic, {"cod_microrregiao": "cod", "microrregiao": "nome",
                                         "mesorregiao": "meso", "pop": "pop", **base, **celula}),
        "quadrantes": {
            "mediana_kpi2": limpar(quad["med_x"][0]), "mediana_kpi1": limpar(quad["med_y"][0]),
            "pontos": registros(quad, {"microrregiao": "micro", "mesorregiao": "meso", "grupo_setorial": "grupo",
                                       "movimentos": "movimentos", "saldo": "saldo", "desligamentos": "desligamentos",
                                       "kpi1_pct_a_pedido": "kpi1", "kpi2_saldo_10mil_hab": "kpi2",
                                       "quadrante": "quadrante"}),
        },
        "macrofamilias": registros(macro, {"area": "area", "nivel": "nivel", **base, **celula}),
        "escolaridade": registros(esc_tot, {"tipo": "tipo", "faixa_escolaridade": "faixa", "n": "n", "pct": "pct"}),
        "salario_grupo": registros(sal_p, {"grupo_setorial": "grupo", "Admitidos": "admitidos", "Desligados": "desligados"}),
        "ia": {
            "modelo": modelo.group(0) if modelo else cfg.GEMINI_MODEL,
            "cbos_total": mf.height,
            "cbos_llm": mf.filter(pl.col("origem") == "llm").height,
            "cbos_heranca": mf.filter(pl.col("origem") == "heranca").height,
            "cbos_outros": mf.filter(pl.col("origem") == "outros").height,
            "areas": 15, "niveis": 4,
        },
        "modelo": modelo_web(),
        "recomendacoes": recs.get("recomendacoes", []),
        "recomendacoes_status": recs.get("status_geral"),
        "testes": testes(),
    }
    destino = SAIDA / "dados.json"
    destino.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    geo = SAIDA / "sc_microrregioes.geojson"
    geo.write_text(json.dumps(geojson_compacto(), separators=(",", ":")), encoding="utf-8")
    print(f"{destino.relative_to(cfg.ROOT)}: {destino.stat().st_size / 1e3:.0f} KB · "
          f"{geo.relative_to(cfg.ROOT)}: {geo.stat().st_size / 1e3:.0f} KB")
    return destino


if __name__ == "__main__":
    main()
