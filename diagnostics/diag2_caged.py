import sys
import numpy as np, pandas as pd, openpyxl
caged, dic_path, mun_path = sys.argv[1:4]
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 50)
cat = ["competênciamov","município","seção","subclasse","cbo2002ocupação","categoria","graudeinstrução","tipomovimentação","tamestabjan"]
dt = {c:"category" for c in cat}; dt.update({"salário":"str","saldomovimentação":"int8"})
df = pd.read_csv(caged, sep=";", usecols=cat+["salário","saldomovimentação"], dtype=dt)
df["sal"] = pd.to_numeric(df["salário"].str.replace(",",".",regex=False), errors="coerce"); df.drop(columns="salário", inplace=True)
win = df["competênciamov"].astype(str).between("202509","202608"); df = df[win].copy()
print("linhas na janela 202509-202608:", f"{len(df):,}", "| saldo:", int(df['saldomovimentação'].sum()))
wb = openpyxl.load_workbook(dic_path, data_only=True)
cbo_name = {str(r[0]).zfill(6): r[1] for r in wb["cbo2002ocupação"].iter_rows(min_row=2, values_only=True) if r[0] is not None}
DIV = {"10":"Alimentos","11":"Bebidas","13":"Têxteis","14":"Confecção","15":"Couro/calçados","16":"Madeira","17":"Celulose/papel","18":"Impressão","20":"Químicos","22":"Borracha/plástico","23":"Minerais não-metál.","24":"Metalurgia","25":"Prod. de metal","26":"Eletrônicos/informát.","27":"Mat. elétrico","28":"Máquinas/equip.","29":"Veículos","30":"Outros transp.","31":"Móveis","32":"Prod. diversos","33":"Manut./instalação"}
df["cbo"] = df["cbo2002ocupação"].astype(str).str.zfill(6); df["div"] = df["subclasse"].astype(str).str.zfill(7).str[:2]
df["mun"] = df["município"].astype(str); df["adm"] = df["saldomovimentação"]==1; df["tm"] = df["tipomovimentação"].astype(str)
C = df[df["seção"]=="C"]; BF = df[df["seção"].isin(list("BCDEF"))]

print("\n=== A. COBERTURA DE CBOs (nº de CBOs p/ cobrir X% dos movimentos) ===")
for nome, d in [("indústria B-F", BF), ("só seção C", C)]:
    vc = d["cbo"].value_counts(); cs = vc.cumsum()/vc.sum()
    print(nome, {f"{int(p*100)}%": int((cs<p).sum()+1) for p in [.5,.8,.9,.95,.99]}, "| total:", len(vc), "| >=100 movs:", int((vc>=100).sum()), "| >=30 movs:", int((vc>=30).sum()))
vc = C["cbo"].value_counts()
for n in [150,200,300,400]: print(f"  top {n} CBOs (seção C) cobrem {vc.head(n).sum()/vc.sum()*100:.1f}%")
print("\nTop 15 CBOs da seção C:")
g = C.groupby("cbo", observed=True).agg(movs=("adm","size"), saldo=("saldomovimentação","sum"), sal_med=("sal","median")).sort_values("movs", ascending=False).head(15)
g["nome"] = [cbo_name.get(i,"?")[:42] for i in g.index]; print(g.to_string())

print("\n=== B. DIVISÕES CNAE da seção C ===")
def divstats(d):
    des = d[~d["adm"]]; ad = d[d["adm"]]
    return pd.Series({"movs":len(d), "saldo":int(d["saldomovimentação"].sum()),
        "%pedido": (des["tm"]=="40").mean()*100 if len(des) else np.nan,
        "sal_adm": ad["sal"].median(), "sal_des": des["sal"].median(),
        "%sup_adm": ad["graudeinstrução"].astype(str).isin(["9","10","11","80"]).mean()*100,
        "%sup_des": des["graudeinstrução"].astype(str).isin(["9","10","11","80"]).mean()*100,
        "%temp_adm": (ad["categoria"].astype(str)=="106").mean()*100})
r = C.groupby("div").apply(divstats, include_groups=False)
r["premio"] = (r["sal_adm"]/r["sal_des"]).round(3); r["nome"] = [DIV.get(i,"?") for i in r.index]
print(r.sort_values("movs", ascending=False).round({"movs":0,"saldo":0,"%pedido":1,"sal_adm":0,"sal_des":0,"%sup_adm":1,"%sup_des":1,"%temp_adm":2,"premio":3}).head(14).to_string())

print("\n=== C. MENSAL — seção C (saldo) ===")
print(C.groupby("competênciamov", observed=True)["saldomovimentação"].sum().to_dict())

print("\n=== D. MUNICÍPIOS (seção C), saldo por 10 mil hab. (Censo 2022) ===")
mun = pd.read_csv(mun_path, header=0, dtype=str, on_bad_lines="skip")
mun = mun[mun.iloc[:,1].str.isdigit().fillna(False)]
pop = pd.DataFrame({"mun": mun.iloc[:,1].str[:6], "nome": mun.iloc[:,0], "pop": pd.to_numeric(mun.iloc[:,5])}).set_index("mun")
m = C.groupby("mun", observed=True).agg(movs=("adm","size"), saldo=("saldomovimentação","sum")).join(pop, how="left")
m["saldo10k"] = m["saldo"]/m["pop"]*10000
print("municípios com movimento em C:", len(m), "| >=1000 movs:", int((m.movs>=1000).sum()), "| >=300:", int((m.movs>=300).sum()), "| >=100:", int((m.movs>=100).sum()), "| <30:", int((m.movs<30).sum()))
print("share dos 10 maiores municípios no volume industrial:", f"{m.movs.sort_values(ascending=False).head(10).sum()/m.movs.sum()*100:.1f}%")
print("Top 8 por volume:"); print(m.sort_values("movs", ascending=False).head(8)[["nome","movs","saldo","saldo10k"]].round(1).to_string())
big = m[m.movs>=1000].sort_values("saldo10k")
print("Maiores quedas (>=1000 movs):"); print(big.head(5)[["nome","movs","saldo","saldo10k"]].round(1).to_string())
print("Maiores altas (>=1000 movs):"); print(big.tail(5)[["nome","movs","saldo","saldo10k"]].round(1).to_string())

print("\n=== E. ESTABELECIMENTOS NOVOS (tamestabjan=1 'Zero') entre admissões ===")
ad = C[C["adm"]]; print("seção C: % das admissões em estab. com 0 empregados em jan:", f"{(ad['tamestabjan'].astype(str)=='1').mean()*100:.1f}%", "| ignorado (99):", f"{(ad['tamestabjan'].astype(str)=='99').mean()*100:.1f}%")
