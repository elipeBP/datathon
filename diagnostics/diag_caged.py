import sys, time, io
import numpy as np, pandas as pd, openpyxl

caged, dic_path, mun_path = sys.argv[1:4]
t0 = time.time()
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 50)

cat_cols = ["competênciamov","região","uf","município","seção","subclasse","cbo2002ocupação","categoria",
            "graudeinstrução","raçacor","sexo","tipoempregador","tipoestabelecimento","tipomovimentação",
            "tipodedeficiência","indtrabintermitente","indtrabparcial","tamestabjan","indicadoraprendiz",
            "origemdainformação","competênciadec","indicadordeforadoprazo","unidadesaláriocódigo"]
str_cols = ["idade","horascontratuais","salário","valorsaláriofixo"]
dt = {c: "category" for c in cat_cols}; dt.update({c: "str" for c in str_cols}); dt["saldomovimentação"] = "int8"
df = pd.read_csv(caged, sep=";", usecols=cat_cols+str_cols+["saldomovimentação"], dtype=dt, encoding="utf-8")
print(f"[leitura {time.time()-t0:.0f}s] linhas={len(df):,} colunas={df.shape[1]} mem={df.memory_usage(deep=True).sum()/1e9:.2f} GB")

wb = openpyxl.load_workbook(dic_path, data_only=True)
def lab(aba): return {str(r[0]): r[1] for r in wb[aba].iter_rows(min_row=2, values_only=True) if r[0] is not None}
L_tipo, L_grau, L_sec, L_cat = lab("tipomovimentação"), lab("graudeinstrução"), lab("seção"), lab("categoria")

print("\n=== 1. NULOS (vazio/NaN) por coluna ===")
nn = df.isna().sum(); print(nn[nn>0].to_string() if (nn>0).any() else "nenhum nulo")

print("\n=== 2. UF / competência ===")
print("uf:", df["uf"].value_counts().to_dict(), "| região:", df["região"].value_counts().to_dict())
print("competênciamov:", df["competênciamov"].value_counts().sort_index().to_dict())
print("competênciadec != competênciamov:", f"{(df['competênciadec'].astype(str)!=df['competênciamov'].astype(str)).mean()*100:.2f}%")
print("indicadordeforadoprazo:", df["indicadordeforadoprazo"].value_counts().to_dict())
print("origemdainformação:", df["origemdainformação"].value_counts().to_dict())
print("COLUNAS DE EXCLUSÃO no arquivo (indicadordeexclusão/competênciaexc):", [c for c in ["indicadordeexclusão","competênciaexc"] if c in df.columns] or "AUSENTES")

print("\n=== 3. SALDO e TIPO DE MOVIMENTAÇÃO ===")
print("saldomovimentação:", df["saldomovimentação"].value_counts().to_dict(), "| saldo total SC (12 meses):", int(df["saldomovimentação"].sum()))
m = df.groupby("competênciamov", observed=True)["saldomovimentação"].agg(["sum","size"]); m.columns=["saldo","movimentos"]; print(m.to_string())
tp = pd.crosstab(df["tipomovimentação"], df["saldomovimentação"])
tp.index = [f"{i} {L_tipo.get(str(i),'?')}" for i in tp.index]; print(tp.to_string())

print("\n=== 4. MUNICÍPIO ===")
mun = pd.read_csv(mun_path, usecols=[1], header=0, dtype=str, on_bad_lines="skip").iloc[:,0].dropna()
mun6 = set(mun[mun.str.isdigit()].str[:6])
codes = df["município"].astype(str)
print("municípios distintos no CAGED:", codes.nunique(), "| tamanho dos códigos:", codes.str.len().value_counts().to_dict())
print("% movimentos em 429999 (ignorado):", f"{(codes=='429999').mean()*100:.3f}%")
fora = ~codes.isin(mun6) & (codes!='429999'); print("% movimentos com município fora do CSV de municípios:", f"{fora.mean()*100:.3f}%")
print("municípios do CSV sem nenhum movimento:", len(mun6 - set(codes.unique())))

print("\n=== 5. SETOR (seção CNAE) ===")
s = df["seção"].value_counts(); print(pd.DataFrame({"movs":s, "pct":(s/len(df)*100).round(2), "desc":[L_sec.get(i,'?')[:45] for i in s.index]}).to_string())
ind = df["seção"].isin(list("BCDEF")); indC = df["seção"]=="C"
print("movimentos B-F:", f"{ind.sum():,} ({ind.mean()*100:.1f}%) | só C (transformação): {indC.sum():,} ({indC.mean()*100:.1f}%)")

print("\n=== 6. SUBCLASSE / CBO: zeros à esquerda ===")
sub = df["subclasse"].astype(str); print("tamanho subclasse:", sub.str.len().value_counts().to_dict())
print("seção das subclasses com 6 dígitos:", df.loc[sub.str.len()==6, "seção"].value_counts().to_dict())
cbo = df["cbo2002ocupação"].astype(str); print("tamanho CBO:", cbo.str.len().value_counts().to_dict())
cbo_ind = cbo[ind]; print("CBOs distintas total:", cbo.nunique(), "| na indústria B-F:", cbo_ind.nunique(), "| só seção C:", cbo[indC].nunique())
vc = cbo[ind].value_counts(); print("CBOs industriais que cobrem 80% dos movimentos:", int((vc.cumsum()/vc.sum()<=0.8).sum()+1), "| com <30 movimentos:", int((vc<30).sum()))
gg = cbo.str.zfill(6).str[0]; print("grande grupo CBO (indústria B-F):", gg[ind].value_counts().sort_index().to_dict())
div = sub.str.zfill(7).str[:2]; dv = div[indC].value_counts(); print("divisões CNAE na seção C (top 12):", dv.head(12).to_dict(), "| nº divisões:", dv.size)

print("\n=== 7. CATEGORIA / PERFIL ===")
c = df["categoria"].value_counts(); print({f"{k} {L_cat.get(str(k),'?')[:28]}": int(v) for k,v in c.items()})
print("intermitente:", df["indtrabintermitente"].value_counts().to_dict(), "| parcial:", df["indtrabparcial"].value_counts().to_dict(), "| aprendiz:", df["indicadoraprendiz"].value_counts().to_dict())
g = df["graudeinstrução"].value_counts().sort_index(); print({f"{k} {L_grau.get(str(k),'?')[:20]}": int(v) for k,v in g.items()})
print("tamestabjan:", df["tamestabjan"].value_counts().to_dict())

print("\n=== 8. SALÁRIO ===")
sal = pd.to_numeric(df["salário"].str.replace(",",".",regex=False), errors="coerce")
fix = pd.to_numeric(df["valorsaláriofixo"].str.replace(",",".",regex=False), errors="coerce")
print("salário não numérico:", int(sal.isna().sum()), "| zero:", int((sal==0).sum()), "| negativo:", int((sal<0).sum()), "| <500:", int((sal<500).sum()), "| >50.000:", int((sal>50000).sum()))
print(sal.describe(percentiles=[.01,.05,.5,.95,.99]).round(0).to_dict())
u = df["unidadesaláriocódigo"]; print("unidade (1 hora,2 dia,3 sem,4 quinz,5 mês,6 tarefa,7 var):", u.value_counts().to_dict())
for k in ["5","1","2"]:
    mk = u==k
    if mk.any(): print(f"  unidade {k}: salário==valorfixo em {(np.isclose(sal[mk],fix[mk])).mean()*100:.1f}% | mediana salário={sal[mk].median():.0f} | mediana valorfixo={fix[mk].median():.2f}")
idade = pd.to_numeric(df["idade"], errors="coerce"); print("idade: min/mediana/max =", idade.min(), idade.median(), idade.max(), "| <14:", int((idade<14).sum()), "| >80:", int((idade>80).sum()))
hrs = pd.to_numeric(df["horascontratuais"].str.replace(",",".",regex=False), errors="coerce"); print("horas contratuais: mediana", hrs.median(), "| zero:", int((hrs==0).sum()), "| >60:", int((hrs>60).sum()))

print("\n=== 9. SALÁRIO MEDIANO ADMITIDOS x DESLIGADOS (indústria B-F, cat. 101, sem interm./parcial, tipos sem transferência) ===")
tm = df["tipomovimentação"].astype(str)
base = ind & (df["categoria"]=="101") & (df["indtrabintermitente"]=="0") & (df["indtrabparcial"]=="0") & (sal>=1000) & (sal<=30000) & ~tm.isin(["70","80"])
adm = base & (df["saldomovimentação"]==1); des = base & (df["saldomovimentação"]==-1)
print("base elegível:", f"{base.sum():,}", "| admissões:", f"{adm.sum():,}", "| desligamentos:", f"{des.sum():,}", "| mediana adm:", sal[adm].median(), "| mediana desl:", sal[des].median())
print("desligamentos a pedido (40) / total desligamentos na base:", f"{(tm[des]=='40').mean()*100:.1f}%")

print("\n=== 10. DUPLICATAS (colunas de negócio) ===")
print("linhas 100% duplicadas:", f"{df.duplicated().sum():,}")
print(f"\n[total {time.time()-t0:.0f}s]")
