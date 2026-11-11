"""Registro das etapas em reports/log_pipeline.md (cada filtro: linhas antes e depois)."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402


def iniciar_log() -> None:
    cfg.REPORTS.mkdir(parents=True, exist_ok=True)
    cfg.LOG_PIPELINE.write_text(
        f"# Log do pipeline\n\nExecução: {datetime.now():%Y-%m-%d %H:%M}\n", encoding="utf-8"
    )


def registrar(etapa: str, linhas: list[tuple[str, str]]) -> None:
    """Acrescenta uma tabela de duas colunas ao log e imprime no console."""
    if not cfg.LOG_PIPELINE.exists():
        iniciar_log()
    bloco = [f"\n## {etapa}\n", "| Item | Valor |", "| --- | --- |"]
    bloco += [f"| {k} | {v} |" for k, v in linhas]
    texto = "\n".join(bloco) + "\n"
    with cfg.LOG_PIPELINE.open("a", encoding="utf-8") as f:
        f.write(texto)
    print(texto)
