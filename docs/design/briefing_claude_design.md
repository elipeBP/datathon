# Briefing de design: Raio-X da Indústria SC

Você vai desenhar as telas de um site de jornalismo de dados sobre o mercado de trabalho industrial de Santa Catarina. O site já existe e funciona (https://datathon-ebon.vercel.app), mas parece genérico, com cara de "dashboard feito por IA". Quero um redesenho com identidade própria, bonito e muito claro no celular.

Depois, as telas serão implementadas em React (Vite) com gráficos em SVG. Desenhe coisas que dão para construir assim: nada de 3D, nada que dependa de vídeo pesado.

---

## 1. Contexto em uma frase

Consultoria de dados para a indústria catarinense: o site mostra **onde** a indústria perde trabalhadores, **por quê**, e **o que fazer**. A frase central é:

> **"O apagão da indústria catarinense aparece como rotatividade, não como falta de gente."**

Público: diretores de indústria e de formação profissional, e uma banca de avaliação de um datathon universitário. Eles vão abrir o link **no celular**, muitos pela primeira vez, durante ou logo depois de um pitch de 3 minutos.

## 2. O que eu quero (e o que não quero)

**Quero:**
- **Cara de coisa feita à mão, com matéria e textura**: papel, impressão, etiqueta, carimbo. Pense em revista impressa, em cartaz de sindicato antigo, em etiqueta de fábrica, em caderno de chão de fábrica. Calor humano, não tecnologia.
- **Adesivos (stickers) ilustrados por setor industrial.** Quando a pessoa escolhe ou vê um setor, aparecem adesivos com os objetos daquele ofício: borda branca recortada, leve rotação, sombra curta, como se colados na página. Lista na seção 5.
- **Mobile first, 390 px de largura.** Uma ideia por tela, números grandes, gráficos que cabem sem rolagem lateral, toques confortáveis (alvos de 44 px ou mais).
- **Números como protagonistas.** Os dados são bons; o design deve deixá-los gritarem.
- **Português do Brasil**, tom direto, sem jargão.

**Não quero (cara de IA, evitar):**
- Gradiente roxo e azul, fundo escuro com brilho neon, glassmorphism, cartões flutuantes com borda luminosa.
- Ícones de faísca/estrela de "IA", robôs, cérebros, circuitos decorativos.
- Grade genérica de cartões iguais com ícone + título + texto.
- Emojis como ícone.
- Fontes Inter, Roboto ou Poppins como identidade.
- Ilustrações 3D lisas e brilhantes, bonecos genéricos de banco de imagem.
- Logos ou identidade visual da FIESC, do SENAI ou de qualquer empresa real. O site cita essas instituições pelo nome, mas não usa a marca delas.

## 3. Marca mínima

**Nome:** Raio-X da Indústria SC
**Assinatura:** "Onde a indústria catarinense perde gente, por quê e o que fazer."
**Tom:** repórter que entende de fábrica. Frases curtas, afirmativas, com número.

**Cores (proposta, pode refinar mantendo os papéis):**

| Papel | Cor | Uso |
| --- | --- | --- |
| Papel (fundo) | `#F4F0E6` | fundo geral, levemente amarelado, com textura sutil de papel |
| Tinta | `#1C1B18` | texto principal |
| Tinta 2 | `#5A574F` | texto secundário |
| Sinal (atenção) | `#D63F2C` | o que pede atenção: saídas a pedido acima da média, setores encolhendo, "apagão" |
| Expansão | `#2D5DA8` | o que cresce (saldo positivo) |
| Retenção | `#5B4BC4` | quadrante "não cresce e perde gente" |
| Neutro de dado | `#B5B0A3` | barras e pontos sem destaque |
| Linha/grade | `#DDD6C6` | grades e divisórias |

Regra: **cor de dado tem significado fixo** (vermelho = perde gente / atenção; azul = cresce; violeta = retenção problemática; cinza = sem destaque). As cores dos adesivos são livres e só decoram, nunca codificam dado. Um modo escuro é bem-vindo, mas não obrigatório.

**Tipografia (sugestão):**
- Títulos: uma serifada expressiva (ex.: Fraunces, ou outra com personalidade editorial).
- Texto: uma sans humanista legível (ex.: IBM Plex Sans, Source Sans 3).
- Números e rótulos de gráfico: uma mono ou com algarismos tabulares (ex.: IBM Plex Mono), dando ar de etiqueta de fábrica e ficha técnica.
- Todas gratuitas no Google Fonts.

**Elementos gráficos de apoio:** etiquetas tipo "tag de roupa" para rótulos, carimbos para status ("APROVADO", "PENDENTE"), fita adesiva segurando cartões, numeração de capítulo grande, textura de meio-tom (halftone) ou risografia em detalhes. Use com parcimônia: o dado vem primeiro.

## 4. Telas (mobile 390 px; e uma versão desktop da tela 1 e da tela 2)

### Tela 1: Abertura / tese
- Título: "O apagão da indústria catarinense aparece como **rotatividade**, não como falta de gente."
- Número herói: **50,9%** "dos desligamentos da indústria de transformação são a pedido do trabalhador" (417.429 desligamentos em 12 meses).
- Três números de apoio:
  - **+1.008** saldo de empregos em 12 meses, em 835.866 movimentações: "o setor gira muito e quase não cresce".
  - **0,975** "quem entra ganha 2,5% menos que quem sai, na mesma ocupação e região".
  - **−0,02 p.p.** "quem entra tem a mesma escolaridade de quem sai: o problema não é formação".
- Fonte pequena: Novo CAGED (MTE), Santa Catarina, set/2025 a ago/2026.
- Uma colagem leve de adesivos de vários setores pode compor a abertura.

### Tela 2: Onde (mapa)
- Mapa de Santa Catarina por **20 microrregiões**, com um seletor de duas posições:
  - **"Saídas a pedido (apagão)"**: escala de um tom só, do papel ao vermelho.
  - **"Saldo por 10 mil hab. (expansão)"**: divergente, vermelho (encolhe) ↔ neutro ↔ azul (cresce).
- Toque numa região abre uma ficha (bottom sheet no celular) com nome, % a pedido, saldo, movimentações.
- Abaixo, ranking das microrregiões.
- Título-conclusão: "O Oeste cresce e perde gente; o Vale do Itajaí encolhe e perde gente."
- Dados na seção 6.

### Tela 3: Setores (aqui entram os adesivos)
- Seletor de setor (chips roláveis na horizontal ou carrossel). Ao escolher um setor, a tela mostra:
  - os **adesivos** daquele setor espalhados pelo topo, como se recém-colados (pequena animação de "colar", se possível);
  - % das saídas a pedido versus média de SC (50,9%);
  - saldo de 12 meses (cresce ou encolhe);
  - salário mediano de quem entra versus quem sai;
  - em qual quadrante ele cai.
- Uma visão geral comparando todos os setores (barras) antes de escolher um.
- Destaque: "Uma única ocupação, o alimentador de linha de produção, é 24% de todas as movimentações. Sem ela, o saldo seria −14.655."

### Tela 4: Por quê
- Mensagem: "Não é escolaridade: é retenção e salário de reposição."
- Gráfico das ocupações agrupadas pela IA (área × nível de formação) com maior % de saída a pedido.
- Comparação salário de quem entra × quem sai, por setor (haltere: dois pontos ligados por linha).
- Escolaridade de quem entra × quem sai (quase idênticas: esse é o ponto).
- Selo discreto explicando a IA: "354 ocupações classificadas por IA (Gemini) em 15 áreas e 4 níveis de formação, com lista fechada e revisão humana." Sem ícone de faísca; pode ser uma etiqueta/carimbo.

### Tela 5: O que fazer (3 recomendações)
Três cartões fortes, cada um com: ação, onde, para quem, por quê (com número), quem executa e **um número de linha de base** para acompanhar. Os adesivos do setor de cada recomendação podem identificar o cartão.
1. **Programa de retenção na agroindústria**, no Oeste (Chapecó, Joaçaba, Concórdia, Xanxerê, São Miguel do Oeste). 64,6% das saídas a pedido em ofícios da agroindústria (SC: 50,9%), num setor que ainda cresce (+2.699 vagas). Quem executa: agroindústrias, com apoio da FIESC. Linha de base: **64,6%**.
2. **Revisão de faixa salarial e retenção no têxtil**, em Rio do Sul. 68,6% a pedido; o setor encolhe e a reposição paga 4,3% menos. Quem executa: confecções do Alto Vale, com apoio da FIESC. Linha de base: **68,6%**.
3. **Requalificação do têxtil para eletroeletrônica e automação**, em Blumenau. O têxtil perdeu 1.283 vagas e a eletroeletrônica criou 568 na mesma região. Quem executa: SENAI-SC. Linha de base: **+189 vagas** na eletroeletrônica.

### Tela 6 (opcional, simples): Método
- "0,01% de diferença para o boletim oficial da FIESC", "7 testes de robustez", "354 ocupações classificadas por IA".
- Lista de testes com carimbo de status (Aprovado / Reprovado / Pendente). Teste reprovado aparece com honestidade, não escondido.
- Premissas em acordeão.

## 5. Adesivos por setor

Estilo único para todos: ilustração plana com traço levemente irregular (feito à mão), 2 a 4 cores por adesivo, borda branca recortada de 3 a 4 px, sombra curta e suave, rotação entre −8° e 8°. Textura de papel ou de impressão risográfica é bem-vinda. Cada adesivo funciona sozinho em 64 a 96 px.

| Setor | Adesivos |
| --- | --- |
| Têxtil, confecção e calçados | carretel de linha, novelo e flor de algodão, agulha com linha, tesoura de costura, etiqueta de roupa, fita métrica |
| Alimentos e bebidas (agroindústria do Oeste) | espiga de milho, caixa de leite, galinha estilizada, ovo, garrafa, avental e touca de fábrica |
| Madeira e móveis | tora com anéis, pinha de araucária, serrote, cadeira de madeira, lápis de carpinteiro |
| Metalmecânica | engrenagem, porca e parafuso, chave inglesa, faísca de solda com máscara, peça usinada |
| Eletroeletrônica | bobina de fio de cobre, motor elétrico, placa de circuito simples, plugue, lâmpada |
| Minerais não metálicos e cerâmica | azulejo/porcelanato com padrão, xícara, tijolo, vaso |
| Plástico e borracha | grânulos de plástico, pneu, balde, garrafa PET |
| Papel, celulose e gráfica | rolo de papel, caixa de papelão, folha impressa com marcas de registro |
| Química e farmacêutica | frasco de laboratório, gota, comprimido |
| Construção | capacete, tijolo, colher de pedreiro, trena |

Detalhe que dá vida: o adesivo do setor que está "perdendo gente" pode ter um pequeno detalhe de desgaste (canto levantado), e o do setor que cresce, um brilho de novo. Sutil.

## 6. Dados reais para usar nas telas (não invente números)

**Setores da transformação (12 meses):**

| Setor | % saídas a pedido | Saldo | Salário de quem entra | Salário de quem sai |
| --- | --- | --- | --- | --- |
| Alimentos e bebidas | 56,2% | +4.731 | R$ 2.100 | R$ 2.164 |
| Madeira e móveis | 53,1% | −2.710 | R$ 2.039 | R$ 2.127 |
| Têxtil, confecção e calçados | 52,4% | −5.916 | R$ 2.141 | R$ 2.220 |
| Eletroeletrônica | 50,1% | +1.646 | R$ 2.268 | R$ 2.407 |
| Plástico e borracha | 49,7% | +265 | R$ 2.230 | R$ 2.275 |
| Papel, celulose e gráfica | 48,3% | +340 | R$ 2.106 | R$ 2.234 |
| Minerais não metálicos e cerâmica | 47,4% | −842 | R$ 2.300 | R$ 2.437 |
| Química e farmacêutica | 46,1% | +341 | R$ 2.210 | R$ 2.326 |
| Metalmecânica | 45,6% | +3.459 | R$ 2.414 | R$ 2.556 |

Média de SC: 50,9% a pedido. Em todos os setores, quem entra ganha menos que quem sai.

**Microrregiões (transformação), % a pedido · saldo por 10 mil habitantes:**
São Miguel do Oeste 67,0% · +11,3 | Concórdia 62,6% · +24,7 | Ituporanga 61,5% · +9,6 | Tabuleiro 59,8% · +0,4 | Rio do Sul 58,9% · −29,4 | Joaçaba 56,2% · +14,2 | São Bento do Sul 55,4% · −77,8 | Chapecó 55,1% · +49,1 | Xanxerê 53,8% · +10,6 | Canoinhas 52,5% · −1,2 | Criciúma 51,4% · −4,6 | Curitibanos 51,2% · −18,0 | Tubarão 50,8% · −8,2 | Blumenau 49,3% · −29,7 | Itajaí 48,0% · +32,6 | Joinville 47,5% · +5,2 | Araranguá 45,8% · −27,5 | Tijucas 43,7% · −23,1 | Campos de Lages 43,5% · +13,1 | Florianópolis 38,7% · −4,9

**Quadrantes (microrregião × setor):** 37 "crescem e perdem gente" (expansão sob pressão), 31 "não crescem e perdem gente" (retenção problemática), 31 "crescem e retêm", 36 "estagnados".

**Ocupações (macrofamílias da IA) com mais saídas a pedido:** Alimentos e bebidas, acima de 200h: 62,8% · Têxtil, acima de 200h: 55,7% · Operação de linha e montagem, até 200h: 55,7% · Têxtil, até 200h: 54,2% · Serviços de apoio: 50,7% · Madeira e móveis: 49,8% · Metalmecânica e soldagem: 45,7%.

**Escolaridade (quem entra × quem sai):** até fundamental 22% × 22%; médio 70% × 70%; superior incompleto 3% × 3%; superior ou mais 5% × 5%.

## 7. Regras de gráfico

- Todo gráfico tem um **título que é a conclusão** ("Alimentos cresce e perde gente"), não o tema ("Saídas por setor").
- Um eixo por gráfico; nunca dois eixos verticais no mesmo plot.
- Barras finas com ponta arredondada; linha de referência tracejada para a média de SC.
- Rótulos diretos só nos pontos que contam a história, não em todos.
- Texto nunca na cor do dado: a cor fica na marca (barra, ponto); o texto fica em tinta.
- Tudo legível em 390 px sem rolagem lateral; no celular, prefira barras horizontais e uma métrica por gráfico.
- Toque em barra, ponto ou região abre detalhe (tooltip no desktop, bottom sheet no celular).

## 8. Entregáveis

1. As 6 telas no celular (390 px) e as telas 1 e 2 no desktop (1280 px).
2. Uma folha de estilo: cores, tipografia com tamanhos, espaçamentos, botões, chips, seletor de duas posições, cartão, etiqueta e carimbo.
3. A família de adesivos da seção 5 (pelo menos têxtil, alimentos, madeira, metalmecânica e eletroeletrônica completos), em formato que dê para exportar como SVG.
4. Notas curtas de interação: o que anima, quando e por quanto tempo. Respeitar quem desativa animações no sistema.
