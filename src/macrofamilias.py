"""Seção 6 do SDD: macrofamílias de CBO com Gemini (lista fechada, temperatura 0, revisão humana).

    python src/macrofamilias.py              # usa o cache / plano B; só chama a API se RODAR_LLM = True
    python src/macrofamilias.py --llm        # força as chamadas ao Gemini (precisa de GEMINI_API_KEY no .env)
    python src/macrofamilias.py --plano-b data/interim/resposta_plano_b.json   # importa a resposta colada do chat

Saídas: data/reference/macrofamilias.csv, reports/revisao_macrofamilias.csv (M3),
reports/macrofamilias_validacao.md (M1, M2, distribuição), data/interim/cbos_para_classificar.csv (plano B).
"""
import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path

import polars as pl
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config as cfg  # noqa: E402


# ---------------------------------------------------------------- taxonomia fechada (6.2)
class Area(str, Enum):
    ALIMENTOS = "Alimentos e bebidas"
    TEXTIL = "Têxtil, confecção e calçados"
    METALMECANICA = "Metalmecânica e soldagem"
    MANUTENCAO = "Manutenção industrial"
    ELETRO = "Eletroeletrônica e automação"
    MADEIRA = "Madeira e móveis"
    PLASTICO = "Plástico, borracha e química"
    CERAMICA = "Cerâmica, vidro e minerais"
    LOGISTICA = "Logística e movimentação"
    LINHA = "Operação de linha e montagem"
    CONSTRUCAO = "Construção"
    QUALIDADE = "Qualidade e controle"
    GESTAO = "Gestão, administrativo e comercial"
    ENGENHARIA = "Engenharia e P&D"
    APOIO = "Serviços de apoio"


class Nivel(str, Enum):
    QUALIF_CURTA = "Qualificação até 200h"
    QUALIF_LONGA = "Qualificação acima de 200h"
    TECNICO = "Técnico"
    SUPERIOR = "Superior"


class Confianca(str, Enum):
    ALTA = "alta"
    MEDIA = "media"
    BAIXA = "baixa"


class Classificacao(BaseModel):
    cbo: str
    area: Area
    nivel: Nivel
    confianca: Confianca
    justificativa: str = Field(description="Até 15 palavras")


LISTA = TypeAdapter(list[Classificacao])

DEFINICOES_AREA = {
    Area.ALIMENTOS: "Ocupações específicas do processamento de alimentos e bebidas: abate, desossa, laticínios, panificação industrial",
    Area.TEXTIL: "Fiação, tecelagem, corte, costura, acabamento, calçados",
    Area.METALMECANICA: "Usinagem, caldeiraria, soldagem, fundição, estamparia, montagem mecânica especializada",
    Area.MANUTENCAO: "Mecânicos, eletricistas e eletromecânicos de manutenção, lubrificadores",
    Area.ELETRO: "Montagem e operação eletroeletrônica, instrumentação, automação, bobinagem",
    Area.MADEIRA: "Serraria, marcenaria, montagem de móveis",
    Area.PLASTICO: "Operação de injetoras e extrusoras, processos químicos",
    Area.CERAMICA: "Fabricação de cerâmica, porcelanato, louça, vidro, cimento e artefatos de minerais não metálicos",
    Area.LOGISTICA: "Motoristas, operadores de empilhadeira, almoxarifes, conferentes, expedição",
    Area.LINHA: "Funções genéricas de produção: alimentadores de linha, operadores de máquina não específicos, montadores, embaladores",
    Area.CONSTRUCAO: "Pedreiros, serventes de obra, carpinteiros de obra, armadores, instaladores prediais",
    Area.QUALIDADE: "Inspeção, controle de qualidade, laboratório, segurança do trabalho",
    Area.GESTAO: "Gerentes, supervisores administrativos, escritório, RH, finanças, compras, vendas, representantes",
    Area.ENGENHARIA: "Engenheiros, projetistas, desenvolvedores, químicos, pesquisadores",
    Area.APOIO: "Limpeza, portaria, vigilância, cozinha, conservação",
}
DEFINICOES_NIVEL = {
    Nivel.QUALIF_CURTA: "Aprende no posto ou em curso curto (ex.: alimentador de linha, embalador, servente)",
    Nivel.QUALIF_LONGA: "Ofício que exige curso de qualificação longo ou prática prolongada (ex.: soldador, eletricista de manutenção, operador de CNC)",
    Nivel.TECNICO: "Curso técnico de nível médio (ex.: técnico em eletrotécnica, técnico de segurança do trabalho)",
    Nivel.SUPERIOR: "Graduação (ex.: engenheiros, analistas, contadores)",
}
GRANDES_GRUPOS = {
    "0": "Forças armadas, policiais e bombeiros militares",
    "1": "Membros superiores do poder público, dirigentes de organizações e gerentes",
    "2": "Profissionais das ciências e das artes",
    "3": "Técnicos de nível médio",
    "4": "Trabalhadores de serviços administrativos",
    "5": "Trabalhadores dos serviços, vendedores do comércio",
    "6": "Trabalhadores agropecuários, florestais e da pesca",
    "7": "Trabalhadores da produção de bens e serviços industriais (sistemas discretos)",
    "8": "Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)",
    "9": "Trabalhadores em serviços de reparação e manutenção",
}
# Exemplos resolvidos (6.4, regra 3): 784205 fixado no SDD; 351605 e 252405 = CBOs mais frequentes
# e de leitura inequívoca dos grandes grupos 3 e 2 em B–F (3.406 e 2.390 movimentos).
EXEMPLOS = [
    {"cbo": "784205", "titulo": "Alimentador de Linha de Produção", "area": Area.LINHA, "nivel": Nivel.QUALIF_CURTA,
     "confianca": "alta", "justificativa": "Função genérica de produção, aprendida no posto"},
    {"cbo": "351605", "titulo": "Técnico em Segurança no Trabalho", "area": Area.QUALIDADE, "nivel": Nivel.TECNICO,
     "confianca": "alta", "justificativa": "Segurança do trabalho exige curso técnico de nível médio"},
    {"cbo": "252405", "titulo": "Analista de Recursos Humanos", "area": Area.GESTAO, "nivel": Nivel.SUPERIOR,
     "confianca": "alta", "justificativa": "Função administrativa de RH que exige graduação"},
]
NIVEL_ESPERADO_M2 = {"2": {Nivel.SUPERIOR.value}, "3": {Nivel.TECNICO.value},
                     **{g: {Nivel.QUALIF_CURTA.value, Nivel.QUALIF_LONGA.value} for g in ["7", "8", "9"]}}
SEM_TITULO = "(sem título no dicionário)"


# ---------------------------------------------------------------- universo de CBOs (6.1)
def universo_cbos() -> pl.DataFrame:
    """Todas as CBOs de B–F, com movimentos, título e onde mais aparecem. Marca o escopo (95% dos movimentos)."""
    d = pl.read_parquet(cfg.CAGED_IND_PARQUET,
                        columns=["cbo2002ocupacao", "grande_grupo_cbo", "titulo_cbo", "secao", "grupo_setorial"])
    moda = lambda col: (d.group_by("cbo2002ocupacao", col).len().sort("len", descending=True)
                        .unique("cbo2002ocupacao", keep="first").select("cbo2002ocupacao", col))
    u = (d.group_by("cbo2002ocupacao").agg(pl.len().alias("movimentos"),
                                           pl.first("grande_grupo_cbo"), pl.first("titulo_cbo"))
         .join(moda("secao"), on="cbo2002ocupacao").join(moda("grupo_setorial"), on="cbo2002ocupacao")
         .sort(["movimentos", "cbo2002ocupacao"], descending=[True, False])
         .rename({"cbo2002ocupacao": "cbo"}))
    acum = u["movimentos"].cum_sum() / u["movimentos"].sum()
    n_escopo = int((acum < cfg.COBERTURA_CBO).sum()) + 1
    return u.with_columns(
        pl.Series("no_escopo", [i < n_escopo for i in range(u.height)]),
        pl.col("titulo_cbo").is_null().alias("sem_titulo"),
        pl.col("titulo_cbo").fill_null(SEM_TITULO),
    )


# ---------------------------------------------------------------- prompt (6.4)
def texto_prompt() -> str:
    areas = "\n".join(f"- {a.value}: {DEFINICOES_AREA[a]}" for a in Area)
    niveis = "\n".join(f"- {n.value}: {DEFINICOES_NIVEL[n]}" for n in Nivel)
    exemplos = "\n".join(
        f'- CBO {e["cbo"]} "{e["titulo"]}" → {{"cbo": "{e["cbo"]}", "area": "{e["area"].value}", '
        f'"nivel": "{e["nivel"].value}", "confianca": "{e["confianca"]}", "justificativa": "{e["justificativa"]}"}}'
        for e in EXEMPLOS)
    return f"""Você é um especialista em classificação de ocupações (CBO 2002) e em formação profissional industrial
no Brasil, no formato do Mapa do Trabalho Industrial (SENAI/CNI).

Classifique cada ocupação da lista em UMA área e UM nível de formação, usando SOMENTE os valores abaixo.
Nunca crie categorias, nunca altere nem invente códigos de CBO. Devolva exatamente as CBOs recebidas, uma vez cada.

ÁREAS:
{areas}

Regra de área: se a ocupação é específica de um ramo (ex.: magarefe, costureira industrial), use a área do ramo;
se é genérica de produção (ex.: alimentador de linha, embalador), use "Operação de linha e montagem".

NÍVEIS DE FORMAÇÃO:
{niveis}

CONFIANÇA: "alta", "media" ou "baixa". Em caso de dúvida, escolha a opção mais próxima e marque a confiança como baixa.
Se o título vier como "{SEM_TITULO}", classifique só pelo código e pelo contexto e marque a confiança como baixa.

JUSTIFICATIVA: até 15 palavras, em português.

EXEMPLOS RESOLVIDOS:
{exemplos}

Para cada ocupação você recebe: código CBO, título oficial, grande grupo da CBO, seção CNAE e grupo setorial
onde ela mais aparece em Santa Catarina, e o número de movimentações (admissões + desligamentos) em 12 meses.
Responda apenas com uma lista JSON de objetos com as chaves cbo, area, nivel, confianca, justificativa.
"""


def linhas_entrada(lote: pl.DataFrame) -> str:
    return "\n".join(
        f'{r["cbo"]} | {r["titulo_cbo"]} | grande grupo {r["grande_grupo_cbo"]} ({GRANDES_GRUPOS.get(r["grande_grupo_cbo"], "?")}) '
        f'| seção {r["secao"]} | {r["grupo_setorial"]} | {r["movimentos"]:,} movimentos'
        for r in lote.iter_rows(named=True))


def registrar_prompt(modelo: str, caminho_resposta: str) -> None:
    cfg.ROOT.joinpath("prompts").mkdir(exist_ok=True)
    (cfg.ROOT / "prompts" / "macrofamilias_v1.md").write_text(
        f"# Prompt de macrofamílias — v1\n\n"
        f"- Versão: v1\n- Modelo: `{modelo}`\n- Data: {datetime.now():%Y-%m-%d %H:%M}\n"
        f"- Caminho: {caminho_resposta}\n- Temperatura: 0 · lotes de {cfg.LOTE_LLM} CBOs · saída JSON com enums (6.3)\n\n"
        f"## Instrução de sistema\n\n```text\n{texto_prompt()}```\n\n"
        f"## Formato da mensagem do usuário (uma linha por CBO)\n\n"
        f"```text\nCBO | título | grande grupo (nome) | seção CNAE | grupo setorial | movimentos\n```\n",
        encoding="utf-8")


# ---------------------------------------------------------------- chamada ao Gemini (6.3)
def _validar_lote(texto: str, esperadas: set[str]) -> list[Classificacao]:
    itens = LISTA.validate_json(texto)
    recebidas = [i.cbo.strip().zfill(6) for i in itens]
    if set(recebidas) != esperadas or len(recebidas) != len(esperadas):
        raise ValueError(f"conjunto diferente: faltam {sorted(esperadas - set(recebidas))[:5]}, "
                         f"sobram {sorted(set(recebidas) - esperadas)[:5]}")
    for i in itens:
        i.cbo = i.cbo.strip().zfill(6)
    return itens


def classificar_com_gemini(escopo: pl.DataFrame) -> tuple[list[Classificacao], list[int]]:
    """Lotes de LOTE_LLM com cache, conferência do conjunto e backoff em 429/503."""
    from dotenv import load_dotenv
    from google import genai
    from google.genai import errors, types

    load_dotenv(cfg.ROOT / ".env")
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("PARAR: crie o arquivo .env com GEMINI_API_KEY (veja .env.example). Nunca cole a chave no chat.")
    client = genai.Client()  # lê GEMINI_API_KEY do ambiente
    config = types.GenerateContentConfig(
        system_instruction=texto_prompt(), temperature=0,
        response_mime_type="application/json", response_schema=list[Classificacao])

    cfg.LLM_CACHE.mkdir(parents=True, exist_ok=True)
    resultado, manuais = [], []
    for n, inicio in enumerate(range(0, escopo.height, cfg.LOTE_LLM), start=1):
        lote = escopo.slice(inicio, cfg.LOTE_LLM)
        esperadas = set(lote["cbo"])
        cache = cfg.LLM_CACHE / f"lote_{n:02d}.json"
        if cache.exists():
            try:
                resultado += _validar_lote(json.loads(cache.read_text(encoding="utf-8"))["texto"], esperadas)
                continue
            except (ValidationError, ValueError, KeyError):
                cache.unlink()
        for tentativa in range(1, cfg.LLM_MAX_TENTATIVAS + 1):
            try:
                resp = _chamar_com_espera(client, lote, config, n)
                itens = _validar_lote(resp.text, esperadas)
                cache.write_text(json.dumps({"modelo": cfg.GEMINI_MODEL, "data": datetime.now().isoformat(),
                                             "texto": resp.text}, ensure_ascii=False), encoding="utf-8")
                resultado += itens
                print(f"lote {n:02d}: {len(itens)} CBOs ok")
                break
            except errors.APIError as e:
                if e.code in (429, 503) and tentativa < cfg.LLM_MAX_TENTATIVAS:
                    espera = 2 ** tentativa * 5
                    print(f"lote {n:02d}: erro {e.code}, nova tentativa em {espera}s")
                    time.sleep(espera)
                    continue
                if e.code == 429:
                    raise SystemExit(f"PARAR: limite do plano gratuito em {cfg.GEMINI_MODEL}. "
                                     f"Espere o dia virar ou troque para GEMINI_MODEL_RESERVA em config.py.")
                raise
            except (ValidationError, ValueError) as e:
                print(f"lote {n:02d}, tentativa {tentativa}: resposta inválida ({e})")
                if tentativa == cfg.LLM_MAX_TENTATIVAS:
                    manuais.append(n)
                    print(f"lote {n:02d}: marcado para classificação manual")
    return resultado, manuais


def _chamar_com_espera(client, lote, config, n: int):
    """503 (pico de demanda) é passageiro: espera mais, sem gastar as tentativas de validação do lote.
    Mantém o mesmo modelo em todos os lotes, para a classificação ficar consistente."""
    from google.genai import errors
    for i in range(cfg.LLM_ESPERAS_503 + 1):
        try:
            return client.models.generate_content(model=cfg.GEMINI_MODEL, contents=linhas_entrada(lote), config=config)
        except errors.APIError as e:
            if e.code != 503 or i == cfg.LLM_ESPERAS_503:
                raise
            espera = min(15 * 2 ** i, 120)
            print(f"lote {n:02d}: 503 (alta demanda), esperando {espera}s ({i + 1}/{cfg.LLM_ESPERAS_503})")
            time.sleep(espera)


# ---------------------------------------------------------------- plano B (6.6)
def exportar_plano_b(escopo: pl.DataFrame) -> None:
    cfg.INTERIM.mkdir(parents=True, exist_ok=True)
    escopo.select("cbo", "titulo_cbo", "grande_grupo_cbo", "secao", "grupo_setorial", "movimentos") \
          .write_csv(cfg.INTERIM / "cbos_para_classificar.csv")
    lotes = [linhas_entrada(escopo.slice(i, cfg.LOTE_LLM)) for i in range(0, escopo.height, cfg.LOTE_LLM)]
    corpo = "\n\n".join(f"### Lote {n:02d}\n\n```text\n{t}\n```" for n, t in enumerate(lotes, start=1))
    (cfg.ROOT / "prompts" / "plano_b_chat.md").write_text(
        "# Plano B — classificar no Google AI Studio (ou outro chat)\n\n"
        "1. Cole a instrução abaixo como instrução de sistema, com temperatura 0.\n"
        "2. Envie um lote por vez e cole cada resposta JSON, em ordem, numa única lista em "
        "`data/interim/resposta_plano_b.json`.\n"
        "3. Rode `python src/macrofamilias.py --plano-b data/interim/resposta_plano_b.json`. "
        "As mesmas validações do caminho com API são aplicadas.\n\n"
        f"## Instrução\n\n```text\n{texto_prompt()}```\n\n## Lotes\n\n{corpo}\n", encoding="utf-8")


def importar_plano_b(caminho: Path, escopo: pl.DataFrame) -> list[Classificacao]:
    return _validar_lote(Path(caminho).read_text(encoding="utf-8"), set(escopo["cbo"]))


# ---------------------------------------------------------------- validações (6.5) e saída
def montar_tabela(u: pl.DataFrame, itens: list[Classificacao], origem: str) -> pl.DataFrame:
    cls = pl.DataFrame([{"cbo": i.cbo, "area": i.area.value, "nivel": i.nivel.value,
                         "confianca": i.confianca.value, "justificativa": i.justificativa} for i in itens])
    t = u.join(cls, on="cbo", how="left").with_columns(
        pl.when(pl.col("area").is_not_null()).then(pl.lit(origem)).otherwise(None).alias("origem"))
    # V20: CBO sem título → confiança baixa forçada
    t = t.with_columns(pl.when(pl.col("sem_titulo") & pl.col("area").is_not_null())
                       .then(pl.lit(cfg.CBOS_SEM_TITULO_CONFIANCA)).otherwise(pl.col("confianca")).alias("confianca"))
    # M4: herança pela família (4 dígitos), moda ponderada por movimentos
    t = t.with_columns(pl.col("cbo").str.slice(0, 4).alias("familia"))
    base = t.filter(pl.col("area").is_not_null())
    heranca = (base.group_by("familia", "area", "nivel").agg(pl.col("movimentos").sum())
               .sort(["familia", "movimentos"], descending=[False, True]).unique("familia", keep="first")
               .select("familia", pl.col("area").alias("area_h"), pl.col("nivel").alias("nivel_h")))
    t = t.join(heranca, on="familia", how="left").with_columns(
        pl.when(pl.col("area").is_null() & pl.col("area_h").is_not_null()).then(pl.lit("heranca"))
          .when(pl.col("area").is_null()).then(pl.lit("outros")).otherwise(pl.col("origem")).alias("origem"),
    ).with_columns(
        pl.when(pl.col("origem") == "heranca").then(pl.col("area_h"))
          .when(pl.col("origem") == "outros").then(pl.lit("Outros")).otherwise(pl.col("area")).alias("area"),
        pl.when(pl.col("origem") == "heranca").then(pl.col("nivel_h"))
          .when(pl.col("origem") == "outros").then(pl.lit("Outros")).otherwise(pl.col("nivel")).alias("nivel"),
        pl.when(pl.col("origem") == "heranca").then(pl.lit("herdada da família ") + pl.col("familia"))
          .otherwise(pl.col("justificativa")).alias("justificativa"),
    )
    # M1 e M2 → lista de revisão
    t = t.with_columns(
        (pl.col("confianca") == "baixa").fill_null(False).alias("m1_confianca_baixa"),
        pl.struct("grande_grupo_cbo", "nivel", "origem").map_elements(
            lambda r: r["origem"] == "llm" and r["grande_grupo_cbo"] in NIVEL_ESPERADO_M2
            and r["nivel"] not in NIVEL_ESPERADO_M2[r["grande_grupo_cbo"]], return_dtype=pl.Boolean
        ).alias("m2_divergente"),
        pl.lit(False).alias("revisado"),
    )
    return t


def salvar(t: pl.DataFrame) -> None:
    t.select("cbo", "titulo_cbo", "area", "nivel", "confianca", "justificativa", "origem", "revisado") \
     .write_csv(cfg.MACROFAMILIAS_CSV)
    # M3: amostra aleatória de 30 classificadas pelo LLM, seed fixa
    llm = t.filter(pl.col("origem") == "llm").sort("cbo")
    random.seed(cfg.SEED)
    idx = sorted(random.sample(range(llm.height), min(30, llm.height)))
    amostra = llm[idx].select("cbo", "titulo_cbo", pl.col("area").alias("llm_area"), pl.col("nivel").alias("llm_nivel")) \
                      .with_columns([pl.lit("").alias(c) for c in
                                     ["revisor_1_area", "revisor_1_nivel", "revisor_2_area", "revisor_2_nivel"]])
    amostra.write_csv(cfg.REPORTS / "revisao_macrofamilias.csv")
    relatorio(t)


def relatorio(t: pl.DataFrame) -> None:
    tot = t["movimentos"].sum()
    dist = lambda col: (t.group_by(col).agg(pl.col("movimentos").sum(), pl.len().alias("cbos"))
                        .sort("movimentos", descending=True)
                        .with_columns((100 * pl.col("movimentos") / tot).round(1).alias("pct")))
    fora_lista = t.filter(~pl.col("area").is_in([a.value for a in Area] + ["Outros"])
                          | ~pl.col("nivel").is_in([n.value for n in Nivel] + ["Outros"])).height
    tab = lambda df, col: "\n".join([f"| {col} | CBOs | Movimentos | % |", "| --- | --- | --- | --- |"] +
                                    [f"| {r[col]} | {r['cbos']} | {r['movimentos']:,} | {r['pct']} |" for r in df.iter_rows(named=True)])
    revisar = t.filter(pl.col("m1_confianca_baixa") | pl.col("m2_divergente")).sort("movimentos", descending=True)
    md = [f"# Validação das macrofamílias\n\nExecução: {datetime.now():%Y-%m-%d %H:%M}\n",
          f"- CBOs de B–F: {t.height} · com área e nível: {t.filter(pl.col('area').is_not_null()).height} · "
          f"fora da lista fechada: {fora_lista}",
          f"- Origem: " + ", ".join(f"{r['origem']} {r['len']}" for r in t.group_by('origem').len().iter_rows(named=True)),
          f"- M1 (confiança baixa): {t['m1_confianca_baixa'].sum()} · M2 (divergência com o grande grupo): {t['m2_divergente'].sum()}",
          "\n## Por área\n", tab(dist("area"), "area"), "\n## Por nível\n", tab(dist("nivel"), "nivel"),
          "\n## Lista de revisão (M1 + M2)\n", "| CBO | Título | Área | Nível | Confiança | M2 |", "| --- | --- | --- | --- | --- | --- |"]
    md += [f"| {r['cbo']} | {r['titulo_cbo']} | {r['area']} | {r['nivel']} | {r['confianca']} | {'sim' if r['m2_divergente'] else ''} |"
           for r in revisar.iter_rows(named=True)]
    (cfg.REPORTS / "macrofamilias_validacao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:8]))


def main(forcar_llm: bool = False, plano_b: str | None = None) -> None:
    u = universo_cbos()
    escopo = u.filter(pl.col("no_escopo"))
    print(f"CBOs de B–F: {u.height} · no escopo (95% dos movimentos): {escopo.height} "
          f"· sem título no dicionário: {u['sem_titulo'].sum()} ({escopo['sem_titulo'].sum()} no escopo)")
    exportar_plano_b(escopo)

    if plano_b:
        itens, origem, manuais = importar_plano_b(Path(plano_b), escopo), "llm", []
        registrar_prompt("chat (plano B)", f"plano B: {plano_b}")
    elif cfg.RODAR_LLM or forcar_llm or len(list(cfg.LLM_CACHE.glob("lote_*.json"))) >= -(-escopo.height // cfg.LOTE_LLM):
        itens, manuais = classificar_com_gemini(escopo)
        origem = "llm"
        registrar_prompt(cfg.GEMINI_MODEL, "API do Gemini")
    elif cfg.MACROFAMILIAS_CSV.exists():
        print(f"RODAR_LLM = False: mantendo {cfg.MACROFAMILIAS_CSV.name} existente.")
        return
    else:
        registrar_prompt(cfg.GEMINI_MODEL, "ainda não executado")
        print("Nada a classificar ainda: sem chave/cache e sem resposta do plano B.\n"
              "  Caminho A: crie .env com GEMINI_API_KEY e rode `python src/macrofamilias.py --llm`.\n"
              "  Caminho B: siga prompts/plano_b_chat.md.")
        return
    if manuais:
        print(f"Atenção: lotes para classificação manual: {manuais}")
    salvar(montar_tabela(u, itens, origem))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--llm", action="store_true")
    p.add_argument("--plano-b", default=None)
    a = p.parse_args()
    main(a.llm, a.plano_b)
