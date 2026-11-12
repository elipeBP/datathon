"""Pipeline completo, sem LLM por padrão (RODAR_LLM em config.py).

    python run_pipeline.py                  # exige regiões do IBGE já baixadas (ou baixa, se houver internet)
    python run_pipeline.py --sem-regioes    # validação local sem a API do IBGE
"""
import argparse

import config as cfg
from src import base_conhecimento, clean, exportar_web, figuras, ingest, kpis, macrofamilias, recomendacoes, referencias, testes
from src.log import iniciar_log


def main(sem_regioes: bool) -> None:
    iniciar_log()
    ingest.main()
    precisa_baixar = not cfg.MUNICIPIOS_REGIOES_CSV.exists() and not sem_regioes
    referencias.main(offline=not precisa_baixar)
    clean.main(sem_regioes=sem_regioes)
    if cfg.TESTES_MD.exists():
        cfg.TESTES_MD.unlink()
    macrofamilias.main()  # só chama o Gemini se RODAR_LLM = True; senão lê o CSV/cache ou prepara o plano B
    kpis.main()
    testes.main()         # T1, conferência da seção 3, T2–T5
    figuras.main()
    recomendacoes.main()  # rascunho em app/recomendacoes.yaml (a equipe aprova; não sobrescreve se aprovado)
    exportar_web.main()   # web/public/dados.json e GeoJSON para o site React
    base_conhecimento.main()  # web/api/_base.js: base do assistente de dúvidas


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sem-regioes", action="store_true")
    main(p.parse_args().sem_regioes)
