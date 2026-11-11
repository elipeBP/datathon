# Plano B — classificar no Google AI Studio (ou outro chat)

1. Cole a instrução abaixo como instrução de sistema, com temperatura 0.
2. Envie um lote por vez e cole cada resposta JSON, em ordem, numa única lista em `data/interim/resposta_plano_b.json`.
3. Rode `python src/macrofamilias.py --plano-b data/interim/resposta_plano_b.json`. As mesmas validações do caminho com API são aplicadas.

## Instrução

```text
Você é um especialista em classificação de ocupações (CBO 2002) e em formação profissional industrial
no Brasil, no formato do Mapa do Trabalho Industrial (SENAI/CNI).

Classifique cada ocupação da lista em UMA área e UM nível de formação, usando SOMENTE os valores abaixo.
Nunca crie categorias, nunca altere nem invente códigos de CBO. Devolva exatamente as CBOs recebidas, uma vez cada.

ÁREAS:
- Alimentos e bebidas: Ocupações específicas do processamento de alimentos e bebidas: abate, desossa, laticínios, panificação industrial
- Têxtil, confecção e calçados: Fiação, tecelagem, corte, costura, acabamento, calçados
- Metalmecânica e soldagem: Usinagem, caldeiraria, soldagem, fundição, estamparia, montagem mecânica especializada
- Manutenção industrial: Mecânicos, eletricistas e eletromecânicos de manutenção, lubrificadores
- Eletroeletrônica e automação: Montagem e operação eletroeletrônica, instrumentação, automação, bobinagem
- Madeira e móveis: Serraria, marcenaria, montagem de móveis
- Plástico, borracha e química: Operação de injetoras e extrusoras, processos químicos
- Cerâmica, vidro e minerais: Fabricação de cerâmica, porcelanato, louça, vidro, cimento e artefatos de minerais não metálicos
- Logística e movimentação: Motoristas, operadores de empilhadeira, almoxarifes, conferentes, expedição
- Operação de linha e montagem: Funções genéricas de produção: alimentadores de linha, operadores de máquina não específicos, montadores, embaladores
- Construção: Pedreiros, serventes de obra, carpinteiros de obra, armadores, instaladores prediais
- Qualidade e controle: Inspeção, controle de qualidade, laboratório, segurança do trabalho
- Gestão, administrativo e comercial: Gerentes, supervisores administrativos, escritório, RH, finanças, compras, vendas, representantes
- Engenharia e P&D: Engenheiros, projetistas, desenvolvedores, químicos, pesquisadores
- Serviços de apoio: Limpeza, portaria, vigilância, cozinha, conservação

Regra de área: se a ocupação é específica de um ramo (ex.: magarefe, costureira industrial), use a área do ramo;
se é genérica de produção (ex.: alimentador de linha, embalador), use "Operação de linha e montagem".

NÍVEIS DE FORMAÇÃO:
- Qualificação até 200h: Aprende no posto ou em curso curto (ex.: alimentador de linha, embalador, servente)
- Qualificação acima de 200h: Ofício que exige curso de qualificação longo ou prática prolongada (ex.: soldador, eletricista de manutenção, operador de CNC)
- Técnico: Curso técnico de nível médio (ex.: técnico em eletrotécnica, técnico de segurança do trabalho)
- Superior: Graduação (ex.: engenheiros, analistas, contadores)

CONFIANÇA: "alta", "media" ou "baixa". Em caso de dúvida, escolha a opção mais próxima e marque a confiança como baixa.
Se o título vier como "(sem título no dicionário)", classifique só pelo código e pelo contexto e marque a confiança como baixa.

JUSTIFICATIVA: até 15 palavras, em português.

EXEMPLOS RESOLVIDOS:
- CBO 784205 "Alimentador de Linha de Produção" → {"cbo": "784205", "area": "Operação de linha e montagem", "nivel": "Qualificação até 200h", "confianca": "alta", "justificativa": "Função genérica de produção, aprendida no posto"}
- CBO 351605 "Técnico em Segurança no Trabalho" → {"cbo": "351605", "area": "Qualidade e controle", "nivel": "Técnico", "confianca": "alta", "justificativa": "Segurança do trabalho exige curso técnico de nível médio"}
- CBO 252405 "Analista de Recursos Humanos" → {"cbo": "252405", "area": "Gestão, administrativo e comercial", "nivel": "Superior", "confianca": "alta", "justificativa": "Função administrativa de RH que exige graduação"}

Para cada ocupação você recebe: código CBO, título oficial, grande grupo da CBO, seção CNAE e grupo setorial
onde ela mais aparece em Santa Catarina, e o número de movimentações (admissões + desligamentos) em 12 meses.
Responda apenas com uma lista JSON de objetos com as chaves cbo, area, nivel, confianca, justificativa.
```

## Lotes

### Lote 01

```text
784205 | Alimentador de Linha de Producao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 207,461 movimentos
717020 | Servente de Obras | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 68,428 movimentos
715210 | Pedreiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 43,592 movimentos
848520 | Magarefe | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 36,298 movimentos
411005 | Auxiliar de Escritorio, em Geral | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 26,198 movimentos
411010 | Assistente Administrativo | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Metalmecânica | 23,067 movimentos
763210 | Costureiro na Confeccao em Serie | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 20,199 movimentos
763215 | Costureiro, a  Maquina  na Confeccao em Serie | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 19,137 movimentos
414105 | Almoxarife | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Metalmecânica | 18,757 movimentos
715505 | Carpinteiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 18,111 movimentos
782510 | Motorista de Caminhao (Rotas Regionais e Internacionais) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Construção | 17,620 movimentos
514320 | Faxineiro (Desativado em 2010) | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 17,430 movimentos
724315 | Soldador | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 15,263 movimentos
763125 | Ajudante de Confecção | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 14,486 movimentos
911305 | Mecanico de Manutencao de Maquinas, em Geral | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Metalmecânica | 12,130 movimentos
784105 | Embalador, a Mao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 11,559 movimentos
761815 | Revisor de Tecidos Acabados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 11,475 movimentos
414135 | Expedidor de Mercadorias | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 11,240 movimentos
716610 | Pintor de Obras | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 11,051 movimentos
862150 | Operador de Maquinas Fixas, em Geral | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 10,606 movimentos
715525 | Carpinteiro de Obras | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 9,600 movimentos
724205 | Montador de Estruturas Metalicas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 9,485 movimentos
715615 | Eletricista de Instalacoes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 9,182 movimentos
715315 | Armador de Estrutura de Concreto Armado | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 8,961 movimentos
521110 | Vendedor de Comercio Varejista | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 8,885 movimentos
514205 | Coletor de Lixo Domiciliar | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção E | Utilidades | 7,578 movimentos
513505 | Auxiliar nos Serviços de Alimentação | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 7,542 movimentos
391205 | Inspetor de Qualidade | grande grupo 3 (Técnicos de nível médio) | seção C | Alimentos e bebidas | 7,251 movimentos
771105 | Marceneiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 7,064 movimentos
761005 | Operador Polivalente da Industria Textil | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 6,913 movimentos
710205 | Mestre (Construcao Civil) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 6,854 movimentos
414210 | Apontador de Producao | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 6,796 movimentos
715305 | Armador de Estrutura de Concreto | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 5,929 movimentos
721215 | Operador de Maquinas-Ferramenta Convencionais | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 5,923 movimentos
811770 | Moldador de Plastico por Injecao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 5,731 movimentos
725205 | Montador de Maquinas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 5,456 movimentos
724110 | Encanador | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 5,420 movimentos
414140 | Auxiliar de Logistica | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 5,418 movimentos
782220 | Operador de Empilhadeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 4,981 movimentos
731175 | Operador de Linha de Montagem (Aparelhos Eletricos) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 4,806 movimentos
521140 | Atendente de Lojas e Mercados | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 4,803 movimentos
354125 | Assistente de Vendas | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 4,456 movimentos
763105 | Auxiliar de Corte (Preparacao da Confeccao de Roupas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 4,426 movimentos
414110 | Armazenista | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 4,352 movimentos
724440 | Serralheiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 4,142 movimentos
813125 | Operador de Producao (Quimica, Petroquimica e Afins) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Química e farmacêutica | 4,035 movimentos
783225 | Ajudante de Motorista | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 3,870 movimentos
761330 | Tecelao de Malhas (Maquina Circular) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 3,693 movimentos
951105 | Eletricista de Manutencao Eletroeletronica | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Construção | 3,591 movimentos
351605 | Tecnico em Seguranca no Trabalho | grande grupo 3 (Técnicos de nível médio) | seção C | Construção | 3,406 movimentos
```

### Lote 02

```text
821450 | Rebarbador de Metal | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 3,301 movimentos
774105 | Montador de Moveis e Artefatos de Madeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 3,229 movimentos
725105 | Montador de Maquinas, Motores e Acessorios (Montagem em Serie) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 3,228 movimentos
513435 | Atendente de Lanchonete | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 3,125 movimentos
954125 | Operador Eletromecanico | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Metalmecânica | 3,125 movimentos
782310 | Motorista de Furgao ou Veiculo Similar | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 3,058 movimentos
514325 | Trabalhador da Manutenção de Edificações | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção F | Construção | 3,025 movimentos
724410 | Caldeireiro (Chapas de Ferro e Aco) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 2,977 movimentos
761410 | Estampador de Tecido | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,878 movimentos
841484 | Trabalhador de Preparacao de Pescados (Limpeza) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 2,874 movimentos
763110 | Cortador de Roupas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,803 movimentos
752305 | Ceramista | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Minerais não metálicos e cerâmica | 2,739 movimentos
715125 | Operador de Maquinas de Construcao Civil e Mineracao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 2,716 movimentos
391125 | Tecnico de Planejamento de Producao | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 2,706 movimentos
721405 | Operador de Centro de Usinagem com Comando Numerico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 2,647 movimentos
731120 | Montador de Equipamentos Eletricos (Aparelhos Eletrodomesticos) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 2,646 movimentos
715115 | Operador de Escavadeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 2,622 movimentos
761309 | Tecelao (Tear Automatico) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,570 movimentos
841505 | Trabalhador de Tratamento do Leite e Fabricacao de Laticinios e Afins | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 2,556 movimentos
772105 | Classificador de Madeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 2,536 movimentos
722215 | Operador de Acabamento de Pecas Fundidas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 2,470 movimentos
773325 | Operador de Maquina de Usinagem Madeira, em Geral | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 2,422 movimentos
764005 | Trabalhador Polivalente da Confeccao de Calcados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,421 movimentos
252405 | Analista de Recursos Humanos | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 2,390 movimentos
783215 | Carregador (Veiculos de Transportes Terrestres) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 2,381 movimentos
731135 | Montador de Equipamentos Eletricos | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 2,353 movimentos
716510 | Ladrilheiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 2,277 movimentos
715230 | Pedreiro de Edificacoes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 2,241 movimentos
723330 | Pintor, a  Pistola (Exceto Obras e Estruturas Metalicas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 2,220 movimentos
723315 | Pintor de Estruturas Metalicas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 2,215 movimentos
811775 | Trefilador de Borracha | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 2,215 movimentos
716405 | Gesseiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 2,185 movimentos
422105 | Recepcionista, em Geral | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Construção | 2,170 movimentos
761327 | Tecelao de Malhas, a  Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,155 movimentos
784110 | Embalador, a Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 2,116 movimentos
763320 | Operador de Maquina de Costura de Acabamento | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 2,003 movimentos
414215 | Conferente de Carga e Descarga | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 1,966 movimentos
391210 | Tecnico de Garantia da Qualidade | grande grupo 3 (Técnicos de nível médio) | seção C | Alimentos e bebidas | 1,953 movimentos
763010 | Costureira de Pecas Sob Encomenda | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 1,934 movimentos
391215 | Operador de Inspecao de Qualidade | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 1,927 movimentos
141205 | Gerente de Producao e Operacoes | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Metalmecânica | 1,896 movimentos
354205 | Comprador | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 1,765 movimentos
724220 | Preparador de Estruturas Metalicas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,713 movimentos
722205 | Fundidor de Metais | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,691 movimentos
414125 | Estoquista | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 1,661 movimentos
724510 | Operador de Maquina de Dobrar Chapas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,631 movimentos
312105 | Tecnico de Obras Civis | grande grupo 3 (Técnicos de nível médio) | seção F | Construção | 1,609 movimentos
514310 | Auxiliar de Manutenção Predial | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Construção | 1,607 movimentos
413110 | Auxiliar de Contabilidade | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Metalmecânica | 1,599 movimentos
848505 | Abatedor | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 1,581 movimentos
```

### Lote 03

```text
721210 | Operador de Maquinas Operatrizes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,572 movimentos
521115 | Promotor de Vendas | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 1,570 movimentos
763310 | Bordador, À Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 1,566 movimentos
848305 | Padeiro | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 1,565 movimentos
823325 | Trabalhador da Elaboracao de Pre-Fabricados (Concreto Armado) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Minerais não metálicos e cerâmica | 1,563 movimentos
842120 | Auxiliar de Processamento de Fumo | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Outras da transformação | 1,560 movimentos
142335 | Analista de Pesquisa de Mercado (A) | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Têxtil, confecção e calçados | 1,513 movimentos
725010 | Ajustador Mecanico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,499 movimentos
514225 | Trabalhador de Servicos de Limpeza e Conservacao de Areas Publicas | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Utilidades | 1,473 movimentos
766315 | Operador de Acabamento (Industria Grafica) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Papel, celulose e gráfica | 1,451 movimentos
992225 | Auxiliar Geral de Conservacao de Vias Permanentes (Exceto Trilhos) | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção F | Construção | 1,447 movimentos
715610 | Eletricista de Instalacoes (Edificios) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,441 movimentos
848310 | Confeiteiro | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 1,399 movimentos
725505 | Montador de Veiculos (Linha de Montagem) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,360 movimentos
721430 | Operador de Torno com Comando Numerico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,358 movimentos
252105 | Administrador | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Construção | 1,331 movimentos
311710 | Colorista Textil | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 1,327 movimentos
911205 | Mecanico de Manutencao e Instalacao de Aparelhos de Climatizacao e  Refrigeracao | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção F | Construção | 1,319 movimentos
622020 | Trabalhador Volante da Agricultura | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Alimentos e bebidas | 1,282 movimentos
142105 | Gerente Administrativo | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Construção | 1,279 movimentos
715405 | Operador de Betoneira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,278 movimentos
773415 | Operador de Maquina de Usinagem de Madeira (Producao em Serie) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 1,252 movimentos
848515 | Desossador | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 1,233 movimentos
252210 | Contador | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 1,202 movimentos
782515 | Motorista Operacional de Guincho | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,174 movimentos
410105 | Supervisor Administrativo | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Construção | 1,170 movimentos
773120 | Serrador de Madeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 1,167 movimentos
761354 | Operador de Maquina de Cordoalha | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 1,160 movimentos
724435 | Funileiro Industrial | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,158 movimentos
832125 | Operador de Maquina de Fabricar Papel e Papelao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Papel, celulose e gráfica | 1,149 movimentos
732120 | Instalador de Linhas Eletricas de Alta e Baixa - Tensao (Rede Aerea e Subterranea) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,143 movimentos
724210 | Montador de Estruturas Metalicas de Embarcacoes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,119 movimentos
715545 | Montador de Andaimes (Edificacoes) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,109 movimentos
513205 | Cozinheiro Geral | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 1,107 movimentos
716525 | Marmorista (Construcao) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Minerais não metálicos e cerâmica | 1,106 movimentos
314110 | Tecnico Mecanico | grande grupo 3 (Técnicos de nível médio) | seção C | Construção | 1,089 movimentos
300305 | Tecnico em Eletromecanica | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 1,074 movimentos
724115 | Instalador de Tubulacoes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,062 movimentos
716305 | Vidraceiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 1,058 movimentos
521105 | Vendedor em Comercio Atacadista | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 1,055 movimentos
862120 | Operador de Caldeira | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Madeira e móveis | 1,055 movimentos
766305 | Acabador de Embalagens (Flexiveis e Cartotecnicas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Papel, celulose e gráfica | 1,047 movimentos
519210 | Selecionador de Material Reciclável | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção E | Utilidades | 1,035 movimentos
414115 | Balanceiro | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 1,030 movimentos
811130 | Trabalhador de Fabricacao de Tintas | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Química e farmacêutica | 1,020 movimentos
763115 | Enfestador de Roupas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 1,016 movimentos
731170 | Bobinador Eletricista, À Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 1,014 movimentos
514120 | Zelador de Edificio | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Construção | 1,011 movimentos
782205 | Guincheiro (Construcao Civil) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 1,001 movimentos
841810 | Operador de Maquinas de Fabricacao de Doces, Salgados e Massas Alimenticias | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 1,001 movimentos
```

### Lote 04

```text
725015 | Ajustador Mecanico (Usinagem em Bancada e em Maquinas-Ferramentas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 996 movimentos
811760 | Moldador de Plastico por Compressao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 992 movimentos
311410 | Tecnico em Plastico | grande grupo 3 (Técnicos de nível médio) | seção C | Plástico e borracha | 991 movimentos
761230 | Operador de Filatorio | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 964 movimentos
823320 | Trabalhador da Elaboracao de Pre-Fabricados (Cimento Amianto) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Minerais não metálicos e cerâmica | 964 movimentos
715410 | Operador de Bomba de Concreto | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Minerais não metálicos e cerâmica | 960 movimentos
421125 | Operador de Caixa | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 939 movimentos
413115 | Auxiliar de Faturamento | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 921 movimentos
760310 | Encarregado de Costura na Confeccao do Vestuario | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 919 movimentos
813115 | Operador de Extrusora (Quimica, Petroquimica e Afins) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 910 movimentos
848525 | Retalhador de Carne | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 910 movimentos
313105 | Eletrotecnico | grande grupo 3 (Técnicos de nível médio) | seção C | Eletroeletrônica | 901 movimentos
763325 | Passadeira de Pecas Confeccionadas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 901 movimentos
914405 | Mecanico de Manutencao de Automoveis, Motocicletas e Veiculos Similares | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Metalmecânica | 894 movimentos
783210 | Carregador (Armazem) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Alimentos e bebidas | 882 movimentos
712205 | Cortador de Pedras | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Minerais não metálicos e cerâmica | 869 movimentos
848115 | Salsicheiro (Fabricacao de Linguica, Salsicha e Produtos Similares) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 865 movimentos
862305 | Operador de Estacao de Tratamento de Agua e Efluentes | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Utilidades | 865 movimentos
721325 | Polidor de Metais | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 863 movimentos
721410 | Operador de Fresadora com Comando Numerico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 863 movimentos
520110 | Supervisor de Vendas Comercial | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 859 movimentos
764115 | Preparador de Calcados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 857 movimentos
318610 | Desenhista Projetista Mecanico | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 856 movimentos
821245 | Operador de Area de Corrida | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 855 movimentos
301105 | Tecnico de Laboratorio Industrial | grande grupo 3 (Técnicos de nível médio) | seção C | Alimentos e bebidas | 854 movimentos
765405 | Trabalhador do Acabamento de Artefatos de Tecidos e Couros | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 850 movimentos
514215 | Varredor de Rua | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção E | Utilidades | 840 movimentos
262410 | Desenhista Industrial Grafico (Designer Grafico) | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Têxtil, confecção e calçados | 834 movimentos
811745 | Laminador de Plastico | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 818 movimentos
761810 | Revisor de Fios (Producao Textil) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 811 movimentos
764305 | Acabador de Calcados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 800 movimentos
828110 | Oleiro (Fabricacao de Tijolos) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Minerais não metálicos e cerâmica | 795 movimentos
731320 | Instalador-Reparador de Linhas e Aparelhos de Telecomunicacoes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 783 movimentos
142330 | Analista de Negocios (A) | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Têxtil, confecção e calçados | 780 movimentos
911320 | Mecanico de Manutencao de Maquinas Texteis | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Têxtil, confecção e calçados | 779 movimentos
252705 | Analista de Pcp (Programacao e Controle da Producao) | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 771 movimentos
848325 | Trabalhador de Fabricacao de Sorvete | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 767 movimentos
623310 | Trabalhador da Avicultura de Postura | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Alimentos e bebidas | 766 movimentos
721105 | Ferramenteiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 764 movimentos
313215 | Tecnico Eletronico | grande grupo 3 (Técnicos de nível médio) | seção C | Eletroeletrônica | 758 movimentos
761415 | Operador de Calandras (Tecidos) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 753 movimentos
840105 | Supervisor de Producao da Industria Alimenticia | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 753 movimentos
721225 | Preparador de Maquinas-Ferramenta | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 736 movimentos
354145 | Vendedor Pracista | grande grupo 3 (Técnicos de nível médio) | seção C | Alimentos e bebidas | 720 movimentos
732105 | Eletricista de Manutencao de Linhas Eletricas, Telefonicas e de Comunicacao de Dados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 707 movimentos
848210 | Queijeiro na Fabricacao de Laticinio | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 705 movimentos
715205 | Calceteiro | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 696 movimentos
516345 | Auxiliar de Lavanderia | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 694 movimentos
910105 | Encarregado de Manutencao Mecanica de Sistemas Operacionais | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Construção | 675 movimentos
411030 | Auxiliar de Pessoal | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Metalmecânica | 673 movimentos
```

### Lote 05

```text
911325 | Mecanico de Manutencao de Maquinas-Ferramentas (Usinagem de Metais) | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção F | Construção | 667 movimentos
314410 | Tecnico em Manutencao de Maquinas | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 659 movimentos
765235 | Estofador de Moveis | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 657 movimentos
782115 | Operador de Guindaste Movel | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 652 movimentos
766205 | Impressor (Serigrafia) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Papel, celulose e gráfica | 636 movimentos
761435 | Operador de Rameuse | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 634 movimentos
517420 | Vigia | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção F | Construção | 628 movimentos
318810 | Modelista de Roupas | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 624 movimentos
715140 | Operador de Pavimentadora (Asfalto, Concreto e Materiais Similares) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 624 movimentos
517410 | Porteiro de Edificios | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Construção | 619 movimentos
823210 | Extrusor de Fios ou Fibras de Vidro | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 615 movimentos
848510 | Acougueiro | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 613 movimentos
723215 | Galvanizador | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 610 movimentos
775115 | Lustrador de Pecas de Madeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 602 movimentos
761820 | Revisor de Tecidos Crus | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 601 movimentos
821440 | Operador de Tesoura Mecanica e Maquina de Corte, no Acabamento de Chapas e Metais | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 600 movimentos
782145 | Sinaleiro (Ponte-Rolante) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 599 movimentos
823125 | Preparador de Esmaltes (Ceramica) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Minerais não metálicos e cerâmica | 599 movimentos
724515 | Prensista (Operador de Prensa) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 598 movimentos
342125 | Tecnólogo em Logistica de Transporte | grande grupo 3 (Técnicos de nível médio) | seção C | Alimentos e bebidas | 594 movimentos
782305 | Motorista de Carro de Passeio | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 583 movimentos
414120 | Conferente Mercadoria (Exceto Carga e Descarga) | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Têxtil, confecção e calçados | 581 movimentos
142305 | Gerente Comercial | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Têxtil, confecção e calçados | 580 movimentos
766310 | Impressor de Corte e Vinco | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 578 movimentos
722320 | Moldador, a  Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 576 movimentos
214205 | Engenheiro Civil | grande grupo 2 (Profissionais das ciências e das artes) | seção F | Construção | 573 movimentos
262425 | Desenhista Industrial de Produto de Moda (Designer de Moda) | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Têxtil, confecção e calçados | 573 movimentos
313130 | Tecnico Eletricista | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 573 movimentos
761430 | Operador de Maquina de Lavar Fios e Tecidos | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 568 movimentos
252545 | Analista Financeiro (Instituicoes Financeiras) | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 566 movimentos
318205 | Desenhista Tecnico Mecanico | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 559 movimentos
715135 | Operador de Pa Carregadeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Construção | 558 movimentos
715705 | Aplicador de Asfalto Impermeabilizante (Coberturas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 556 movimentos
725705 | Mecanico de Refrigeracao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 554 movimentos
317110 | Programador de Sistemas de Informacao | grande grupo 3 (Técnicos de nível médio) | seção C | Eletroeletrônica | 549 movimentos
632125 | Trabalhador de Extracao Florestal, em Geral | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Madeira e móveis | 546 movimentos
818105 | Assistente de Laboratorio Industrial | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 532 movimentos
723310 | Pintor a Pincel e Rolo (Exceto Obras e Estruturas Metalicas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 528 movimentos
773340 | Operador de Serras (Usinagem de Madeira) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 528 movimentos
731150 | Montador de Equipamentos Eletronicos | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 527 movimentos
811750 | Moldador de Borracha por Compressao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 526 movimentos
770105 | Mestre (Industria de Madeira e Mobiliario) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 519 movimentos
524105 | Vendedor em Domicilio | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Construção | 517 movimentos
314115 | Tecnico Mecanico (Calefacao, Ventilacao e Refrigeracao) | grande grupo 3 (Técnicos de nível médio) | seção F | Construção | 504 movimentos
773110 | Operador de Serras no Desdobramento de Madeira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 498 movimentos
313115 | Eletrotenico na Fabricacao, Montagem e Instalacao de Maquinas e Equipamentos | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 492 movimentos
313120 | Tecnico de Manutencao Eletrica | grande grupo 3 (Técnicos de nível médio) | seção C | Construção | 489 movimentos
142320 | Gerente de Vendas | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Têxtil, confecção e calçados | 486 movimentos
313310 | Tecnico de Rede (Telecomunicacoes) | grande grupo 3 (Técnicos de nível médio) | seção F | Construção | 484 movimentos
318510 | Desenhista Projetista de Construcao Civil | grande grupo 3 (Técnicos de nível médio) | seção F | Construção | 483 movimentos
```

### Lote 06

```text
516330 | Tingidor de Roupas | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 483 movimentos
252305 | Secretaria  Executiva | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Construção | 481 movimentos
722330 | Operador de Maquina de Moldar Automatizada | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 479 movimentos
212405 | Analista de Desenvolvimento de Sistemas | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 477 movimentos
848315 | Masseiro (Massas Alimenticias) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 476 movimentos
821305 | Operador de Laminador | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 475 movimentos
515225 | Auxiliar de Producao Farmaceutica | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Química e farmacêutica | 471 movimentos
818110 | Auxiliar de Laboratorio de Analises Fisico-Quimicas | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Química e farmacêutica | 469 movimentos
722315 | Moldador, a  Mao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 460 movimentos
764120 | Preparador de Solas e Palmilhas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 455 movimentos
732130 | Instalador-Reparador de Redes Telefonicas e de Comunicacao de Dados | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 454 movimentos
622010 | Jardineiro | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção F | Construção | 447 movimentos
833205 | Cartonageiro, a Mao (Caixas de Papelao) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Papel, celulose e gráfica | 444 movimentos
833120 | Operador de Maquina de Cortar e Dobrar Papelao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Papel, celulose e gráfica | 441 movimentos
311715 | Preparador de Tintas | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 439 movimentos
766235 | Impressor Flexografico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Plástico e borracha | 439 movimentos
711230 | Operador de Maquina Perfuratriz | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 435 movimentos
782130 | Operador de Ponte Rolante | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 432 movimentos
841408 | Cozinhador (Conservacao de Alimentos) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 430 movimentos
318805 | Projetista de Moveis | grande grupo 3 (Técnicos de nível médio) | seção C | Madeira e móveis | 426 movimentos
722220 | Operador de Maquina Centrifugadora de Fundicao | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 425 movimentos
391115 | Controlador de Entrada e Saida | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 423 movimentos
752330 | Ceramista Prensador | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Minerais não metálicos e cerâmica | 419 movimentos
317210 | Tecnico de Apoio ao Usuario de Informatica (Helpdesk) | grande grupo 3 (Técnicos de nível médio) | seção C | Eletroeletrônica | 416 movimentos
722310 | Macheiro, a  Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 405 movimentos
311720 | Preparador de Tintas (Fabrica de Tecidos) | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 403 movimentos
841468 | Preparador de Racoes | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 402 movimentos
252715 | Analista de Logistica | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 400 movimentos
395105 | Tecnico de Apoio em Pesquisa e Desenvolvimento (Exceto Agropecuario e Florestal) | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 400 movimentos
391105 | Cronoanalista | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 393 movimentos
761205 | Operador de Abertura (Fiacao) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 391 movimentos
521125 | Repositor de Mercadorias | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 388 movimentos
318605 | Desenhista Projetista de Maquinas | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 386 movimentos
141305 | Gerente de Producao e Operacoes da Construcao Civil e Obras Publicas | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção F | Construção | 384 movimentos
354135 | Tecnico de Vendas | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 383 movimentos
810205 | Mestre (Industria de Borracha e Plastico) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 382 movimentos
516415 | Passador de Roupas, À Mao | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 377 movimentos
354140 | Tecnico em Atendimento e Vendas | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 374 movimentos
731125 | Montador de Equipamentos Eletricos (Centrais Eletricas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 374 movimentos
773220 | Preparador de Aglomerantes | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Madeira e móveis | 374 movimentos
763015 | Costureira de Reparacao de Roupas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 373 movimentos
832135 | Operador de Rebobinadeira na Fabricacao de Papel e Papelao | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Papel, celulose e gráfica | 373 movimentos
761339 | Tecelao de Meias (Maquina Circular) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 372 movimentos
764205 | Costurador de Calcados, a  Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 372 movimentos
731155 | Montador de Equipamentos Eletricos (Elevadores e Equipamentos Similares) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 371 movimentos
919315 | Montador de Bicicletas | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Metalmecânica | 371 movimentos
821435 | Operador de Jato Abrasivo | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 368 movimentos
712120 | Operador de Britador de Mandibulas | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção B | Extrativa | 365 movimentos
760105 | Contramestre de Acabamento (Industria Textil) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 363 movimentos
354120 | Agente de Vendas de Servicos | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 362 movimentos
```

### Lote 07

```text
414205 | Apontador de Mao-De-Obra | grande grupo 4 (Trabalhadores de serviços administrativos) | seção F | Construção | 359 movimentos
821405 | Encarregado de Acabamento de Chapas e Metais  (Tempera) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 357 movimentos
821415 | Marcador de Produtos (Siderurgico e Metalurgico) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Metalmecânica | 357 movimentos
821445 | Preparador de Sucata e Aparas | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção E | Utilidades | 356 movimentos
841456 | Operador de Camaras Frias | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Alimentos e bebidas | 354 movimentos
828105 | Oleiro (Fabricacao de Telhas) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Minerais não metálicos e cerâmica | 348 movimentos
766225 | Impressor de Rotogravura | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Plástico e borracha | 347 movimentos
516305 | Lavadeiro, em Geral | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 342 movimentos
632120 | Operador de Motosserra | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Madeira e móveis | 342 movimentos
513405 | Garcom | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Alimentos e bebidas | 339 movimentos
833105 | Cartonageiro, a Maquina | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Papel, celulose e gráfica | 338 movimentos
641010 | Operador de Maquinas de Beneficiamento de Produtos Agricolas | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Alimentos e bebidas | 333 movimentos
516310 | Lavador de Roupas  a Maquina | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 332 movimentos
300105 | Tecnico em Mecatronica - Automacao da Manufatura | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 331 movimentos
391130 | Tecnico de Planejamento e Programacao da Manutencao | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 331 movimentos
318415 | Desenhista Tecnico (Ilustracoes Tecnicas) | grande grupo 3 (Técnicos de nível médio) | seção C | Têxtil, confecção e calçados | 329 movimentos
731160 | Montador de Equipamentos Eletricos (Transformadores) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Eletroeletrônica | 329 movimentos
251215 | Economista Financeiro | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Construção | 328 movimentos
992115 | Borracheiro | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Plástico e borracha | 327 movimentos
311105 | Tecnico Quimico | grande grupo 3 (Técnicos de nível médio) | seção C | Química e farmacêutica | 325 movimentos
715110 | Operador de Compactadora de Solos | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 323 movimentos
410205 | Supervisor de Almoxarifado | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Metalmecânica | 321 movimentos
784115 | Operador de Maquina de Etiquetar | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 321 movimentos
142705 | Gerente de Projetos e Servicos de Manutencao | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Metalmecânica | 318 movimentos
318005 | Desenhista Tecnico | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 318 movimentos
712220 | Polidor de Pedras | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 317 movimentos
722325 | Operador de Equipamentos de Preparacao de Areia | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 316 movimentos
732110 | Emendador de Cabos Eletricos e Telefonicos (Aereos e Subterraneos) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 315 movimentos
322420 | Auxiliar de Protese Dentaria | grande grupo 3 (Técnicos de nível médio) | seção C | Outras da transformação | 311 movimentos
631210 | Pescador Profissional | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Alimentos e bebidas | 311 movimentos
724325 | Soldador Eletrico | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 310 movimentos
142205 | Gerente de Recursos Humanos | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Metalmecânica | 304 movimentos
354130 | Promotor de Vendas Especializado | grande grupo 3 (Técnicos de nível médio) | seção C | Plástico e borracha | 304 movimentos
313205 | Tecnico de Manutencao Eletronica | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 303 movimentos
314120 | Tecnico Mecanico (Maquinas) | grande grupo 3 (Técnicos de nível médio) | seção C | Metalmecânica | 303 movimentos
516325 | Passador de Roupas em Geral | grande grupo 5 (Trabalhadores dos serviços, vendedores do comércio) | seção C | Têxtil, confecção e calçados | 300 movimentos
914425 | Mecanico de Veiculos Automotores a Diesel (Exceto Tratores) | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção C | Metalmecânica | 299 movimentos
318505 | Desenhista Projetista de Arquitetura | grande grupo 3 (Técnicos de nível médio) | seção C | Construção | 298 movimentos
715130 | Operador de Motoniveladora | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 298 movimentos
142115 | Gerente Financeiro | grande grupo 1 (Membros superiores do poder público, dirigentes de organizações e gerentes) | seção C | Construção | 293 movimentos
312320 | Topografo | grande grupo 3 (Técnicos de nível médio) | seção F | Construção | 293 movimentos
722230 | Operador de Vazamento (Lingotamento) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 293 movimentos
761250 | Operador de Passador (Fiacao) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 292 movimentos
715725 | Instalador de Material Isolante, a Mao (Edificacoes) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 290 movimentos
724310 | Oxicortador a Mao e a  Maquina | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Metalmecânica | 289 movimentos
951305 | Instalador de Sistemas Eletroeletronicos de Seguranca | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção F | Construção | 287 movimentos
212420 | Analista de Suporte Computacional | grande grupo 2 (Profissionais das ciências e das artes) | seção C | Metalmecânica | 284 movimentos
761225 | Operador de Conicaleira | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção C | Têxtil, confecção e calçados | 284 movimentos
954105 | Eletromecanico de Manutencao de Elevadores | grande grupo 9 (Trabalhadores em serviços de reparação e manutenção) | seção F | Construção | 284 movimentos
813120 | Operador de Processo (Quimica, Petroquimica e Afins) | grande grupo 8 (Trabalhadores da produção de bens e serviços industriais (sistemas contínuos)) | seção C | Plástico e borracha | 283 movimentos
```

### Lote 08

```text
621005 | Trabalhador Agropecuario em Geral | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção F | Construção | 279 movimentos
410240 | Supervisor de Logistica | grande grupo 4 (Trabalhadores de serviços administrativos) | seção C | Alimentos e bebidas | 276 movimentos
642015 | Operador de Trator Florestal | grande grupo 6 (Trabalhadores agropecuários, florestais e da pesca) | seção C | Madeira e móveis | 276 movimentos
711320 | Sondador de Pocos (Exceto de Petroleo e Gas) | grande grupo 7 (Trabalhadores da produção de bens e serviços industriais (sistemas discretos)) | seção F | Construção | 276 movimentos
```
