"""Gráficos compartilhados pelo painel e pela exportação de PNG (SDD 8.2).

Regras: uma cor de destaque só para o que pede atenção, o resto em cinza; título com a conclusão,
gerado a partir dos números; recorte abaixo do volume mínimo em cinza claro, nunca em ranking.
"""
import json
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import polars as pl

DESTAQUE = "#D1495B"   # contraste adequado nos temas claro e escuro
NEUTRO = "#8C939D"
COMPARACAO = "#4C78A8"  # segunda série de comparação, sem significado de alerta
INSUFICIENTE = "#C9CDD2"
CORES_QUADRANTE = {
    "Expansão sob pressão": DESTAQUE,
    "Retenção problemática": "#E8A33D",
    "Expansão saudável": NEUTRO,
    "Estagnado": INSUFICIENTE,
}


def _layout(fig: go.Figure, titulo: str, subtitulo: str = "", altura: int = 460) -> go.Figure:
    texto = f"<b>{titulo}</b>" + (f"<br><span style='font-size:13px'>{subtitulo}</span>" if subtitulo else "")
    fig.update_layout(title=dict(text=texto, x=0, xanchor="left"), height=altura,
                      margin=dict(l=10, r=30, t=80, b=40), font=dict(size=13),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(140,147,157,0.25)")
    fig.update_yaxes(showgrid=False)
    return fig


def fmt_int(v: int) -> str:
    return f"{int(v):,}".replace(",", ".")


def fmt_pct(v: float) -> str:
    return f"{v:.1f}".replace(".", ",") + "%"


def barras_pedido_grupo(t: pl.DataFrame, referencia: float, segmento: str) -> go.Figure:
    """KPI 1 por grupo setorial, ordenado, com a linha do segmento em SC."""
    d = t.filter(pl.col("segmento") == segmento).sort("kpi1_pct_a_pedido")
    cor = [INSUFICIENTE if not s else (DESTAQUE if v > referencia else NEUTRO)
           for v, s in zip(d["kpi1_pct_a_pedido"], d["kpi1_suficiente"])]
    fig = go.Figure(go.Bar(
        x=d["kpi1_pct_a_pedido"], y=d["grupo_setorial"], orientation="h", marker_color=cor,
        text=[f"{fmt_pct(v)}  (n={fmt_int(n)})" for v, n in zip(d["kpi1_pct_a_pedido"], d["desligamentos"])],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>%{x:.1f}% dos desligamentos a pedido<extra></extra>"))
    fig.add_vline(x=referencia, line_dash="dash", line_color=NEUTRO, layer="below",
                  annotation_text=f"{segmento} em SC: {fmt_pct(referencia)}", annotation_position="top")
    topo = d.filter(pl.col("kpi1_suficiente")).sort("kpi1_pct_a_pedido", descending=True).row(0, named=True)
    fig.update_xaxes(title="% dos desligamentos que foram a pedido do trabalhador", range=[0, max(d["kpi1_pct_a_pedido"]) * 1.25])
    return _layout(fig, f"{topo['grupo_setorial']} perde {fmt_pct(topo['kpi1_pct_a_pedido'])} dos que saem por pedido",
                   f"{segmento} · Novo CAGED set/2025–ago/2026 · em vermelho: acima da média do segmento")


def barras_com_sem(com: pl.DataFrame, sem: pl.DataFrame, segmento: str, cbo_rotulo: str) -> go.Figure:
    """T3: KPI 1 por grupo setorial com e sem a CBO dominante."""
    a = com.filter(pl.col("segmento") == segmento).select("grupo_setorial", pl.col("kpi1_pct_a_pedido").alias("com"))
    b = sem.filter(pl.col("segmento") == segmento).select("grupo_setorial", pl.col("kpi1_pct_a_pedido").alias("sem"))
    d = a.join(b, on="grupo_setorial").sort("com")
    fig = go.Figure([
        go.Bar(name="Todas as ocupações", x=d["com"], y=d["grupo_setorial"], orientation="h", marker_color=NEUTRO),
        go.Bar(name=f"Sem {cbo_rotulo}", x=d["sem"], y=d["grupo_setorial"], orientation="h", marker_color=COMPARACAO),
    ])
    maior = d.with_columns((pl.col("com") - pl.col("sem")).alias("dif")).sort("dif", descending=True).row(0, named=True)
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=-0.15))
    fig.update_xaxes(title="% dos desligamentos a pedido")
    return _layout(fig, f"Sem o {cbo_rotulo.lower()}, {maior['grupo_setorial']} cai de {fmt_pct(maior['com'])} para {fmt_pct(maior['sem'])}",
                   "Teste T3: quanto do resultado depende de uma única ocupação", 520)


def dispersao_quadrantes(q: pl.DataFrame, segmento: str) -> go.Figure:
    d = q.filter(pl.col("segmento") == segmento)
    fig = px.scatter(d.to_pandas(), x="kpi2_saldo_10mil_hab", y="kpi1_pct_a_pedido", size="movimentos",
                     color="quadrante", color_discrete_map=CORES_QUADRANTE, size_max=38,
                     hover_name="microrregiao", hover_data={"grupo_setorial": True, "mesorregiao": True,
                                                            "movimentos": ":,", "quadrante": False})
    fig.add_vline(x=d["med_x"][0], line_dash="dot", line_color=NEUTRO)
    fig.add_hline(y=d["med_y"][0], line_dash="dot", line_color=NEUTRO)
    fig.update_xaxes(title="Saldo por 10 mil habitantes (12 meses)")
    fig.update_yaxes(title="% dos desligamentos a pedido")
    n = d.filter(pl.col("quadrante") == "Expansão sob pressão").height
    r = d.filter(pl.col("quadrante") == "Retenção problemática").height
    return _layout(fig, f"{n} polos crescem e perdem gente; {r} não crescem e perdem gente",
                   f"Microrregião × grupo setorial · {segmento} · linhas na mediana das unidades com volume suficiente", 560)


def mapa_microrregioes(t: pl.DataFrame, geojson_path: Path, segmento: str) -> go.Figure:
    geo = json.loads(Path(geojson_path).read_text(encoding="utf-8"))
    d = t.filter(pl.col("segmento") == segmento).with_columns(
        pl.when(pl.col("kpi1_suficiente")).then(pl.col("kpi1_pct_a_pedido")).otherwise(None).alias("kpi1_mapa"))
    fig = px.choropleth(d.to_pandas(), geojson=geo, locations="cod_microrregiao", featureidkey="properties.codarea",
                        color="kpi1_mapa", color_continuous_scale=[[0, "#F2F3F5"], [1, DESTAQUE]],
                        hover_name="microrregiao", hover_data={"kpi1_pct_a_pedido": ":.1f", "movimentos": ":,", "cod_microrregiao": False},
                        labels={"kpi1_mapa": "% a pedido"})
    fig.update_geos(fitbounds="locations", visible=False)
    topo = d.filter(pl.col("kpi1_suficiente")).sort("kpi1_pct_a_pedido", descending=True).row(0, named=True)
    return _layout(fig, f"{topo['microrregiao']} lidera as saídas a pedido: {fmt_pct(topo['kpi1_pct_a_pedido'])}",
                   f"{segmento} · microrregiões com volume insuficiente ficam em branco", 520)


def barras_kpi_macrofamilia(t: pl.DataFrame, referencia: float, recorte: str) -> go.Figure:
    """KPI 1 por macrofamília (área × nível) no recorte, com a linha de SC."""
    d = t.with_columns((pl.col("area") + " · " + pl.col("nivel")).alias("macro")).sort("kpi1_pct_a_pedido")
    cor = [INSUFICIENTE if not s else (DESTAQUE if v > referencia else NEUTRO)
           for v, s in zip(d["kpi1_pct_a_pedido"], d["kpi1_suficiente"])]
    fig = go.Figure(go.Bar(x=d["kpi1_pct_a_pedido"], y=d["macro"], orientation="h", marker_color=cor,
                           text=[f"{fmt_pct(v)} (n={fmt_int(n)})" if s else "amostra insuficiente"
                                 for v, n, s in zip(d["kpi1_pct_a_pedido"], d["desligamentos"], d["kpi1_suficiente"])],
                           textposition="outside", cliponaxis=False))
    fig.add_vline(x=referencia, line_dash="dash", line_color=NEUTRO, layer="below",
                  annotation_text=f"SC: {fmt_pct(referencia)}", annotation_position="top")
    ok = d.filter(pl.col("kpi1_suficiente"))
    titulo = (f"{ok.sort('kpi1_pct_a_pedido', descending=True)['macro'][0]} lidera as saídas a pedido em {recorte}"
              if ok.height else f"Nenhuma macrofamília com volume suficiente em {recorte}")
    fig.update_xaxes(title="% dos desligamentos a pedido", range=[0, max(d["kpi1_pct_a_pedido"].fill_null(0)) * 1.3 + 1])
    return _layout(fig, titulo, "Macrofamília = área × nível de formação · cinza claro: amostra insuficiente",
                   max(380, 34 * d.height + 140))


def perfil_escolaridade(esc: pl.DataFrame, recorte: str) -> go.Figure:
    ordem = ["Até fundamental", "Médio", "Superior incompleto", "Superior ou mais"]
    d = esc.group_by("tipo", "faixa_escolaridade").agg(pl.col("n").sum()).with_columns(
        (100 * pl.col("n") / pl.col("n").sum().over("tipo")).alias("pct"))
    fig = go.Figure([go.Bar(name=tipo, x=ordem,
                            y=[d.filter((pl.col("tipo") == tipo) & (pl.col("faixa_escolaridade") == f))["pct"].sum() for f in ordem],
                            marker_color=NEUTRO if tipo == "Desligados" else COMPARACAO,
                            text=[fmt_pct(d.filter((pl.col("tipo") == tipo) & (pl.col("faixa_escolaridade") == f))["pct"].sum()) for f in ordem],
                            textposition="outside") for tipo in ["Admitidos", "Desligados"]])
    sup = {tp: d.filter((pl.col("tipo") == tp) & (pl.col("faixa_escolaridade") == "Superior ou mais"))["pct"].sum() for tp in ["Admitidos", "Desligados"]}
    dif = sup["Admitidos"] - sup["Desligados"]
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(title="% do grupo")
    verbo = "menos" if dif < 0 else "mais"
    return _layout(fig, f"Quem entra tem {fmt_pct(abs(dif)).replace('%', '')} p.p. {verbo} superior que quem sai",
                   f"{recorte} · escolaridade de admitidos e desligados (sem 'não identificado')", 420)


def salario_adm_desl(sal: pl.DataFrame, rotulo: str) -> go.Figure:
    d = sal.pivot(on="tipo", index=rotulo, values="salario_mediano").sort("Admitidos")
    fig = go.Figure([go.Bar(name=tp, y=d[rotulo], x=d[tp], orientation="h",
                            marker_color=NEUTRO if tp == "Desligados" else COMPARACAO) for tp in ["Admitidos", "Desligados"]])
    d = d.with_columns((pl.col("Admitidos") / pl.col("Desligados")).alias("r"))
    pior = d.sort("r").row(0, named=True)
    fig.update_layout(barmode="group", legend=dict(orientation="h", y=-0.15))
    fig.update_xaxes(title="Salário mediano (R$)")
    return _layout(fig, f"Em {pior[rotulo]}, quem entra ganha {fmt_pct(100 * (1 - pior['r']))} menos que quem sai",
                   "Salário mediano de admissão × desligamento · só celetistas comuns, R$ 1.000 a R$ 30.000", max(380, 40 * d.height + 140))
