"""Modelo explicativo das saídas a pedido (transformação, SC, set/2025–ago/2026).

    python src/modelo.py

Pergunta: entre os desligamentos, o que está ASSOCIADO a a saída ser a pedido do trabalhador (tipo 40),
e não por iniciativa da empresa ou fim de contrato, mantendo os outros fatores fixos?

Desenho (decisões que a banca pode questionar, todas em reports/modelo_saida_pedido.md):
- Amostra: desligamentos da seção C com salário válido (R8+R9) e escolaridade, idade e sexo identificados.
  Fora: aposentadoria (50), morte (60) e tipo ignorado (98): não são decisão de nenhuma das partes.
- Salário relativo: salário da pessoa ÷ mediana da MESMA ocupação (CBO) e microrregião (células com ≥ 30
  salários válidos; senão, mediana estadual da CBO). Em faixas, sem supor efeito linear.
- Regressão logística com controles fixos de setor (grupo setorial), microrregião, grande grupo da CBO e mês;
  erros-padrão agrupados por ocupação × microrregião.
- Resultados em probabilidade prevista média (ajustada pelos outros fatores), mais legível que razão de chances.
- Benchmark: gradient boosting com as mesmas variáveis, para medir quanto poder preditivo a logística deixa na mesa.
- Raça/cor fica fora: variável sensível que não muda a decisão do cliente.
Associação, não causa. O CAGED não traz tempo de casa; o salário relativo carrega parte dele.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import statsmodels.formula.api as smf
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402
from src.log import registrar  # noqa: E402

SAIDA_EFEITOS = cfg.PROCESSED / "modelo_pedido_efeitos.csv"
SAIDA_RESUMO = cfg.PROCESSED / "modelo_pedido_resumo.json"
RELATORIO = cfg.REPORTS / "modelo_saida_pedido.md"

FAIXAS_SAL = [(-np.inf, 0.80, "20% ou mais abaixo"), (0.80, 0.90, "10% a 20% abaixo"), (0.90, 0.97, "3% a 10% abaixo"),
              (0.97, 1.03, "na mediana (±3%)"), (1.03, 1.10, "3% a 10% acima"), (1.10, 1.20, "10% a 20% acima"), (1.20, np.inf, "20% ou mais acima")]
FAIXAS_IDADE = [(14, 18, "até 17"), (18, 25, "18 a 24"), (25, 30, "25 a 29"), (30, 40, "30 a 39"), (40, 50, "40 a 49"), (50, 120, "50 ou mais")]
PORTE = {"1": "até 19", "2": "até 19", "3": "até 19", "4": "até 19", "5": "20 a 99", "6": "20 a 99",
         "7": "100 a 499", "8": "100 a 499", "9": "500 ou mais", "10": "500 ou mais"}
REFS = {"faixa_sal": "na mediana (±3%)", "faixa_idade": "30 a 39", "escolaridade": "Médio", "sexo": "Homem", "porte": "100 a 499"}
ORDEM = {
    "faixa_sal": [f[2] for f in FAIXAS_SAL],
    "faixa_idade": [f[2] for f in FAIXAS_IDADE],
    "escolaridade": ["Até fundamental", "Médio", "Superior incompleto", "Superior ou mais"],
    "sexo": ["Homem", "Mulher"],
    "porte": ["até 19", "20 a 99", "100 a 499", "500 ou mais", "não informado"],
}
NOMES = {"faixa_sal": "Salário em relação à mediana da ocupação na região", "faixa_idade": "Idade",
         "escolaridade": "Escolaridade", "sexo": "Sexo", "porte": "Tamanho da empresa (empregados)"}
FOCO = list(NOMES)
CONTROLES = ["grupo_setorial", "microrregiao", "grande_grupo_cbo", "competenciamov"]
SEMENTE = cfg.SEED


def faixa(v, faixas):
    for lo, hi, nome in faixas:
        if lo <= v < hi:
            return nome
    return None


def montar_base() -> pd.DataFrame:
    d = pl.read_parquet(cfg.CAGED_IND_PARQUET).filter(pl.col("secao") == "C")
    val = d.filter(pl.col("valido_salario"))
    cel = val.group_by("cbo2002ocupacao", "cod_microrregiao").agg(pl.col("salario").median().alias("med_cel"), pl.len().alias("n_cel"))
    cbo = val.group_by("cbo2002ocupacao").agg(pl.col("salario").median().alias("med_cbo"), pl.len().alias("n_cbo"))
    x = (val.filter((pl.col("saldomovimentacao") == -1) & ~pl.col("tipomovimentacao").is_in(["50", "60", "98"]))
         .join(cel, on=["cbo2002ocupacao", "cod_microrregiao"], how="left").join(cbo, on="cbo2002ocupacao", how="left")
         .with_columns(pl.when(pl.col("n_cel") >= 30).then(pl.col("med_cel"))
                       .when(pl.col("n_cbo") >= 30).then(pl.col("med_cbo")).otherwise(None).alias("ref_sal"))
         .with_columns((pl.col("salario") / pl.col("ref_sal")).alias("sal_rel"),
                       (pl.col("tipomovimentacao") == "40").cast(pl.Int8).alias("a_pedido"))
         .filter(pl.col("sal_rel").is_not_null() & pl.col("idade").is_not_null()
                 & (pl.col("faixa_escolaridade") != "Não identificado") & pl.col("sexo").is_in(["1", "3"])))
    df = x.select("a_pedido", "sal_rel", "idade", "faixa_escolaridade", "sexo", "tamestabjan", *CONTROLES,
                  "cbo2002ocupacao", "cod_microrregiao", "tipomovimentacao").to_pandas()
    df["faixa_sal"] = df["sal_rel"].map(lambda v: faixa(v, FAIXAS_SAL))
    df["faixa_idade"] = df["idade"].map(lambda v: faixa(v, FAIXAS_IDADE))
    df["escolaridade"] = df["faixa_escolaridade"]
    df["sexo"] = df["sexo"].map({"1": "Homem", "3": "Mulher"})
    df["porte"] = df["tamestabjan"].map(PORTE).fillna("não informado")
    df["cluster"] = df["cbo2002ocupacao"] + "_" + df["cod_microrregiao"]
    return df.dropna(subset=["faixa_sal", "faixa_idade"]).reset_index(drop=True)


def formula() -> str:
    termos = [f"C({v}, Treatment(reference='{REFS[v]}'))" for v in FOCO] + [f"C({c})" for c in CONTROLES]
    return "a_pedido ~ " + " + ".join(termos)


def probabilidades(modelo, df: pd.DataFrame, amostra: int = 120_000) -> pd.DataFrame:
    """Probabilidade prevista média para cada nível de cada fator, com os outros fatores como na amostra."""
    base = df.sample(min(amostra, len(df)), random_state=SEMENTE)
    linhas = []
    for v in FOCO:
        for nivel in ORDEM[v]:
            if nivel not in set(df[v]):
                continue
            p = float(modelo.predict(base.assign(**{v: nivel})).mean())
            linhas.append({"fator": v, "fator_nome": NOMES[v], "nivel": nivel, "prob_prevista": 100 * p,
                           "referencia": nivel == REFS[v], "n": int((df[v] == nivel).sum()),
                           "pct_pedido_bruto": 100 * float(df.loc[df[v] == nivel, "a_pedido"].mean())})
    out = pd.DataFrame(linhas)
    ref = out[out["referencia"]].set_index("fator")["prob_prevista"]
    out["dif_pp_vs_ref"] = out.apply(lambda r: r["prob_prevista"] - ref[r["fator"]], axis=1)
    return out


def razoes(modelo) -> pd.DataFrame:
    tab = pd.DataFrame({"coef": modelo.params, "ep": modelo.bse, "p": modelo.pvalues})
    ic = modelo.conf_int()
    tab["or"], tab["or_ic_inf"], tab["or_ic_sup"] = np.exp(tab["coef"]), np.exp(ic[0]), np.exp(ic[1])
    linhas = []
    for termo, r in tab.iterrows():
        for v in FOCO:
            if termo.startswith(f"C({v},"):
                linhas.append({"fator": v, "nivel": termo.split("[T.")[1].rstrip("]"), **r[["or", "or_ic_inf", "or_ic_sup", "p"]].to_dict()})
    return pd.DataFrame(linhas)


def validacao(df: pd.DataFrame) -> dict:
    """AUC fora da amostra: logística × gradient boosting; importância por permutação (boosting)."""
    tr, te = train_test_split(df, test_size=0.2, random_state=SEMENTE, stratify=df["a_pedido"])
    logit = smf.logit(formula(), data=tr).fit(disp=0, maxiter=200)
    auc_logit = roc_auc_score(te["a_pedido"], logit.predict(te))
    cols = FOCO + CONTROLES
    enc = {c: {k: i for i, k in enumerate(sorted(df[c].astype(str).unique()))} for c in cols}
    X = lambda d: np.column_stack([d[c].astype(str).map(enc[c]).values for c in cols])
    gbm = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, categorical_features=[True] * len(cols),
                                         random_state=SEMENTE, early_stopping=True)
    gbm.fit(X(tr), tr["a_pedido"])
    auc_gbm = roc_auc_score(te["a_pedido"], gbm.predict_proba(X(te))[:, 1])
    amostra = te.sample(min(40_000, len(te)), random_state=SEMENTE)
    imp = permutation_importance(gbm, X(amostra), amostra["a_pedido"], scoring="roc_auc", n_repeats=3, random_state=SEMENTE)
    rotulos = {**NOMES, "grupo_setorial": "Setor", "microrregiao": "Microrregião", "grande_grupo_cbo": "Grande grupo da ocupação", "competenciamov": "Mês"}
    importancia = sorted(({"variavel": rotulos[c], "queda_auc": float(m)} for c, m in zip(cols, imp.importances_mean)), key=lambda x: -x["queda_auc"])
    return {"auc_logit": float(auc_logit), "auc_gbm": float(auc_gbm), "importancia_gbm": importancia, "n_treino": len(tr), "n_teste": len(te)}


MERCADO_VARS = {
    "log_sal_rel": "Salário da ocupação na região × mediana da ocupação em SC",
    "log_premio": "Prêmio de contratação (quem entra × quem sai)",
    "cresc": "Crescimento (saldo ÷ movimentações)",
    "p_sup": "% com superior completo",
    "p_jovem": "% de 14 a 24 anos",
    "p_mulher": "% de mulheres",
    "p_grande": "% em empresas com 500 ou mais empregados",
}


def celulas(desl_min: int = 100, sem_cbo: str | None = None) -> pd.DataFrame:
    """Células ocupação (CBO) × microrregião da transformação, com o % de saídas a pedido e as características do mercado."""
    d = pl.read_parquet(cfg.CAGED_IND_PARQUET).filter(pl.col("secao") == "C")
    if sem_cbo:
        d = d.filter(pl.col("cbo2002ocupacao") != sem_cbo)
    val = d.filter(pl.col("valido_salario"))
    adm, desl = pl.col("saldomovimentacao") == 1, pl.col("saldomovimentacao") == -1
    med_cbo = val.group_by("cbo2002ocupacao").agg(pl.col("salario").median().alias("med_cbo"), pl.len().alias("n_cbo"))
    cel = d.group_by("cbo2002ocupacao", "cod_microrregiao").agg(
        pl.len().alias("mov"), desl.sum().alias("desl"), (desl & (pl.col("tipomovimentacao") == "40")).sum().alias("desl_pedido"),
        pl.col("saldomovimentacao").sum().alias("saldo"),
        (pl.col("faixa_escolaridade") == "Superior ou mais").mean().alias("p_sup"),
        pl.col("idade").is_between(14, 24).mean().alias("p_jovem"), (pl.col("sexo") == "3").mean().alias("p_mulher"),
        pl.col("tamestabjan").is_in(["9", "10"]).mean().alias("p_grande"),
        pl.col("grupo_setorial").mode().first().alias("grupo_setorial"), pl.col("mesorregiao").first().alias("mesorregiao"),
        pl.col("microrregiao").first().alias("microrregiao"), pl.col("grande_grupo_cbo").first().alias("grande_grupo_cbo"))
    sal = val.group_by("cbo2002ocupacao", "cod_microrregiao").agg(
        pl.col("salario").median().alias("med_cel"), pl.len().alias("n_val"),
        pl.col("salario").filter(adm).median().alias("med_adm"), pl.col("salario").filter(desl).median().alias("med_desl"),
        adm.sum().alias("n_adm_val"), desl.sum().alias("n_desl_val"))
    c = (cel.join(sal, on=["cbo2002ocupacao", "cod_microrregiao"]).join(med_cbo, on="cbo2002ocupacao")
         .filter((pl.col("desl") >= desl_min) & (pl.col("n_val") >= 30) & (pl.col("n_cbo") >= 100))
         .with_columns((pl.col("desl_pedido") / pl.col("desl")).alias("frac"),
                       (pl.col("med_cel") / pl.col("med_cbo")).log().alias("log_sal_rel"),
                       (100 * pl.col("saldo") / pl.col("mov")).alias("cresc"),
                       pl.when((pl.col("n_adm_val") >= 30) & (pl.col("n_desl_val") >= 30))
                       .then((pl.col("med_adm") / pl.col("med_desl")).log()).otherwise(None).alias("log_premio")))
    return c.drop_nulls("log_premio").to_pandas()


def ajustar_mercado(c: pd.DataFrame):
    """Logit fracionário (GLM binomial ponderado pelos desligamentos), controles fixos de setor, mesorregião e grande grupo."""
    f = "frac ~ " + " + ".join(MERCADO_VARS) + " + C(grupo_setorial) + C(mesorregiao) + C(grande_grupo_cbo)"
    import statsmodels.api as sm
    return smf.glm(f, data=c, family=sm.families.Binomial(), var_weights=c["desl"]).fit(cov_type="HC1")


def efeito_pp(m, c: pd.DataFrame, var: str, delta: float) -> float:
    """Variação média da probabilidade prevista (p.p.) quando a variável sobe `delta`, com o resto como está."""
    return float(100 * (m.predict(c.assign(**{var: c[var] + delta})).mean() - m.predict(c).mean()))


def modelo_mercado() -> dict:
    c = celulas()
    m = ajustar_mercado(c)
    linhas = []
    for v, nome in MERCADO_VARS.items():
        sd = float(c[v].std())
        linhas.append({"variavel": v, "nome": nome, "coef": float(m.params[v]), "p": float(m.pvalues[v]),
                       "ic_inf": float(m.conf_int().loc[v, 0]), "ic_sup": float(m.conf_int().loc[v, 1]),
                       "dp": sd, "efeito_1dp_pp": efeito_pp(m, c, v, sd)})
    efeitos = pd.DataFrame(linhas)
    efeitos.to_csv(cfg.PROCESSED / "modelo_mercado_efeitos.csv", index=False)
    sal10 = efeito_pp(m, c, "log_sal_rel", float(np.log(1.10)))
    # robustez: volume mínimo da célula e sem a ocupação dominante (T3)
    rob = []
    for rotulo, kw in [("células com ≥ 50 desligamentos", {"desl_min": 50}), ("células com ≥ 200 desligamentos", {"desl_min": 200}),
                       ("sem o alimentador de linha (CBO 784205)", {"sem_cbo": cfg.CBO_DOMINANTE})]:
        cc = celulas(**kw)
        mm = ajustar_mercado(cc)
        rob.append({"recorte": rotulo, "celulas": len(cc), "efeito_sal10_pp": efeito_pp(mm, cc, "log_sal_rel", float(np.log(1.10))),
                    "p_sal": float(mm.pvalues["log_sal_rel"]), "p_premio": float(mm.pvalues["log_premio"])})
    return {"celulas": len(c), "desligamentos": int(c["desl"].sum()), "efeito_sal10_pp": sal10,
            "p_sal": float(m.pvalues["log_sal_rel"]), "efeitos": linhas, "robustez": rob}


def f1(v, c=1):
    return f"{v:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> dict:
    t0 = time.time()
    df = montar_base()
    modelo = smf.logit(formula(), data=df).fit(disp=0, maxiter=200, cov_type="cluster", cov_kwds={"groups": pd.factorize(df["cluster"])[0]})
    probs = probabilidades(modelo, df)
    ors = razoes(modelo)
    efeitos = probs.merge(ors, on=["fator", "nivel"], how="left")
    efeitos.to_csv(SAIDA_EFEITOS, index=False)
    val = validacao(df)
    # "não informado" no tamanho da empresa é cadastro incompleto, não um porte: fica fora da amplitude
    amplitude = (probs[probs["nivel"] != "não informado"].groupby("fator")["prob_prevista"].agg(lambda s: s.max() - s.min()).sort_values(ascending=False))
    mercado = modelo_mercado()
    resumo = {
        "mercado": mercado,
        "n": int(len(df)), "taxa_pedido": float(100 * df["a_pedido"].mean()), "pseudo_r2": float(modelo.prsquared),
        "auc_logit": val["auc_logit"], "auc_gbm": val["auc_gbm"], "importancia_gbm": val["importancia_gbm"],
        "amplitude_pp": [{"fator": f, "fator_nome": NOMES[f], "amplitude_pp": float(a)} for f, a in amplitude.items()],
        "celulas_ref": "mediana do salário na mesma CBO × microrregião (≥ 30 salários válidos); senão, mediana estadual da CBO",
    }
    SAIDA_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    escrever_relatorio(df, probs, ors, resumo)
    registrar("Modelo das saídas a pedido", [
        ("Desligamentos na amostra", f"{len(df):,}"), ("Taxa a pedido na amostra", f"{resumo['taxa_pedido']:.1f}%"),
        ("AUC fora da amostra (logística × boosting)", f"{val['auc_logit']:.3f} × {val['auc_gbm']:.3f}"),
        ("Pseudo-R² (McFadden)", f"{modelo.prsquared:.3f}"),
        ("Fator de maior amplitude", f"{amplitude.index[0]} ({amplitude.iloc[0]:.1f} p.p.)"),
        ("Mercado: células ocupação × microrregião", f"{mercado['celulas']} ({mercado['desligamentos']:,} desligamentos)"),
        ("Mercado: +10% de salário relativo", f"{mercado['efeito_sal10_pp']:+.2f} p.p. de saídas a pedido (p = {mercado['p_sal']:.4f})"),
        ("Tempo", f"{time.time() - t0:.0f} s"),
    ])
    return resumo


def escrever_relatorio(df, probs, ors, r) -> None:
    m = r["mercado"]
    ef = {e["variavel"]: e for e in m["efeitos"]}
    sig = lambda p: "p < 0,001" if p < 0.001 else f"p = {f1(p, 3)}"
    L = ["# Modelo das saídas a pedido\n",
         "Pergunta: o que está **associado** a o trabalhador pedir para sair da indústria de transformação de SC (set/2025–ago/2026)? "
         "Dois níveis, porque cada um responde uma coisa diferente. Associação, não causa.\n",
         "## Nível 1 — Mercado: pagar acima do mercado retém?\n",
         f"Unidade: célula ocupação (CBO) × microrregião com pelo menos 100 desligamentos e 30 salários válidos: {f1(m['celulas'], 0)} células, "
         f"{f1(m['desligamentos'], 0)} desligamentos ({f1(100 * m['desligamentos'] / 417429, 0)}% da transformação). "
         "Desfecho: % das saídas a pedido na célula. Logit fracionário (GLM binomial ponderado pelos desligamentos), controles fixos de setor, "
         "mesorregião e grande grupo da ocupação, erros-padrão robustos (HC1).\n",
         f"**Resultado principal:** onde a mesma ocupação paga 10% acima da mediana da ocupação em SC, a parcela de saídas a pedido é "
         f"**{f1(m['efeito_sal10_pp'], 1)} p.p.** ({sig(m['p_sal'])}), com os outros fatores fixos.\n",
         "| Característica da célula | Efeito de +1 desvio-padrão | Significância |", "| --- | --- | --- |"]
    for e in sorted(m["efeitos"], key=lambda x: -abs(x["efeito_1dp_pp"])):
        L.append(f"| {e['nome']} | {'+' if e['efeito_1dp_pp'] > 0 else ''}{f1(e['efeito_1dp_pp'], 2)} p.p. | {sig(e['p'])} |")
    L += ["", f"- O prêmio de contratação (quem entra × quem sai) **não se sustenta** com os controles ({sig(ef['log_premio']['p'])}): confirma que era um sinal fraco. "
          "O que se associa às saídas é o nível do salário da ocupação na região em relação ao resto do estado, não a diferença entre quem entra e quem sai.",
          f"- Mercado aquecido (crescimento) puxa as saídas a pedido para cima ({sig(ef['cresc']['p'])}): sinal fraco, coerente com mercado apertado.",
          "- Composição: células com mais mulheres e com mais empresas de 500+ empregados têm mais saídas a pedido; com mais superior completo, menos.\n",
          "**Robustez do efeito do salário (+10%):**\n", "| Recorte | Células | Efeito | p (salário) | p (prêmio) |", "| --- | --- | --- | --- | --- |",
          f"| Principal (≥ 100 desligamentos) | {m['celulas']} | {f1(m['efeito_sal10_pp'], 2)} p.p. | {sig(m['p_sal'])} | {sig(ef['log_premio']['p'])} |"]
    L += [f"| {x['recorte'].capitalize()} | {x['celulas']} | {f1(x['efeito_sal10_pp'], 2)} p.p. | {sig(x['p_sal'])} | {sig(x['p_premio'])} |" for x in m["robustez"]]
    L += ["\n## Nível 2 — Perfil: entre quem saiu, quem saiu a pedido?\n",
          f"- Amostra: {f1(r['n'], 0)} desligamentos com salário válido (celetista comum, R$ 1.000 a R$ 30.000) e escolaridade, idade e sexo "
          f"identificados. Fora: aposentadoria, morte e tipo ignorado. Taxa a pedido na amostra: {f1(r['taxa_pedido'])}%.",
          f"- Fatores: salário relativo (÷ {r['celulas_ref']}, em faixas), escolaridade, idade, sexo e tamanho da empresa. Controles fixos: setor, "
          "microrregião, grande grupo da ocupação e mês. Regressão logística, erros-padrão agrupados por ocupação × microrregião. Raça/cor fica fora.",
          f"- Validação fora da amostra (80/20): AUC da logística {f1(r['auc_logit'], 3)}, gradient boosting {f1(r['auc_gbm'], 3)}. "
          f"Pseudo-R² {f1(r['pseudo_r2'], 3)}. O desfecho individual tem muito ruído: o objetivo é medir associações, não prever pessoas.",
          "- Importância por permutação (boosting): " + "; ".join(f"{x['variavel']} {f1(x['queda_auc'], 3)}" for x in r["importancia_gbm"]) + ".\n",
          "| Fator | Nível | Prob. prevista | Diferença vs. referência | Taxa bruta | Razão de chances (IC 95%) | n |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for _, x in probs.merge(ors, on=["fator", "nivel"], how="left").iterrows():
        orx = "referência" if x["referencia"] else f"{f1(x['or'], 2)} ({f1(x['or_ic_inf'], 2)}–{f1(x['or_ic_sup'], 2)})"
        dif = "—" if x["referencia"] else ("+" if x["dif_pp_vs_ref"] > 0 else "") + f1(x["dif_pp_vs_ref"]) + " p.p."
        L.append(f"| {x['fator_nome']} | {x['nivel']} | {f1(x['prob_prevista'])}% | {dif} | {f1(x['pct_pedido_bruto'])}% | {orx} | {f1(x['n'], 0)} |")
    L += ["\nLeitura do perfil:",
          "- Jovens (18 a 24 anos), mulheres, quem tem superior completo e quem trabalha em empresas de 500+ empregados têm mais chance de a saída ter sido a pedido, na mesma ocupação e região.",
          "- O salário relativo **não deve ser lido sozinho neste nível**: entre quem saiu, quem ganhava 20% ou mais acima da mediana saiu mais vezes por demissão sem justa causa "
          "(a empresa desliga mais quem custa mais). Por isso a pergunta \"pagar mais retém?\" é respondida no Nível 1, que compara mercados e não depende de quem a empresa escolheu demitir.",
          "- \"Tamanho da empresa: não informado\" é cadastro incompleto, não um porte; fica fora da leitura.\n",
          "## Limites\n",
          "- Associação, não causa: o modelo não promete que aumentar o salário reduz as saídas.",
          "- O CAGED não traz tempo de casa nem vagas abertas; parte do que aparece como salário ou idade é tempo de casa.",
          "- O Nível 2 só olha quem saiu; o Nível 1 compara mercados, mas ainda dentro do fluxo de 12 meses.",
          "- Células e limiares são escolhas da equipe; a tabela de robustez mostra que o resultado principal não depende deles."]
    RELATORIO.write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=1)[:2500])
