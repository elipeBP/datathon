"""Exporta os gráficos principais em PNG em reports/figures/ (SDD 8.4), para os slides.

    python src/figuras.py

Se o kaleido pedir o Chrome: `plotly_get_chrome` (vem com o kaleido 1.x); se ainda falhar, `pip install kaleido==0.2.1`.
"""
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src import graficos as g  # noqa: E402


def main() -> list[Path]:
    cfg.FIGURES.mkdir(parents=True, exist_ok=True)
    seg = pl.read_csv(cfg.PROCESSED / "kpis_segmento.csv")
    grp = pl.read_csv(cfg.PROCESSED / "kpis_grupo_setorial.csv")
    grp_sem = pl.read_csv(cfg.PROCESSED / "kpis_grupo_setorial_sem_cbo_dominante.csv")
    segmento = "Transformação"
    ref = seg.filter(pl.col("segmento") == segmento)["kpi1_pct_a_pedido"][0]
    figs = {
        "01_pedido_por_grupo_setorial": g.barras_pedido_grupo(grp, ref, segmento),
        "02_t3_com_sem_alimentador": g.barras_com_sem(grp, grp_sem, segmento, "Alimentador de linha"),
    }
    if (cfg.PROCESSED / "quadrantes.csv").exists():
        figs["03_quadrantes"] = g.dispersao_quadrantes(pl.read_csv(cfg.PROCESSED / "quadrantes.csv", infer_schema_length=0)
                                                       .with_columns(pl.col(c).cast(pl.Float64) for c in
                                                                     ["kpi1_pct_a_pedido", "kpi2_saldo_10mil_hab", "med_x", "med_y"])
                                                       .with_columns(pl.col("movimentos").cast(pl.Int64)), segmento)
    if (cfg.PROCESSED / "kpis_microrregiao.csv").exists() and cfg.GEOJSON_MICRO.exists():
        mic = pl.read_csv(cfg.PROCESSED / "kpis_microrregiao.csv", schema_overrides={"cod_microrregiao": pl.Utf8})
        figs["04_mapa_microrregioes"] = g.mapa_microrregioes(mic, cfg.GEOJSON_MICRO, segmento)
        figs["05_mapa_saldo_microrregioes"] = g.mapa_microrregioes(mic, cfg.GEOJSON_MICRO, segmento, "kpi2")
    saidas = []
    for nome, fig in figs.items():
        p = cfg.FIGURES / f"{nome}.png"
        fig.write_image(p, width=1200, height=fig.layout.height or 500, scale=2)
        saidas.append(p)
        print("PNG:", p.relative_to(cfg.ROOT))
    return saidas


if __name__ == "__main__":
    main()
