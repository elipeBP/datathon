"""Auditoria do repositório antes da entrega (SDD Fase 4).

    git add -A && python src/auditoria.py

Confere, nos arquivos que o Git vai versionar: nada de data/raw/ ou data/interim/, nenhum .env,
nenhum arquivo acima de 50 MB, nenhuma chave de API escrita em texto, e o tamanho de data/processed/.
"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402

LIMITE_MB = 50
PADRAO_CHAVE = re.compile(r"AIza[0-9A-Za-z_\-]{30,}")  # formato das chaves do Google


def arquivos_versionados() -> list[Path]:
    saida = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                           cwd=cfg.ROOT, capture_output=True, text=True, check=True).stdout
    return [cfg.ROOT / l for l in saida.splitlines() if l]


def main() -> bool:
    try:
        arquivos = arquivos_versionados()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Rode dentro de um repositório Git (git init) para auditar.")
        return False
    problemas = []
    for p in arquivos:
        rel = p.relative_to(cfg.ROOT).as_posix()
        if rel.startswith(("data/raw/", "data/interim/")) and not rel.endswith(".gitkeep"):
            problemas.append(f"dado bruto ou intermediário versionado: {rel}")
        if p.name == ".env":
            problemas.append(f".env versionado: {rel}")
        if p.exists() and p.stat().st_size > LIMITE_MB * 1e6:
            problemas.append(f"arquivo acima de {LIMITE_MB} MB: {rel}")
        if p.exists() and p.suffix in {".py", ".md", ".ipynb", ".yaml", ".toml", ".txt", ".csv", ".json"} and p.stat().st_size < 5e6:
            if PADRAO_CHAVE.search(p.read_text(encoding="utf-8", errors="ignore")):
                problemas.append(f"possível chave de API escrita em: {rel}")
    processed = sum(p.stat().st_size for p in cfg.PROCESSED.glob("*") if p.is_file()) / 1e6
    print(f"Arquivos que serão versionados: {len(arquivos)}")
    print(f"data/processed/: {processed:.2f} MB (limite 20 MB)")
    if processed > 20:
        problemas.append("data/processed/ acima de 20 MB")
    for linha in problemas:
        print("PROBLEMA:", linha)
    print("Auditoria:", "OK" if not problemas else f"{len(problemas)} problema(s)")
    return not problemas


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
