"""SDD 8.3: recomendações candidatas a partir dos KPIs.

    python src/recomendacoes.py

1. Combinações área × nível × microrregião da transformação, com volume suficiente.
2. Classifica cada combinação no quadrante (medianas das combinações elegíveis, como em 5.4).
3. Candidatas: quadrantes "Expansão sob pressão" e "Retenção problemática", KPI 1 acima da mediana de SC,
   ordenadas pelo KPI 1; no máximo uma por área e uma por microrregião entre as 3 escolhidas.
4. Escreve reports/recomendacoes_candidatas.md e app/recomendacoes.yaml (status: rascunho).

A ação sugerida é uma regra simples, só para o rascunho. A equipe escolhe, reescreve e aprova.
"""
import sys
from datetime import datetime
from pathlib import Path

import polars as pl
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.kpis import quadrantes  # noqa: E402

SEGMENTO = "Transformação"
FORMACAO_NIVEIS = {"Qualificação acima de 200h", "Técnico", "Superior"}


def _f(v: float, casas: int = 1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def _i(v: int) -> str:
    return f"{int(v):,}".replace(",", ".")


def acao_sugerida(r: dict, ref: dict) -> tuple[str, str]:
    """Regra do rascunho → (ação, quem executa)."""
    premio_baixo = r.get("kpi3_premio_contratacao") is not None and ref.get("kpi3") is not None \
        and r["kpi3_premio_contratacao"] < ref["kpi3"]
    if r["quadrante"] == "Retenção problemática":
        return ("Revisão de faixa salarial e programa de retenção" if premio_baixo else "Programa de retenção",
                "Empresas do setor, com apoio da FIESC")
    if r["nivel"] in FORMACAO_NIVEIS or (r.get("kpi4_descasamento_sup_pp") or 0) < 0:
        return "Formação profissional direcionada", "SENAI-SC"
    return "Atração de talentos regionais", "FIESC e prefeituras"


def candidatas(proc: Path = cfg.PROCESSED) -> tuple[pl.DataFrame, dict]:
    t = pl.read_csv(proc / "kpis_micro_macrofamilia.csv",
                    schema_overrides={"cod_microrregiao": pl.Utf8, "cod_mesorregiao": pl.Utf8})
    seg = pl.read_csv(proc / "kpis_segmento.csv").filter(pl.col("segmento") == SEGMENTO).row(0, named=True)
    ref = {"kpi1": seg["kpi1_pct_a_pedido"], "kpi3": seg.get("kpi3_premio_contratacao"),
           "kpi4": seg.get("kpi4_descasamento_sup_pp")}
    q = quadrantes(t.filter(pl.col("segmento") == SEGMENTO))
    mediana_kpi1 = q["kpi1_pct_a_pedido"].median()
    c = (q.filter(pl.col("quadrante").is_in(["Expansão sob pressão", "Retenção problemática"])
                  & (pl.col("kpi1_pct_a_pedido") > mediana_kpi1))
         .sort("kpi1_pct_a_pedido", descending=True))
    ref["mediana_combinacoes_kpi1"] = mediana_kpi1
    return c, ref


def escolher_3(c: pl.DataFrame) -> list[dict]:
    escolhidas, areas, micros = [], set(), set()
    for r in c.iter_rows(named=True):
        if r["area"] in areas or r["microrregiao"] in micros:
            continue
        escolhidas.append(r)
        areas.add(r["area"])
        micros.add(r["microrregiao"])
        if len(escolhidas) == 3:
            break
    return escolhidas


def texto(r: dict, ref: dict) -> dict:
    acao, quem = acao_sugerida(r, ref)
    porque = (f"{_f(r['kpi1_pct_a_pedido'])}% dos desligamentos são a pedido, contra {_f(ref['kpi1'])}% na transformação de SC "
              f"(n = {_i(r['desligamentos'])} desligamentos); saldo de {_f(r['kpi2_saldo_10mil_hab'])} por 10 mil habitantes")
    if r.get("kpi3_premio_contratacao") is not None:
        porque += f"; prêmio de contratação {_f(r['kpi3_premio_contratacao'], 3)}"
    return {
        "status": "rascunho",
        "acao": acao,
        "macrofamilia": f"{r['area']} × {r['nivel']}",
        "regiao": f"{r['microrregiao']} ({r['mesorregiao']})",
        "quadrante": r["quadrante"],
        "porque": porque,
        "quem_executa": quem,
        "texto": f"{acao} para {r['area']} × {r['nivel']} em {r['microrregiao']}, porque {porque}. Quem executa: {quem}.",
        "indicador_de_acompanhamento": {
            "kpi": "% de desligamentos a pedido (KPI 1) na macrofamília e na microrregião",
            "linha_de_base": round(r["kpi1_pct_a_pedido"], 1),
            "referencia_sc": round(ref["kpi1"], 1),
            "fonte": "Novo CAGED, mensal (MTE)",
        },
    }


def main(proc: Path = cfg.PROCESSED, yaml_path: Path = cfg.RECOMENDACOES_YAML, md_path: Path = cfg.RECOMENDACOES_MD) -> list[dict]:
    if not (proc / "kpis_micro_macrofamilia.csv").exists():
        motivo = "faltam as microrregiões do IBGE (V21) e/ou a classificação das macrofamílias (Fase 2)"
        yaml_path.write_text(yaml.safe_dump({"gerado_em": f"{datetime.now():%Y-%m-%d %H:%M}", "status_geral": "pendente",
                                             "motivo": motivo, "recomendacoes": []}, allow_unicode=True, sort_keys=False), encoding="utf-8")
        md_path.write_text(f"# Recomendações candidatas\n\nPendente: {motivo}.\n", encoding="utf-8")
        print("Recomendações pendentes:", motivo)
        return []
    c, ref = candidatas(proc)
    top = [texto(r, ref) for r in escolher_3(c)]
    yaml_path.write_text(yaml.safe_dump({"gerado_em": f"{datetime.now():%Y-%m-%d %H:%M}", "status_geral": "rascunho",
                                         "recomendacoes": top}, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    linhas = [f"# Recomendações candidatas\n\nExecução: {datetime.now():%Y-%m-%d %H:%M} · segmento: {SEGMENTO}\n",
              f"Critério: combinações área × nível × microrregião nos quadrantes \"Expansão sob pressão\" e \"Retenção problemática\", "
              f"com KPI 1 acima da mediana das combinações ({_f(ref['mediana_combinacoes_kpi1'])}%), ordenadas pelo KPI 1. "
              f"Total: {c.height} candidatas.\n",
              "## As 3 sugeridas para o painel (status: rascunho)\n"]
    linhas += [f"{i}. {r['texto']}\n   - Acompanhar: {r['indicador_de_acompanhamento']['kpi']}; linha de base "
               f"{_f(r['indicador_de_acompanhamento']['linha_de_base'])}% (SC: {_f(r['indicador_de_acompanhamento']['referencia_sc'])}%)."
               for i, r in enumerate(top, 1)]
    linhas += ["\n## Todas as candidatas\n", "| Microrregião | Área | Nível | Quadrante | % a pedido | Saldo/10 mil | Desligamentos |",
               "| --- | --- | --- | --- | --- | --- | --- |"]
    linhas += [f"| {r['microrregiao']} | {r['area']} | {r['nivel']} | {r['quadrante']} | {_f(r['kpi1_pct_a_pedido'])} | "
               f"{_f(r['kpi2_saldo_10mil_hab'])} | {_i(r['desligamentos'])} |" for r in c.iter_rows(named=True)]
    md_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"{c.height} candidatas; 3 em {yaml_path.name} como rascunho.")
    return top


if __name__ == "__main__":
    main()
