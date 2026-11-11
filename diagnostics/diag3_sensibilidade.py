import sys
import numpy as np, pandas as pd
caged = sys.argv[1]
cols = ["competênciamov","seção","subclasse","cbo2002ocupação","tipomovimentação","categoria","graudeinstrução","saldomovimentação","salário"]
dt = {c:"category" for c in cols[:-2]}; dt.update({"saldomovimentação":"int8","salário":"str"})
df = pd.read_csv(caged, sep=";", usecols=cols, dtype=dt)
df = df[df["competênciamov"].astype(str).between("202509","202608")].copy()
df["sal"] = pd.to_numeric(df["salário"].str.replace(",",".",regex=False), errors="coerce")
df["adm"] = df["saldomovimentação"]==1; df["tm"] = df["tipomovimentação"].astype(str); df["sec"] = df["seção"].astype(str)
df["cbo"] = df["cbo2002ocupação"].astype(str)
defs = {"C (transformação)":["C"], "B-E (indústria geral, estilo MTE)":list("BCDE"), "F (construção)":["F"], "B-F (com construção)":list("BCDEF")}
rows = []
for nome, secs in defs.items():
    d = df[df["sec"].isin(secs)]; des = d[~d["adm"]]; ad = d[d["adm"]]
    top = d["cbo"].value_counts(); 
    rows.append({"definição":nome, "movs":len(d), "%do total":round(len(d)/len(df)*100,1), "saldo":int(d["saldomovimentação"].sum()),
        "%a_pedido":round((des["tm"]=="40").mean()*100,1), "sal_adm":round(ad["sal"].median()), "sal_des":round(des["sal"].median()),
        "%sup_adm":round(ad["graudeinstrução"].astype(str).isin(["9","10","11","80"]).mean()*100,1),
        "CBOs":top.size, "top1_CBO_%":round(top.iloc[0]/len(d)*100,1)})
print(pd.DataFrame(rows).to_string(index=False))
F = df[df["sec"]=="F"].copy(); F["div"] = F["subclasse"].astype(str).str.zfill(7).str[:2]
g = F.groupby("div").apply(lambda x: pd.Series({"movs":len(x), "saldo":int(x["saldomovimentação"].sum()), "%a_pedido":round((x.loc[~x["adm"],"tm"]=="40").mean()*100,1)}), include_groups=False)
print("\nConstrução por divisão (41 edifícios, 42 infra, 43 serviços especializados):"); print(g.to_string())
B = df[df["sec"].isin(list("BDE"))].copy(); B["div"] = B["subclasse"].astype(str).str.zfill(7).str[:2]
print("\nB, D, E por seção:", B.groupby("sec", observed=True).agg(movs=("adm","size"), saldo=("saldomovimentação","sum")).to_dict("index"))
