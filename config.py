"""Parâmetros do projeto (SDD v2). Mudar uma decisão = trocar uma linha aqui."""
import os
from pathlib import Path

# ---------------------------------------------------------------- caminhos
ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
REFERENCE = ROOT / "data" / "reference"
PROCESSED = Path(os.getenv("DATATHON_PROCESSED", ROOT / "data" / "processed"))  # variável só para testes
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
LLM_CACHE = INTERIM / "llm_cache"

CAGED_CSV = RAW / "Novo_Caged_MOV_Limpo.csv"
MUNICIPIOS_CSV = RAW / "Municipios_SC_limpo.csv"
DICIONARIO_XLSX = RAW / "Dicionario_de_dados.xlsx"

CAGED_RAW_PARQUET = INTERIM / "caged_raw.parquet"
CAGED_IND_PARQUET = INTERIM / "caged_ind.parquet"
LOG_PIPELINE = REPORTS / "log_pipeline.md"
TESTES_MD = REPORTS / "testes.md"

MUNICIPIOS_REGIOES_CSV = REFERENCE / "municipios_regioes.csv"
GEOJSON_MICRO = REFERENCE / "sc_microrregioes.geojson"
CBO_TITULOS_CSV = REFERENCE / "cbo_titulos.csv"
SUBCLASSE_CSV = REFERENCE / "subclasse_descricao.csv"
MACROFAMILIAS_CSV = REFERENCE / "macrofamilias.csv"
RECOMENDACOES_YAML = Path(os.getenv("DATATHON_RECOMENDACOES", ROOT / "app" / "recomendacoes.yaml"))
RECOMENDACOES_MD = REPORTS / "recomendacoes_candidatas.md"

# ---------------------------------------------------------------- APIs IBGE (R12)
# Conferir em servicodados.ibge.gov.br/api/docs antes de usar.
IBGE_MUNICIPIOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/42/municipios"
IBGE_MALHA_MICRO_URL = (
    "https://servicodados.ibge.gov.br/api/v3/malhas/estados/42"
    "?intrarregiao=microrregiao&formato=application/vnd.geo+json"
)
GEOJSON_MAX_MB = 5

# ---------------------------------------------------------------- R1b: nomes ASCII
RENOMEAR_COLUNAS = {
    "competênciamov": "competenciamov",
    "região": "regiao",
    "município": "municipio",
    "seção": "secao",
    "saldomovimentação": "saldomovimentacao",
    "cbo2002ocupação": "cbo2002ocupacao",
    "graudeinstrução": "graudeinstrucao",
    "raçacor": "racacor",
    "tipomovimentação": "tipomovimentacao",
    "tipodedeficiência": "tipodedeficiencia",
    "salário": "salario",
    "origemdainformação": "origemdainformacao",
    "competênciadec": "competenciadec",
    "unidadesaláriocódigo": "unidadesalariocodigo",
    "valorsaláriofixo": "valorsalariofixo",
    # Caso uma versão nova do arquivo traga as colunas de exclusão (R6):
    "indicadordeexclusão": "indicadordeexclusao",
    "competênciaexc": "competenciaexc",
}
COLUNAS_INDICE = ["Unnamed: 0.1", "Unnamed: 0"]

# ---------------------------------------------------------------- R4, R5: janela e seções
JANELA_INI = "202509"
JANELA_FIM = "202608"
SECOES = ["B", "C", "D", "E", "F"]
SECAO_PRINCIPAL = "C"
SEGMENTO_POR_SECAO = {
    "C": "Transformação",
    "B": "Extrativa e utilidades",
    "D": "Extrativa e utilidades",
    "E": "Extrativa e utilidades",
    "F": "Construção",
}

# ---------------------------------------------------------------- R8, R9: base de salário
SAL_MIN = 1000
SAL_MAX = 30000

# ---------------------------------------------------------------- R10: escolaridade
FAIXA_ESCOLARIDADE = {
    **{c: "Até fundamental" for c in ["1", "2", "3", "4", "5"]},
    "6": "Médio", "7": "Médio",
    "8": "Superior incompleto",
    **{c: "Superior ou mais" for c in ["9", "10", "11", "80"]},
    "99": "Não identificado",
}

# ---------------------------------------------------------------- R14: grupos setoriais
GRUPOS_SETORIAIS = {
    "Alimentos e bebidas": ["10", "11"],
    "Têxtil, confecção e calçados": ["13", "14", "15"],
    "Madeira e móveis": ["16", "31"],
    "Papel, celulose e gráfica": ["17", "18"],
    "Química e farmacêutica": ["19", "20", "21"],
    "Plástico e borracha": ["22"],
    "Minerais não metálicos e cerâmica": ["23"],
    "Metalmecânica": ["24", "25", "28", "29", "30", "33"],
    "Eletroeletrônica": ["26", "27"],
    "Outras da transformação": ["12", "32"],
    "Extrativa": ["05", "06", "07", "08", "09"],
    "Utilidades": ["35", "36", "37", "38", "39"],
    "Construção": ["41", "42", "43"],
}
GRUPO_POR_DIVISAO = {d: g for g, ds in GRUPOS_SETORIAIS.items() for d in ds}

# ---------------------------------------------------------------- KPIs (seção 5)
MIN_DESL = 300
MIN_MOV = 300
MIN_ADM_SAL = 50
MIN_DESL_SAL = 50
MIN_ADM_ESC = 100
MIN_DESL_ESC = 100
QL_CORTE = 1.25
QL_MIN_MOV = 1000
T2_CORTE_PP = 5
CBO_DOMINANTE = "784205"  # alimentador de linha de produção (T3)

# ---------------------------------------------------------------- T1: reconciliação (saldo jan–mai/2026)
T1_JANELA = ("202601", "202605")
T1_TOLERANCIA = 0.005
T1_REFERENCIA_FIESC = {
    "Transformação (C)": (["C"], 24269),
    "Indústria geral (B–E)": (["B", "C", "D", "E"], 24527),
    "Construção (F)": (["F"], 10721),
    "Indústria total (B–F)": (["B", "C", "D", "E", "F"], 35248),
}

# ---------------------------------------------------------------- IA (seção 6)
RODAR_LLM = False
GEMINI_MODEL = "gemini-3.8-flash"          # Flash mais recente em ai.google.dev (consultado em 10/11/2026)
GEMINI_MODEL_RESERVA = "gemini-3.5-flash-lite"  # usar se o limite diário do plano gratuito estourar
LLM_MAX_TENTATIVAS = 3
CBOS_SEM_TITULO_CONFIANCA = "baixa"  # V20
LOTE_LLM = 50
COBERTURA_CBO = 0.95
SEED = 42
