"""Seção 5 do SDD: KPIs 1–4, quadrantes e quociente locacional. Saídas em data/processed/.

    python src/kpis.py

Recortes que dependem de microrregião (5.2, 5.4, 5.5) ou de macrofamília (6) só são gerados
quando data/reference/municipios_regioes.csv e macrofamilias.csv existem.
"""
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.log import registrar  # noqa: E402

ADM = pl.col("saldomovimentacao") == 1
DESL = pl.col("saldomovimentacao") == -1
SUP = pl.col("faixa_escolaridade") == "Superior ou mais"


def carregar(caminho: Path = cfg.CAGED_IND_PARQUET) -> pl.DataFrame:
    return pl.read_parquet(caminho)


def tem_regioes(df: pl.DataFrame) -> bool:
    return df["microrregiao"].null_count() < df.height


# ---------------------------------------------------------------- populações por recorte
def populacao(df: pl.DataFrame, chaves: list[str]) -> pl.DataFrame:
    """População do recorte = soma da população (Censo 2022) dos municípios do recorte territorial.
    Recortes não territoriais (setor, macrofamília) usam a população de SC inteira."""
    territoriais = [c for c in chaves if c in ("municipio", "cod_microrregiao", "microrregiao", "cod_mesorregiao", "mesorregiao")]
    mun = df.select("municipio", "pop_censo2022", *[c for c in territoriais if c != "municipio"]).unique("municipio")
    if not territoriais:
        return pl.DataFrame({"pop": [mun["pop_censo2022"].sum()]})
    return mun.group_by(territoriais).agg(pl.col("pop_censo2022").sum().alias("pop"))


# ---------------------------------------------------------------- KPIs 1 e 2 (contagem)
def kpis_contagem(df: pl.DataFrame, chaves: list[str]) -> pl.DataFrame:
    agg = [
        pl.len().alias("movimentos"),
        ADM.sum().alias("admissoes"),
        DESL.sum().alias("desligamentos"),
        pl.col("saldomovimentacao").sum().alias("saldo"),
        (DESL & (pl.col("tipomovimentacao") == "40")).sum().alias("desl_a_pedido"),
    ]
    t = df.group_by(chaves).agg(agg) if chaves else df.select(agg)
    pop = populacao(df, chaves)
    t = t.join(pop, on=[c for c in pop.columns if c != "pop"], how="left") if pop.width > 1 else t.with_columns(pl.lit(pop["pop"][0]).alias("pop"))
    return t.with_columns(
        (100 * pl.col("desl_a_pedido") / pl.col("desligamentos")).alias("kpi1_pct_a_pedido"),
        (pl.col("saldo") / pl.col("pop") * 10_000).alias("kpi2_saldo_10mil_hab"),
        (pl.col("desligamentos") >= cfg.MIN_DESL).alias("kpi1_suficiente"),
        (pl.col("movimentos") >= cfg.MIN_MOV).alias("kpi2_suficiente"),
    )


# ---------------------------------------------------------------- KPIs 3 e 4 (células CBO × microrregião, 5.2)
def _celulas(df: pl.DataFrame, chaves: list[str], kpi: str) -> pl.DataFrame:
    cel = list(dict.fromkeys([*chaves, "cbo2002ocupacao", "cod_microrregiao"]))
    if kpi == "kpi3":
        b = df.filter(pl.col("valido_salario"))
        c = b.group_by(cel).agg(
            pl.len().alias("peso"), ADM.sum().alias("n_adm"), DESL.sum().alias("n_desl"),
            pl.col("salario").filter(ADM).median().alias("med_adm"),
            pl.col("salario").filter(DESL).median().alias("med_desl"),
        ).with_columns((pl.col("med_adm") / pl.col("med_desl")).alias("valor"),
                       ((pl.col("n_adm") >= cfg.MIN_ADM_SAL) & (pl.col("n_desl") >= cfg.MIN_DESL_SAL)).alias("elegivel"))
    else:
        b = df.filter(pl.col("faixa_escolaridade") != "Não identificado")
        c = b.group_by(cel).agg(
            pl.len().alias("peso"), ADM.sum().alias("n_adm"), DESL.sum().alias("n_desl"),
            (SUP & ADM).sum().alias("sup_adm"), (SUP & DESL).sum().alias("sup_desl"),
        ).with_columns((100 * (pl.col("sup_adm") / pl.col("n_adm") - pl.col("sup_desl") / pl.col("n_desl"))).alias("valor"),
                       ((pl.col("n_adm") >= cfg.MIN_ADM_ESC) & (pl.col("n_desl") >= cfg.MIN_DESL_ESC)).alias("elegivel"))
    return c


def kpis_celula(df: pl.DataFrame, chaves: list[str]) -> pl.DataFrame:
    """Média ponderada das células elegíveis do recorte + cobertura (% dos movimentos da base em células elegíveis)."""
    saidas = []
    for kpi, nome in [("kpi3", "kpi3_premio_contratacao"), ("kpi4", "kpi4_descasamento_sup_pp")]:
        c = _celulas(df, chaves, kpi)
        agg = [
            ((pl.col("valor") * pl.col("peso")).filter(pl.col("elegivel")).sum()
             / pl.col("peso").filter(pl.col("elegivel")).sum()).alias(nome),
            (100 * pl.col("peso").filter(pl.col("elegivel")).sum() / pl.col("peso").sum()).alias(f"{kpi}_cobertura_pct"),
            pl.col("elegivel").sum().alias(f"{kpi}_celulas"),
            pl.col("peso").filter(pl.col("elegivel")).sum().alias(f"{kpi}_n"),
        ]
        saidas.append(c.group_by(chaves).agg(agg) if chaves else c.select(agg))
    if not chaves:
        return pl.concat(saidas, how="horizontal")
    return saidas[0].join(saidas[1], on=chaves, how="full", coalesce=True)


def kpis(df: pl.DataFrame, chaves: list[str]) -> pl.DataFrame:
    t = kpis_contagem(df, chaves)
    if tem_regioes(df):
        k = kpis_celula(df, chaves)
        t = t.join(k, on=chaves, how="left") if chaves else pl.concat([t, k], how="horizontal")
    return t.sort(chaves) if chaves else t


# ---------------------------------------------------------------- quadrantes (5.4) e QL (5.5)
def quadrantes(t: pl.DataFrame) -> pl.DataFrame:
    """Unidade = microrregião × grupo setorial; medianas das unidades elegíveis, dentro de cada segmento."""
    el = t.filter(pl.col("kpi1_suficiente") & pl.col("kpi2_suficiente"))
    med = el.group_by("segmento").agg(pl.col("kpi2_saldo_10mil_hab").median().alias("med_x"),
                                      pl.col("kpi1_pct_a_pedido").median().alias("med_y"))
    el = el.join(med, on="segmento")
    acima_x = pl.col("kpi2_saldo_10mil_hab") >= pl.col("med_x")
    acima_y = pl.col("kpi1_pct_a_pedido") >= pl.col("med_y")
    return el.with_columns(
        pl.when(acima_x & acima_y).then(pl.lit("Expansão sob pressão"))
          .when(acima_x).then(pl.lit("Expansão saudável"))
          .when(acima_y).then(pl.lit("Retenção problemática"))
          .otherwise(pl.lit("Estagnado")).alias("quadrante"))


def quociente_locacional(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    mov_sr = df.group_by("cod_microrregiao", "microrregiao", "grupo_setorial").len("mov_sr")
    mov_r = df.group_by("cod_microrregiao").len("mov_r")
    mov_s = df.group_by("grupo_setorial").len("mov_s")
    tot = df.height
    q = (mov_sr.join(mov_r, on="cod_microrregiao").join(mov_s, on="grupo_setorial")
         .with_columns(((pl.col("mov_sr") / pl.col("mov_r")) / (pl.col("mov_s") / tot)).alias("ql")))
    q = q.with_columns(((pl.col("ql") > cfg.QL_CORTE) & (pl.col("mov_sr") >= cfg.QL_MIN_MOV)).alias("polo"))
    sens = {corte: q.filter((pl.col("ql") > corte) & (pl.col("mov_sr") >= cfg.QL_MIN_MOV)).height for corte in (1.1, 1.25, 1.5)}
    return q, sens


# ---------------------------------------------------------------- perfil admitidos × desligados (página Por quê)
def perfil(df: pl.DataFrame, chaves: list[str]) -> tuple[pl.DataFrame, pl.DataFrame]:
    tipo = pl.when(ADM).then(pl.lit("Admitidos")).otherwise(pl.lit("Desligados")).alias("tipo")
    esc = (df.filter(pl.col("faixa_escolaridade") != "Não identificado").with_columns(tipo)
           .group_by([*chaves, "tipo", "faixa_escolaridade"]).len("n")
           .with_columns((100 * pl.col("n") / pl.col("n").sum().over([*chaves, "tipo"])).alias("pct")))
    sal = (df.filter(pl.col("valido_salario")).with_columns(tipo)
           .group_by([*chaves, "tipo"]).agg(pl.col("salario").median().alias("salario_mediano"), pl.len().alias("n")))
    return esc, sal


# ---------------------------------------------------------------- execução
def main(caminho: Path = cfg.CAGED_IND_PARQUET, saida: Path = cfg.PROCESSED) -> dict:
    df = carregar(caminho)
    saida.mkdir(parents=True, exist_ok=True)
    log, geradas = [], {}

    def salvar(nome: str, t: pl.DataFrame) -> None:
        t.write_csv(saida / f"{nome}.csv")
        geradas[nome] = t
        log.append((nome, f"{t.height} linhas"))

    salvar("kpis_segmento", kpis(df, ["segmento"]))
    salvar("kpis_grupo_setorial", kpis(df, ["segmento", "grupo_setorial"]))
    salvar("kpis_divisao", kpis(df, ["segmento", "grupo_setorial", "divisao_cnae"]))
    # T3 reprovou: o painel mostra os recortes com e sem a CBO dominante
    sem = df.filter(pl.col("cbo2002ocupacao") != cfg.CBO_DOMINANTE)
    salvar("kpis_segmento_sem_cbo_dominante", kpis(sem, ["segmento"]))
    salvar("kpis_grupo_setorial_sem_cbo_dominante", kpis(sem, ["segmento", "grupo_setorial"]))
    esc, sal = perfil(df, ["segmento", "grupo_setorial"])
    salvar("perfil_escolaridade_grupo", esc)
    salvar("perfil_salario_grupo", sal)

    if tem_regioes(df):
        micro = ["cod_mesorregiao", "mesorregiao", "cod_microrregiao", "microrregiao"]
        salvar("kpis_microrregiao", kpis(df, ["segmento", *micro]))
        mg = kpis(df, ["segmento", *micro, "grupo_setorial"])
        salvar("kpis_micro_grupo", mg)
        salvar("quadrantes", quadrantes(mg))
        esc, sal = perfil(df, ["segmento", "cod_microrregiao", "microrregiao", "grupo_setorial"])
        salvar("perfil_escolaridade_micro_grupo", esc)
        salvar("perfil_salario_micro_grupo", sal)
        q, sens = quociente_locacional(df)
        salvar("quociente_locacional", q)
        log.append(("Polos (QL > 1,1 / 1,25 / 1,5 com ≥1.000 mov.)", f"{sens[1.1]} / {sens[1.25]} / {sens[1.5]}"))
    else:
        log.append(("Recortes por microrregião, quadrantes e QL", "PENDENTES: falta municipios_regioes.csv (V21)"))

    if cfg.MACROFAMILIAS_CSV.exists():
        mf = pl.read_csv(cfg.MACROFAMILIAS_CSV, infer_schema_length=0).select(
            pl.col("cbo").alias("cbo2002ocupacao"), "area", "nivel")
        dm = df.join(mf, on="cbo2002ocupacao", how="left").filter(pl.col("area") != "Outros")
        salvar("kpis_macrofamilia", kpis(dm, ["segmento", "area", "nivel"]))
        salvar("kpis_grupo_macrofamilia", kpis(dm, ["segmento", "grupo_setorial", "area", "nivel"]))
        if tem_regioes(df):
            micro = ["cod_mesorregiao", "mesorregiao", "cod_microrregiao", "microrregiao"]
            salvar("kpis_micro_macrofamilia", kpis(dm, ["segmento", *micro, "area", "nivel"]))
            salvar("kpis_micro_grupo_macrofamilia", kpis(dm, ["segmento", *micro, "grupo_setorial", "area", "nivel"]))
    else:
        log.append(("Recortes por macrofamília", "PENDENTES: falta macrofamilias.csv (Fase 2)"))

    tamanho = sum(p.stat().st_size for p in saida.glob("*") if p.is_file()) / 1e6
    log.append(("Tamanho de data/processed", f"{tamanho:.2f} MB (limite 20 MB)"))
    if caminho == cfg.CAGED_IND_PARQUET:
        registrar("KPIs (seção 5)", log)
    return geradas


if __name__ == "__main__":
    main()
