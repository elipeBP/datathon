"""Testes de validação (SDD seção 7) e conferência dos valores de referência (seção 3).

Fase 1 implementa T1 e a conferência. T2–T6 entram na Fase 3.
Escreve reports/testes.md e reports/conferencia_secao3.md.
"""
import sys
from datetime import datetime
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402


def _cabecalho_testes() -> None:
    if not cfg.TESTES_MD.exists():
        cfg.TESTES_MD.write_text(
            "# Testes de validação\n\n| Data | Teste | Grupo | Obtido | Referência | Critério | Resultado |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")


def t1_reconciliacao(df: pl.DataFrame) -> bool:
    """T1: saldo jan–mai/2026 por grupo contra o boletim da FIESC (tolerância 0,5%)."""
    _cabecalho_testes()
    ini, fim = cfg.T1_JANELA
    jan = df.filter(pl.col("competenciamov").is_between(pl.lit(ini), pl.lit(fim)))
    ok_total = True
    linhas = []
    for grupo, (secoes, ref) in cfg.T1_REFERENCIA_FIESC.items():
        obtido = int(jan.filter(pl.col("secao").is_in(secoes))["saldomovimentacao"].sum())
        dif = abs(obtido - ref) / ref
        ok = dif <= cfg.T1_TOLERANCIA
        ok_total &= ok
        linhas.append(f"| {datetime.now():%Y-%m-%d} | T1 | {grupo} | {obtido:,} | {ref:,} | diferença ≤ 0,5% "
                      f"| {'aprovado' if ok else 'REPROVADO'} ({dif:.2%}) |")
    with cfg.TESTES_MD.open("a", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))
    return ok_total


def conferir_secao3(raw: pl.DataFrame, ind: pl.DataFrame) -> list[tuple[str, str, str, bool]]:
    """Reproduz os valores de referência do SDD (seção 3). Tolerância 0 em contagens, ±0,1 p.p. em %."""
    jan = raw.filter(pl.col("competenciamov").is_between(pl.lit(cfg.JANELA_INI), pl.lit(cfg.JANELA_FIM)))
    adm = raw.filter(pl.col("saldomovimentacao") == 1)
    pct = lambda d: 100 * (d.filter(pl.col("saldomovimentacao") == -1)["tipomovimentacao"] == "40").mean()
    med_adm = lambda d: d.filter(pl.col("saldomovimentacao") == 1)["salario"].median()
    C = ind.filter(pl.col("secao") == "C")
    BE = ind.filter(pl.col("secao").is_in(["B", "C", "D", "E"]))
    F = ind.filter(pl.col("secao") == "F")
    Cs = C.filter(pl.col("valido_salario"))
    colunas_raw = raw.columns
    Craw = C.select(colunas_raw)
    cbo_mov = ind.group_by("cbo2002ocupacao").len().sort("len", descending=True)
    n95 = int((cbo_mov["len"].cum_sum() / cbo_mov["len"].sum() < cfg.COBERTURA_CBO).sum() + 1)
    mun_c = C.group_by("municipio").len()

    def linha(nome, obtido, esperado, tol=0.0):
        ok = abs(float(obtido) - float(esperado)) <= tol
        return (nome, f"{obtido:,}" if isinstance(obtido, int) else f"{obtido:,.2f}", f"{esperado:,}", ok)

    return [
        linha("Linhas totais", raw.height, 3397416),
        linha("Linhas fora da janela", raw.height - jan.height, 6128),
        linha("Linhas idênticas (cópias excedentes, arquivo)", raw.height - raw.hash_rows().n_unique(), 97635),
        linha("Fora do prazo (arquivo)", raw.filter(pl.col("indicadordeforadoprazo") == "1").height, 36940),
        linha("Nulos em idade", raw["idade"].null_count(), 2202),
        linha("CBO com 5 dígitos (na janela, antes do zfill)", int((jan["cbo2002ocupacao"].str.len_chars() == 5).sum()), 7),
        linha("Admissões tipo 97", adm.filter(pl.col("tipomovimentacao") == "97").height, 1718686),
        linha("Admissões totais", adm.height, 1719449),
        linha("Salário zero (na janela)", jan.filter(pl.col("salario") == 0).height, 33854),
        linha("Salário máximo", float(raw["salario"].max()), 3471600.00),
        linha("Movimentos C", C.height, 835866),
        linha("Saldo C", int(C["saldomovimentacao"].sum()), 1008),
        linha("% a pedido C", pct(C), 50.9, 0.1),
        linha("Mediana adm. C (sem filtros)", med_adm(C), 2175.80, 0.005),
        linha("Movimentos B–E", BE.height, 867570),
        linha("Saldo B–E", int(BE["saldomovimentacao"].sum()), 1112),
        linha("% a pedido B–E", pct(BE), 50.6, 0.1),
        linha("Movimentos F", F.height, 272063),
        linha("Saldo F", int(F["saldomovimentacao"].sum()), 1533),
        linha("% a pedido F", pct(F), 38.2, 0.1),
        linha("Mediana adm. F (sem filtros)", med_adm(F), 2561.05, 0.005),
        linha("C após R8+R9 (linhas)", Cs.height, 786129),
        linha("C mediana adm. válida", med_adm(Cs), 2200.0, 0.005),
        linha("C mediana desl. válida", Cs.filter(pl.col("saldomovimentacao") == -1)["salario"].median(), 2277.0, 0.5),
        linha("Duplicatas C (cópias excedentes)", Craw.height - Craw.hash_rows().n_unique(), 22211),
        linha("CBOs para 95% de B–F", n95, 354),
        linha("Municípios com ≥300 mov. em C", int((mun_c["len"] >= 300).sum()), 189),
    ]


def registrar_teste(teste: str, grupo: str, obtido: str, referencia: str, criterio: str, ok: bool | None) -> None:
    _cabecalho_testes()
    res = "pendente" if ok is None else ("aprovado" if ok else "REPROVADO")
    linha = f"| {datetime.now():%Y-%m-%d} | {teste} | {grupo} | {obtido} | {referencia} | {criterio} | {res} |"
    with cfg.TESTES_MD.open("a", encoding="utf-8") as f:
        f.write(linha + "\n")
    print(linha)


def _detalhe(nome: str, df: pl.DataFrame) -> None:
    """Tabelas completas dos testes (o SDD pede a distribuição inteira) em reports/testes_detalhe/."""
    pasta = cfg.REPORTS / "testes_detalhe"
    pasta.mkdir(exist_ok=True)
    df.write_csv(pasta / f"{nome}.csv")


def _pct_pedido(df: pl.DataFrame, chaves: list[str]) -> pl.DataFrame:
    return (df.filter(pl.col("saldomovimentacao") == -1).group_by(chaves)
            .agg(pl.len().alias("desl"), (pl.col("tipomovimentacao") == "40").sum().alias("pedido"))
            .with_columns((100 * pl.col("pedido") / pl.col("desl")).alias("pct")))


def t2_composicao(ind: pl.DataFrame) -> bool:
    """T2: a diferença de % a pedido entre divisões é do setor ou da mistura de ocupações?"""
    C = ind.filter(pl.col("secao") == cfg.SECAO_PRINCIPAL)
    # (a) dentro da mesma CBO
    dc = _pct_pedido(C, ["cbo2002ocupacao", "divisao_cnae"]).filter(pl.col("desl") >= cfg.MIN_DESL)
    por_cbo = (dc.group_by("cbo2002ocupacao").agg(pl.len().alias("divisoes"), (pl.col("pct").max() - pl.col("pct").min()).alias("amplitude_pp"))
               .filter(pl.col("divisoes") >= 3).sort("amplitude_pp", descending=True))
    _detalhe("t2a_amplitude_dentro_da_cbo", por_cbo)
    n_a = por_cbo.height
    registrar_teste("T2a", "C, mesma CBO em ≥3 divisões", f"{n_a} CBOs; amplitude mediana {por_cbo['amplitude_pp'].median():.1f} p.p.; "
                    f"{(por_cbo['amplitude_pp'] > cfg.T2_CORTE_PP).sum()} acima de {cfg.T2_CORTE_PP} p.p." if n_a else "0 CBOs",
                    "≥ 10 CBOs", "informativo (reportar se < 10 CBOs)", n_a >= 10)
    # (b) padronização indireta pelas taxas de cada CBO no estado
    maiores = C.group_by("divisao_cnae").len().sort("len", descending=True).head(14)["divisao_cnae"]
    taxa_cbo = _pct_pedido(C, ["cbo2002ocupacao"]).select("cbo2002ocupacao", pl.col("pct").alias("taxa_estado_cbo"))
    taxa_estado = 100 * C.filter((pl.col("saldomovimentacao") == -1) & (pl.col("tipomovimentacao") == "40")).height / C.filter(pl.col("saldomovimentacao") == -1).height
    d = _pct_pedido(C.filter(pl.col("divisao_cnae").is_in(maiores.to_list())), ["divisao_cnae", "cbo2002ocupacao"]).join(taxa_cbo, on="cbo2002ocupacao")
    pad = (d.group_by("divisao_cnae").agg(
        (pl.col("pedido").sum() / pl.col("desl").sum() * 100).alias("observado"),
        ((pl.col("desl") * pl.col("taxa_estado_cbo")).sum() / pl.col("desl").sum()).alias("esperado_pela_mistura"))
        .with_columns((pl.col("observado") - pl.col("esperado_pela_mistura") + taxa_estado).alias("padronizado"),
                      pl.col("divisao_cnae").replace_strict(cfg.GRUPO_POR_DIVISAO, default=None).alias("grupo_setorial"))
        .sort("padronizado", descending=True))
    _detalhe("t2b_padronizacao_14_divisoes", pad)
    amp_obs = pad["observado"].max() - pad["observado"].min()
    amp_pad = pad["padronizado"].max() - pad["padronizado"].min()
    ok = amp_pad > cfg.T2_CORTE_PP
    registrar_teste("T2b", "C, 14 maiores divisões", f"amplitude padronizada {amp_pad:.1f} p.p. (observada {amp_obs:.1f})",
                    f"> {cfg.T2_CORTE_PP} p.p.", "diferença entre maior e menor taxa padronizada", ok)
    print(pad.with_columns(pl.col(pl.Float64).round(1)))
    return ok


def t3_dependencia_cbo(ind: pl.DataFrame, cbo: str = "784205") -> bool:
    """T3: o ranking das 5 piores divisões muda no máximo 1 posição sem a CBO dominante?"""
    from src.kpis import kpis_contagem
    C = ind.filter(pl.col("secao") == cfg.SECAO_PRINCIPAL)
    ok_total = True
    for kpi, desc, nome in [("kpi1_pct_a_pedido", True, "KPI 1"), ("kpi2_saldo_10mil_hab", False, "KPI 2")]:
        rank = lambda df: (kpis_contagem(df, ["divisao_cnae"]).filter(pl.col("kpi1_suficiente") & pl.col("kpi2_suficiente"))
                           .sort(kpi, descending=desc).with_row_index("pos", offset=1).select("divisao_cnae", "pos", kpi))
        com, sem = rank(C), rank(C.filter(pl.col("cbo2002ocupacao") != cbo))
        top = com.head(5).join(sem, on="divisao_cnae", how="left", suffix="_sem").with_columns(
            (pl.col("pos_sem").cast(pl.Int64) - pl.col("pos").cast(pl.Int64)).abs().alias("mudanca"))
        _detalhe(f"t3_{kpi}", top)
        mx = int(top["mudanca"].max())
        ok = mx <= 1
        ok_total &= ok
        registrar_teste("T3", f"{nome}, 5 piores divisões sem CBO {cbo}",
                        "ordem com: " + ", ".join(top["divisao_cnae"]) + f"; maior mudança {mx}", "≤ 1 posição", "ranking estável", ok)
    return ok_total


def t4_estabilidade(ind: pl.DataFrame) -> bool:
    """T4: correlação do % a pedido entre semestres (set–fev × mar–ago) nos recortes acima do volume mínimo."""
    regioes = ind["microrregiao"].null_count() < ind.height
    chaves = ["cod_microrregiao", "grupo_setorial"] if regioes else ["municipio", "grupo_setorial"]
    rotulo = "microrregião × grupo setorial" if regioes else "município × grupo setorial (provisório, sem regiões)"
    C = ind.filter(pl.col("secao") == cfg.SECAO_PRINCIPAL)
    s1 = _pct_pedido(C.filter(pl.col("competenciamov") <= "202602"), chaves).filter(pl.col("desl") >= cfg.MIN_DESL)
    s2 = _pct_pedido(C.filter(pl.col("competenciamov") >= "202603"), chaves).filter(pl.col("desl") >= cfg.MIN_DESL)
    j = s1.join(s2, on=chaves, suffix="_s2")
    _detalhe("t4_semestres", j)
    r = j.select(pl.corr("pct", "pct_s2"))[0, 0]
    ok = r > 0.7
    registrar_teste("T4", f"C, {rotulo}", f"r = {r:.2f} em {j.height} recortes", "> 0,7", "estabilidade entre semestres",
                    ok if regioes else None)
    return ok


def t5_sensibilidade(ind: pl.DataFrame) -> bool | None:
    """T5: KPI 1 do estado e top 5 de microrregiões em C contra B–E."""
    from src.kpis import kpis_contagem
    C = ind.filter(pl.col("secao") == "C")
    BE = ind.filter(pl.col("secao").is_in(["B", "C", "D", "E"]))
    k = lambda d: kpis_contagem(d, [])["kpi1_pct_a_pedido"][0]
    dif = abs(k(C) - k(BE))
    registrar_teste("T5", "KPI 1 do estado, C × B–E", f"{k(C):.2f}% × {k(BE):.2f}% (dif. {dif:.2f} p.p.)", "< 1 p.p.", "", dif < 1)
    if ind["microrregiao"].null_count() == ind.height:
        registrar_teste("T5", "Top 5 microrregiões por KPI 1, C × B–E", "aguardando regiões do IBGE (V21)", "≤ 1 troca", "", None)
        return None
    top = lambda d: (kpis_contagem(d, ["microrregiao"]).filter(pl.col("kpi1_suficiente"))
                     .sort("kpi1_pct_a_pedido", descending=True).head(5)["microrregiao"].to_list())
    a, b = top(C), top(BE)
    trocas = len(set(a) - set(b))
    registrar_teste("T5", "Top 5 microrregiões por KPI 1, C × B–E", f"C: {', '.join(a)} | B–E: {', '.join(b)}; {trocas} troca(s)",
                    "≤ 1 troca", "", trocas <= 1)
    return dif < 1 and trocas <= 1


def t6_macrofamilias(caminho: Path = cfg.REPORTS / "revisao_macrofamilias.csv") -> bool | None:
    """T6 (M3): concordância entre o LLM e os dois revisores humanos na amostra de 30 CBOs."""
    if not caminho.exists():
        registrar_teste("T6", "Amostra M3", "planilha ainda não gerada (Fase 2)", "≥ 85%", "concordância LLM × revisores", None)
        return None
    r = pl.read_csv(caminho, infer_schema_length=0).fill_null("")
    preenchida = r.filter((pl.col("revisor_1_area") != "") & (pl.col("revisor_2_area") != ""))
    if preenchida.height < r.height:
        registrar_teste("T6", "Amostra M3", f"{preenchida.height} de {r.height} linhas preenchidas pelos dois revisores",
                        "≥ 85%", "concordância LLM × revisores", None)
        return None
    acertos = []
    for rev in ("revisor_1", "revisor_2"):
        ok = (pl.col("llm_area") == pl.col(f"{rev}_area")) & (pl.col("llm_nivel") == pl.col(f"{rev}_nivel"))
        acertos.append(100 * r.select(ok.mean())[0, 0])
    entre = 100 * r.select(((pl.col("revisor_1_area") == pl.col("revisor_2_area"))
                            & (pl.col("revisor_1_nivel") == pl.col("revisor_2_nivel"))).mean())[0, 0]
    conc = sum(acertos) / 2
    registrar_teste("T6", "Amostra M3 (área e nível iguais)",
                    f"LLM × revisor 1: {acertos[0]:.0f}% · × revisor 2: {acertos[1]:.0f}% · média {conc:.0f}% · entre revisores {entre:.0f}%",
                    "≥ 85%", "concordância LLM × revisores", conc >= 85)
    return conc >= 85


def main_fase3() -> None:
    ind = pl.read_parquet(cfg.CAGED_IND_PARQUET)
    t2_composicao(ind)
    t3_dependencia_cbo(ind)
    t4_estabilidade(ind)
    t5_sensibilidade(ind)
    t6_macrofamilias()


def main() -> None:
    raw = pl.read_parquet(cfg.CAGED_RAW_PARQUET)
    ind = pl.read_parquet(cfg.CAGED_IND_PARQUET)
    t1 = t1_reconciliacao(ind)
    conf = conferir_secao3(raw, ind)
    md = ["# Conferência dos valores de referência (SDD seção 3)\n", f"Execução: {datetime.now():%Y-%m-%d %H:%M}\n",
          "| Fato | Obtido | SDD | Bateu |", "| --- | --- | --- | --- |"]
    md += [f"| {n} | {o} | {e} | {'sim' if ok else 'NÃO'} |" for n, o, e, ok in conf]
    (cfg.REPORTS / "conferencia_secao3.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\nT1: {'APROVADO' if t1 else 'REPROVADO'} | Conferência: {sum(c[3] for c in conf)}/{len(conf)} bateram")
    del raw
    main_fase3()


if __name__ == "__main__":
    main()
