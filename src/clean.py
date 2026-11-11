"""R3–R14: filtros, colunas derivadas e junções. Saída: data/interim/caged_ind.parquet.

    python src/clean.py                 # padrão: exige data/reference/municipios_regioes.csv
    python src/clean.py --sem-regioes   # só para validação local sem a API do IBGE
"""
import argparse
import sys
from pathlib import Path

import pandas as pd
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.log import registrar  # noqa: E402
from src.referencias import ler_municipios  # noqa: E402


def padronizar(df: pl.DataFrame) -> pl.DataFrame:
    """R3: zfill e colunas derivadas de código."""
    return df.with_columns(
        pl.col("subclasse").str.zfill(7),
        pl.col("cbo2002ocupacao").str.zfill(6),
    ).with_columns(
        pl.col("subclasse").str.slice(0, 2).alias("divisao_cnae"),
        pl.col("cbo2002ocupacao").str.slice(0, 1).alias("grande_grupo_cbo"),
    )


def filtrar(df: pl.DataFrame, log: list) -> pl.DataFrame:
    """R4–R7, registrando linhas antes e depois de cada regra."""
    n0 = df.height
    df = df.filter(pl.col("competenciamov").is_between(pl.lit(cfg.JANELA_INI), pl.lit(cfg.JANELA_FIM)))
    log.append(("R4 janela " + f"{cfg.JANELA_INI}–{cfg.JANELA_FIM}", f"{n0:,} → {df.height:,} (−{n0 - df.height:,})"))

    n0 = df.height
    df = df.filter(pl.col("secao").is_in(cfg.SECOES))
    log.append(("R5 seções " + "".join(cfg.SECOES), f"{n0:,} → {df.height:,} (−{n0 - df.height:,})"))

    if "indicadordeexclusao" in df.columns:
        n0 = df.height
        df = df.filter(pl.col("indicadordeexclusao") != "1")
        log.append(("R6 exclusões", f"{n0:,} → {df.height:,} (−{n0 - df.height:,})"))
    else:
        log.append(("R6 exclusões", "coluna ausente: nada removido (V2)"))

    dup = df.height - df.hash_rows().n_unique()
    fora = df.filter(pl.col("indicadordeforadoprazo") == "1").height
    log.append(("R7 cópias excedentes de linhas idênticas mantidas (B–F)", f"{dup:,}"))
    log.append(("R7 fora do prazo mantidas", f"{fora:,}"))
    return df


def derivar(df: pl.DataFrame) -> pl.DataFrame:
    """R5 segmento, R8–R9 valido_salario, R10 escolaridade, R14 grupo setorial."""
    return df.with_columns(
        pl.col("secao").replace_strict(cfg.SEGMENTO_POR_SECAO).alias("segmento"),
        pl.col("divisao_cnae").replace_strict(cfg.GRUPO_POR_DIVISAO, default=None).alias("grupo_setorial"),
        pl.col("graudeinstrucao").replace_strict(cfg.FAIXA_ESCOLARIDADE, default=None).alias("faixa_escolaridade"),
        (
            (pl.col("categoria") == "101")
            & (pl.col("indtrabintermitente") == "0")
            & (pl.col("indtrabparcial") == "0")
            & (pl.col("indicadoraprendiz") == "0")
            & pl.col("salario").is_between(cfg.SAL_MIN, cfg.SAL_MAX)
        ).alias("valido_salario"),
    )


def juntar(df: pl.DataFrame, sem_regioes: bool, log: list) -> pl.DataFrame:
    """R11 população, R12 regiões, R12b títulos."""
    mun = pl.from_pandas(ler_municipios()[["cod6", "pop_censo2022"]])
    df = df.join(mun, left_on="municipio", right_on="cod6", how="left")
    log.append(("R11 municípios casados", f"{df['municipio'].n_unique()} de {mun.height}; sem população: {df['pop_censo2022'].null_count():,}"))

    if cfg.MUNICIPIOS_REGIOES_CSV.exists():
        reg = pl.read_csv(cfg.MUNICIPIOS_REGIOES_CSV, infer_schema_length=0).select(
            "cod6", "cod_microrregiao", "microrregiao", "cod_mesorregiao", "mesorregiao")
        df = df.join(reg, left_on="municipio", right_on="cod6", how="left")
        log.append(("R12 regiões", f"{df['microrregiao'].n_unique()} microrregiões; nulos: {df['microrregiao'].null_count():,}"))
    elif sem_regioes:
        df = df.with_columns([pl.lit(None, dtype=pl.Utf8).alias(c) for c in
                              ["cod_microrregiao", "microrregiao", "cod_mesorregiao", "mesorregiao"]])
        log.append(("R12 regiões", "NÃO APLICADO (--sem-regioes). Rodar src/referencias.py com internet."))
    else:
        raise SystemExit("PARAR: falta data/reference/municipios_regioes.csv. Rode `python src/referencias.py`.")

    cbo = pl.read_csv(cfg.CBO_TITULOS_CSV, infer_schema_length=0)
    sub = pl.read_csv(cfg.SUBCLASSE_CSV, infer_schema_length=0)
    df = df.join(cbo, on="cbo2002ocupacao", how="left").join(sub, on="subclasse", how="left")
    log.append(("R12b CBO sem título", f"{df['titulo_cbo'].null_count():,} linhas"))
    log.append(("R12b subclasse sem descrição", f"{df['descricao_subclasse'].null_count():,} linhas"))
    return df


def main(sem_regioes: bool = False) -> pl.DataFrame:
    log: list = []
    df = pl.read_parquet(cfg.CAGED_RAW_PARQUET)
    log.append(("Entrada (caged_raw.parquet)", f"{df.height:,}"))
    df = filtrar(padronizar(df), log)
    df = juntar(derivar(df), sem_regioes, log)
    for c in ["divisao_cnae", "cbo2002ocupacao", "grupo_setorial", "microrregiao"]:
        log.append((f"Nulos em {c}", f"{df[c].null_count():,}"))
    df.write_parquet(cfg.CAGED_IND_PARQUET)
    log.append(("Saída (caged_ind.parquet)", f"{df.height:,} linhas, {df.width} colunas"))
    registrar("Limpeza e junções (R3–R14)", log)
    return df


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sem-regioes", action="store_true")
    main(p.parse_args().sem_regioes)
