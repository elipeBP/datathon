"""R1, R1b, R2: leitura do CSV bruto do Novo CAGED e gravação de caged_raw.parquet."""
import resource
import sys
import time
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.log import registrar  # noqa: E402


def pico_memoria_mb() -> float:
    """Pico de memória residente do processo (Linux em KB, macOS em bytes)."""
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return pico / 1024 ** 2 if sys.platform == "darwin" else pico / 1024


def ler_caged(caminho: Path = cfg.CAGED_CSV) -> pl.DataFrame:
    """R1: tudo como texto; R1b: nomes ASCII; R2: conversões numéricas."""
    df = pl.read_csv(caminho, separator=";", encoding="utf8", infer_schema_length=0)
    df = df.drop([c for c in cfg.COLUNAS_INDICE if c in df.columns])
    df = df.rename({k: v for k, v in cfg.RENOMEAR_COLUNAS.items() if k in df.columns})

    decimal_virgula = lambda c: pl.col(c).str.replace(",", ".", literal=True).cast(pl.Float64, strict=False)
    df = df.with_columns(
        decimal_virgula("salario").alias("salario"),
        decimal_virgula("horascontratuais").alias("horascontratuais"),
        decimal_virgula("valorsalariofixo").alias("valorsalariofixo"),
        pl.col("idade").cast(pl.Float64, strict=False).cast(pl.Int16, strict=False).alias("idade"),
        pl.col("saldomovimentacao").cast(pl.Int8).alias("saldomovimentacao"),
    )
    return df


def main() -> pl.DataFrame:
    t0 = time.time()
    df = ler_caged()
    cfg.INTERIM.mkdir(parents=True, exist_ok=True)
    df.write_parquet(cfg.CAGED_RAW_PARQUET)
    registrar("Ingestão (R1–R2)", [
        ("Linhas lidas", f"{df.height:,}"),
        ("Colunas", str(df.width)),
        ("Nulos em idade", f"{df['idade'].null_count():,}"),
        ("Salário não numérico", f"{df['salario'].null_count():,}"),
        ("Tempo de leitura", f"{time.time() - t0:.1f} s"),
        ("Pico de memória do processo", f"{pico_memoria_mb():,.0f} MB"),
    ])
    return df


if __name__ == "__main__":
    main()
