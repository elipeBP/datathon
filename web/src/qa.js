// Banco de perguntas e respostas prontas (do design), por capítulo.
// Servidas na hora, sem chamar a IA. Usado pelo site e pela função /api/perguntar.
// Toda resposta cita a fonte. Os números foram conferidos contra web/api/_base.js
// (o mesmo verificador de aterramento do assistente).

const SINAL = "var(--sinal)", EXP = "var(--expansao)", NEUTRO = "var(--neutro)", CLARO = "var(--neutro-claro)";
const FONTE = "Novo CAGED (MTE), indústria de transformação, SC, set/2025 a ago/2026.";

export const CAPITULOS = [
  { id: "tese", n: 1, nome: "Tese", titulo: "A tese", contexto: "Capítulo 1, tese" },
  { id: "onde", n: 2, nome: "Onde", titulo: "Onde a indústria perde gente", contexto: "Capítulo 2, mapa" },
  { id: "setores", n: 3, nome: "Setores", titulo: "Setor por setor", contexto: "Capítulo 3, setores" },
  { id: "porque", n: 4, nome: "Por quê", titulo: "Por que saem", contexto: "Capítulo 4, por quê" },
  { id: "oque", n: 5, nome: "O que fazer", titulo: "O que fazer", contexto: "Capítulo 5, recomendações" },
  { id: "metodo", n: 6, nome: "Método", titulo: "Como medimos", contexto: "Capítulo 6, método" },
];

export const QA = {
  tese: [
    { id: "tese-1", q: "O que significa 50,9% a pedido?",
      a: "De cada 100 desligamentos na indústria de transformação de Santa Catarina em 12 meses, 51 foram pedidos pelo próprio trabalhador. Foram 417.429 desligamentos no período. Quando a maioria das saídas é voluntária, o desafio principal é segurar quem já está empregado, não encontrar gente nova.",
      src: FONTE },
    { id: "tese-2", q: "Se há tanta rotatividade, por que o saldo é positivo?",
      a: "Porque as contratações quase empatam com as saídas. Em 835.866 movimentações, o saldo foi de apenas +1.008 vagas, o equivalente a 0,12% do giro. O setor contrata e perde gente em volume parecido: gira muito e quase não cresce.",
      src: "Novo CAGED (MTE), saldo e movimentações da transformação em SC, 12 meses." },
    { id: "tese-3", q: "A falta de qualificação explica as saídas?",
      a: "Os dados indicam que não. Quem entra tem praticamente a mesma escolaridade de quem sai: comparando na mesma ocupação e região, a diferença no ensino superior é de −0,02 ponto percentual, e o ensino médio fica em 69,8% e 70,0%. O que muda é o salário: quem entra ganha 2,5% menos na mesma ocupação e região.",
      src: "Novo CAGED (MTE), escolaridade e salário de admitidos e desligados, mesma ocupação e microrregião.",
      chartTitle: "Ensino médio: quem entra × quem sai",
      bars: [{ l: "Quem entra", v: "69,8%", w: 69.8, c: NEUTRO }, { l: "Quem sai", v: "70,0%", w: 70, c: NEUTRO }] },
  ],
  onde: [
    { id: "onde-1", q: "Por que o Oeste perde gente se está crescendo?",
      a: "Porque a indústria do Oeste contrata muito, mas não segura quem contrata. Chapecó tem o maior saldo de SC (+49,1 por 10 mil habitantes) e, mesmo assim, 55,1% das saídas são a pedido, acima da média de 50,9%. Concórdia (62,6%) e São Miguel do Oeste (67,0%) seguem o mesmo padrão: abrir vagas não basta se o trabalhador sai logo depois.",
      src: "Novo CAGED (MTE), microrregiões do Oeste, indústria de transformação, set/2025 a ago/2026.",
      chartTitle: "% dos desligamentos a pedido",
      bars: [{ l: "São Miguel do Oeste", v: "67,0%", w: 95.7, c: SINAL }, { l: "Concórdia", v: "62,6%", w: 89.4, c: SINAL },
        { l: "Chapecó", v: "55,1%", w: 78.7, c: SINAL }, { l: "Média de SC", v: "50,9%", w: 72.7, c: NEUTRO }] },
    { id: "onde-2", q: "Qual região mais encolhe?",
      a: "São Bento do Sul, com saldo de −77,8 empregos industriais por 10 mil habitantes, de longe o pior resultado do estado. Lá, 55,4% das saídas são a pedido. Blumenau (−29,7) e Rio do Sul (−29,4) vêm em seguida, ambas no Vale do Itajaí.",
      src: "Novo CAGED (MTE), saldo por 10 mil habitantes, indústria de transformação, 12 meses.",
      chartTitle: "Saldo por 10 mil habitantes (negativo)",
      bars: [{ l: "São Bento do Sul", v: "−77,8", w: 97.3, c: SINAL }, { l: "Blumenau", v: "−29,7", w: 37.1, c: SINAL }, { l: "Rio do Sul", v: "−29,4", w: 36.8, c: SINAL }] },
    { id: "onde-3", q: "Onde a indústria retém melhor?",
      a: "Florianópolis tem a menor taxa de saídas a pedido do estado (38,7%), seguida de Campos de Lages (43,5%) e Tijucas (43,7%). Das três, só Campos de Lages também cresce (+13,1 por 10 mil habitantes).",
      src: "Novo CAGED (MTE), microrregiões de SC, indústria de transformação, 12 meses.",
      chartTitle: "% dos desligamentos a pedido",
      bars: [{ l: "Florianópolis", v: "38,7%", w: 55.3, c: NEUTRO }, { l: "Campos de Lages", v: "43,5%", w: 62.1, c: NEUTRO },
        { l: "Tijucas", v: "43,7%", w: 62.4, c: NEUTRO }, { l: "Média de SC", v: "50,9%", w: 72.7, c: CLARO }] },
  ],
  setores: [
    { id: "setores-1", q: "Por que alimentos perde gente se cresce?",
      a: "Alimentos e bebidas tem o maior saldo entre os setores (+4.731 vagas em 12 meses) e, ao mesmo tempo, a maior taxa de saídas a pedido: 56,2%, contra 50,9% na média de SC. Quem entra ganha R$ 2.100 e quem sai ganhava R$ 2.164 (−3,0%). O setor contrata muito, mas a reposição paga menos e não segura o trabalhador.",
      src: "Novo CAGED (MTE), setores da transformação, SC, set/2025 a ago/2026.",
      chartTitle: "% dos desligamentos a pedido",
      bars: [{ l: "Alimentos", v: "56,2%", w: 80.3, c: SINAL }, { l: "Madeira", v: "53,1%", w: 75.9, c: SINAL },
        { l: "Têxtil", v: "52,4%", w: 74.9, c: SINAL }, { l: "Média de SC", v: "50,9%", w: 72.7, c: NEUTRO }] },
    { id: "setores-2", q: "Qual setor mais encolhe?",
      a: "Têxtil, confecção e calçados: saldo de −5.916 vagas em 12 meses, com 52,4% das saídas a pedido. Madeira e móveis vem em seguida (−2.710) e minerais e cerâmica (−842). Os três têm saldo negativo; têxtil e madeira também perdem mais gente que a média.",
      src: "Novo CAGED (MTE), saldo por setor, 12 meses.",
      chartTitle: "Saldo em 12 meses (negativo)",
      bars: [{ l: "Têxtil", v: "−5.916", w: 98.6, c: SINAL }, { l: "Madeira", v: "−2.710", w: 45.2, c: SINAL }, { l: "Cerâmica", v: "−842", w: 14, c: SINAL }] },
    { id: "setores-3", q: "O que o alimentador de linha muda na leitura do saldo?",
      a: "Uma única ocupação, o alimentador de linha de produção, responde por 24% de todas as movimentações. Ela sustenta o saldo positivo: com ela, a transformação fecha em +1.008 vagas; sem ela, o saldo seria −14.655.",
      src: "Novo CAGED (MTE), movimentações por ocupação (CBO), transformação, SC.",
      chartTitle: "Saldo em 12 meses",
      bars: [{ l: "Com a ocupação", v: "+1.008", w: 6.9, c: EXP }, { l: "Sem a ocupação", v: "−14.655", w: 100, c: SINAL }] },
  ],
  porque: [
    { id: "porque-1", q: "Qual setor tem a maior diferença salarial?",
      a: "Eletroeletrônica: quem entra ganha R$ 2.268 e quem sai ganhava R$ 2.407, uma diferença de −5,8%. Papel e gráfica (−5,7%), minerais e cerâmica (−5,6%) e metalmecânica (−5,6%) vêm logo atrás. A menor diferença é em plástico e borracha (−2,0%). Em nenhum setor quem entra ganha mais.",
      src: "Novo CAGED (MTE), salário mediano de admitidos e desligados por setor, SC, 12 meses.",
      chartTitle: "Quem entra ganha menos (%)",
      bars: [{ l: "Eletroeletrônica", v: "−5,8%", w: 100, c: SINAL }, { l: "Papel e gráfica", v: "−5,7%", w: 98, c: SINAL },
        { l: "Metalmecânica", v: "−5,6%", w: 96.5, c: SINAL }, { l: "Plástico", v: "−2,0%", w: 34.5, c: SINAL }] },
    { id: "porque-2", q: "Como a IA classificou as ocupações?",
      a: "Cada uma das 354 ocupações (CBO) que cobrem 95% das movimentações foi classificada pelo Gemini em uma de 15 áreas e um de 4 níveis de formação. A IA só podia escolher categorias de uma lista fechada, e as classificações passaram por revisão humana. Isso permite comparar famílias de ofícios, como “alimentos e bebidas acima de 200h”, que tem 62,8% de saídas a pedido.",
      src: "Metodologia do Raio-X; ocupações do Novo CAGED (MTE)." },
    { id: "porque-3", q: "Então formar mais gente não resolve?",
      a: "Formação sozinha não ataca o que os dados mostram. Quem entra tem a mesma escolaridade de quem sai (−0,02 p.p. de diferença no ensino superior, na mesma ocupação e região; 69,8% e 70,0% com ensino médio). O que difere entre os dois grupos é o salário: quem entra ganha 2,5% menos na mesma ocupação e região. A prioridade é reter quem já está na fábrica.",
      src: "Novo CAGED (MTE), escolaridade e salário de admitidos e desligados.",
      chartTitle: "Ensino médio",
      bars: [{ l: "Quem entra", v: "69,8%", w: 69.8, c: NEUTRO }, { l: "Quem sai", v: "70,0%", w: 70, c: CLARO }] },
  ],
  oque: [
    { id: "oque-1", q: "Por que começar pelo Oeste?",
      a: "Porque é onde a perda de gente é maior num setor que ainda cresce. Nos ofícios da agroindústria do Oeste, 64,6% das saídas são a pedido, contra 50,9% na média de SC, e o setor abriu +2.699 vagas. Reter quem já foi contratado tem efeito direto: cada saída evitada é uma vaga que não precisa ser reposta.",
      src: "Novo CAGED (MTE), ofícios da agroindústria nas microrregiões do Oeste, 12 meses.",
      chartTitle: "% dos desligamentos a pedido",
      bars: [{ l: "Agroindústria, Oeste", v: "64,6%", w: 92.3, c: SINAL }, { l: "Média de SC", v: "50,9%", w: 72.7, c: NEUTRO }] },
    { id: "oque-2", q: "Por que mexer no salário do têxtil?",
      a: "Em Rio do Sul, 68,6% das saídas do têxtil são a pedido e a reposição paga 4,3% menos que o salário de quem sai. Num setor que encolhe, a empresa perde gente experiente e contrata por menos, o que pode alimentar novas saídas. Rever a faixa salarial ataca essa diferença.",
      src: "Novo CAGED (MTE), têxtil em Rio do Sul, salário de admitidos e desligados, 12 meses.",
      chartTitle: "% dos desligamentos a pedido",
      bars: [{ l: "Têxtil, Rio do Sul", v: "68,6%", w: 98, c: SINAL }, { l: "Média de SC", v: "50,9%", w: 72.7, c: NEUTRO }] },
    { id: "oque-3", q: "Por que requalificar em Blumenau?",
      a: "Na mesma região, o têxtil perdeu 1.283 vagas e a eletroeletrônica criou 568. Há gente saindo de um setor e vagas abrindo em outro. Requalificar para eletroeletrônica e automação aproveita essa troca. A linha de base para acompanhar é +189 vagas na eletroeletrônica.",
      src: "Novo CAGED (MTE), saldo por setor em Blumenau, 12 meses.",
      chartTitle: "Saldo em 12 meses, Blumenau",
      bars: [{ l: "Têxtil", v: "−1.283", w: 100, c: SINAL }, { l: "Eletroeletrônica", v: "+568", w: 44.3, c: EXP }] },
    { id: "oque-4", q: "Como acompanhar se está funcionando?",
      a: "Cada recomendação tem uma linha de base reapurável todo mês no Novo CAGED: 64,6% de saídas a pedido na agroindústria do Oeste (meta: cair), 68,6% no têxtil de Rio do Sul (meta: cair) e +189 vagas na eletroeletrônica de Blumenau (meta: subir).",
      src: "Linhas de base do Raio-X, calculadas no Novo CAGED (MTE)." },
  ],
  metodo: [
    { id: "metodo-1", q: "Quão confiáveis são estes números?",
      a: "O saldo da transformação calculado pelo Raio-X para jan–mai/2026 difere 0,01% do boletim oficial da FIESC para o mesmo período, o que indica que a base foi tratada corretamente. Além disso, os resultados passaram por 7 testes de robustez; o que não passou está listado nesta página, com a explicação.",
      src: "Comparação com o boletim da FIESC; metodologia do Raio-X." },
    { id: "metodo-2", q: "De onde vêm os dados?",
      a: "Dos microdados do Novo CAGED, publicados pelo Ministério do Trabalho e Emprego. O recorte é a indústria de transformação de Santa Catarina, de setembro de 2025 a agosto de 2026: 835.866 movimentações e 417.429 desligamentos.",
      src: "Novo CAGED (MTE)." },
    { id: "metodo-3", q: "Como a IA foi usada no estudo?",
      a: "Para agrupar ocupações e para responder perguntas neste site. O Gemini classificou 354 ocupações em 15 áreas e 4 níveis de formação, escolhendo apenas entre categorias de uma lista fechada, com revisão humana. Os números em si vêm direto do CAGED, sem passar pela IA.",
      src: "Metodologia do Raio-X." },
  ],
};

export const TODAS = Object.values(QA).flat();

// ---------------------------------------------------------------- respostas geradas a partir dos dados (sem IA)
const f1 = (v) => v.toFixed(1).replace(".", ",");
const mil = (v) => Math.round(Math.abs(v)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
const sg1 = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + f1(Math.abs(v));
const sgI = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + mil(v);

/** Resposta da ficha de uma microrregião (dados do dados.json). */
export function qaRegiao(m, mediaSC) {
  const acima = m.kpi1 > mediaSC, cresce = m.kpi2 > 0;
  return {
    id: `regiao-${m.cod}`, q: `O que os dados mostram sobre ${m.nome}?`,
    a: `Em ${m.nome} (${m.meso}), ${f1(m.kpi1)}% dos desligamentos da indústria de transformação foram a pedido do trabalhador, ` +
      `${acima ? "acima" : "abaixo"} da média de SC (${f1(mediaSC)}%). O saldo foi de ${sgI(m.saldo)} vagas em 12 meses ` +
      `(${sg1(m.kpi2)} por 10 mil habitantes), em ${mil(m.movimentos)} movimentações. ` +
      `Leitura: ${acima ? "perde mais gente que a média" : "perde menos gente que a média"} e a indústria ${cresce ? "cresce" : "encolhe"}.`,
    src: `Novo CAGED (MTE), microrregião de ${m.nome}, indústria de transformação, 12 meses.`,
    chartTitle: "% dos desligamentos a pedido",
    bars: [{ l: m.nome, v: `${f1(m.kpi1)}%`, w: (m.kpi1 / 70) * 100, c: acima ? SINAL : NEUTRO },
      { l: "Média de SC", v: `${f1(mediaSC)}%`, w: (mediaSC / 70) * 100, c: CLARO }],
  };
}

/** Resposta do cartão de um setor (dados do dados.json). */
export function qaSetor(g, sal, mediaSC, curto) {
  const acima = g.kpi1 > mediaSC, cresce = g.saldo > 0;
  const quad = cresce ? (acima ? "Cresce e perde gente" : "Cresce e retém") : (acima ? "Não cresce e perde gente" : "Estagnado");
  const gap = sal ? (sal.admitidos / sal.desligados - 1) * 100 : null;
  return {
    id: `setor-${g.grupo}`, q: `Como ler o quadrante de ${curto}?`,
    a: `${g.grupo}: ${f1(g.kpi1)}% das saídas são a pedido (${g.kpi1 >= mediaSC ? "+" : "−"}${f1(Math.abs(g.kpi1 - mediaSC))} p.p. em relação à média de ${f1(mediaSC)}%) ` +
      `e o saldo foi de ${sgI(g.saldo)} vagas em 12 meses. Por isso o setor cai em “${quad}”.` +
      (sal ? ` Quem entra ganha ${f1(Math.abs(gap))}% menos que quem sai (R$ ${mil(sal.admitidos)} contra R$ ${mil(sal.desligados)}).` : ""),
    src: `Novo CAGED (MTE), ${g.grupo.toLowerCase()}, SC, set/2025 a ago/2026.`,
  };
}
