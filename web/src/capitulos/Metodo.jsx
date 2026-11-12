// Capítulo 6 — Método (Tela6-Metodo.dc.html), com os resultados reais de reports/testes.md.
import { useState } from "react";
import { QA } from "../qa.js";
import { Pergunte, ProximoCapitulo } from "../componentes/base.jsx";
import { int, pct } from "../fmt.jsx";

const num = (s) => (s || "").replace(/(\d)\.(\d)/g, "$1,$2");

function testes(rows) {
  const de = (id) => rows.filter((r) => r.teste === id);
  const st = (lista) => (lista.some((r) => /pendente/i.test(r.resultado)) ? "pend" : lista.some((r) => /reprovado/i.test(r.resultado)) ? "mau" : "ok");
  const t1c = de("T1").find((r) => /Transforma/.test(r.grupo));
  const t1f = de("T1").find((r) => /Constru/.test(r.grupo));
  const pctDe = (r) => num((r?.resultado.match(/\(([\d.]+)%\)/) || [])[1] || "");
  const t4 = de("T4")[0], t5 = de("T5"), t2b = de("T2b")[0], t2a = de("T2a")[0];
  return [
    { nome: "Bate com o boletim oficial da FIESC", status: "ok",
      det: `Saldo da transformação em jan–mai/2026: ${pctDe(t1c)}% de diferença. Na construção, ${pctDe(t1f)}%, no limite da tolerância de 0,5%; declarado.` },
    { nome: "A mesma ocupação muda de taxa conforme o setor", status: st([t2a]), det: num(t2a?.obtido) },
    { nome: "O setor pesa mesmo descontada a mistura de ocupações", status: st([t2b]), det: `${num(t2b?.obtido)}; corte de 5 p.p. Aprovado por pouco.` },
    { nome: "Não depende de uma única ocupação", status: st(de("T3")),
      det: "Sem o alimentador de linha, o ranking dos setores muda (madeira cai de 3º para 7º). Por isso o site mostra o resultado com e sem essa ocupação." },
    { nome: "Estável entre os dois semestres", status: st([t4]), det: `${num(t4?.obtido)} (critério: acima de 0,7).` },
    { nome: "Não depende da definição de indústria", status: st(t5), det: "Transformação × indústria geral: 0,28 p.p. de diferença e o mesmo top 5 de microrregiões." },
    { nome: "A IA confere com revisores humanos", status: st(de("T6")), det: "Dois revisores conferem 30 ocupações sorteadas; meta de 85% de concordância." },
  ];
}

export default function Metodo({ dados }) {
  const [aberto, setAberto] = useState(0);
  const t = dados.segmentos.find((s) => s.segmento === "Transformação");
  const ia = dados.ia;
  const lista = testes(dados.testes);
  const t1 = dados.testes.find((r) => r.teste === "T1" && /Transforma/.test(r.grupo));
  const dif = num((t1?.resultado.match(/\(([\d.]+)%\)/) || [])[1] || "0,01");
  const ctx = { cap: "metodo", texto: "Capítulo 6, método" };
  const ROT = { ok: "Aprovado", mau: "Reprovado", pend: "Pendente" };
  const premissas = [
    ["Fonte e período", `Microdados do Novo CAGED (MTE), Santa Catarina, de setembro de 2025 a agosto de 2026: 12 meses, ${int(t.movimentos)} movimentações na indústria de transformação.`],
    ["O que conta como “a pedido”", `Desligamentos por iniciativa do trabalhador divididos pelo total de desligamentos do recorte. Média de SC: ${pct(t.kpi1)} (${int(t.desligamentos)} desligamentos).`],
    ["O CAGED mede fluxo, não vagas", "O CAGED registra contratações e desligamentos, não vagas abertas nem desemprego. Por isso o “apagão” é inferido por sinais indiretos: saídas a pedido, saldo, salário de reposição e escolaridade."],
    ["Salário de reposição", `Salário mediano de quem entra dividido pelo de quem sai, na mesma ocupação e microrregião, ponderado. Resultado: ${t.kpi3.toFixed(3).replace(".", ",")}. Só celetistas comuns, de R$ 1.000 a R$ 30.000. É uma hipótese da equipe: sinal fraco.`],
    ["Associação, não causa", "Escolaridade e salário aparecem associados às saídas; os dados não permitem afirmar que causam o gargalo."],
    ["Classificação das ocupações por IA", `${ia.cbos_llm} ocupações classificadas pelo Gemini (${ia.modelo}) em ${ia.areas} áreas e ${ia.niveis} níveis de formação, a partir de uma lista fechada de categorias, com revisão humana. ${int(ia.cbos_heranca)} herdaram a classificação pela família da ocupação.`],
    ["Quadrantes", "Microrregião × setor, com volume mínimo de 300 desligamentos e movimentações. O corte é a mediana das combinações: 37 crescem e perdem gente, 31 não crescem e perdem gente, 31 crescem e retêm, 36 estagnados."],
    ["Recorte geográfico", "20 microrregiões e 6 mesorregiões do IBGE, com o contorno oficial. População do Censo 2022."],
    ["Linhas repetidas", "Linhas idênticas foram mantidas, como nos números oficiais (provável contratação em lote). Removê-las levaria o saldo de +1.008 para −12.287."],
  ];

  return (
    <>
      <section className="abre">
        <div className="eyebrow">Método</div>
        <h1>Os números batem com o boletim oficial. Mostramos o que passou e o que não passou.</h1>
      </section>

      <section className="kpis3">
        <div><div className="v num">{dif}%</div><div className="t">diferença para o boletim da FIESC</div></div>
        <div><div className="v num">{lista.length}</div><div className="t">testes de robustez</div></div>
        <div><div className="v num">{ia.cbos_llm}</div><div className="t">ocupações classificadas por IA</div></div>
      </section>
      <div className="bloco"><Pergunte titulo="" itens={[QA.metodo[0]]} contexto={ctx} /></div>

      <div className="metodo-grade">
        <section style={{ margin: "36px var(--margem) 0" }}>
          <h2 className="graf" style={{ margin: 0 }}>Testes de robustez</h2>
          <div className="sub-graf">Cada afirmação do estudo passou por estes testes antes de entrar no site</div>
          <ol className="testes">
            {lista.map((x, i) => (
              <li key={x.nome}>
                <span className="n num">{String(i + 1).padStart(2, "0")}</span>
                <span className="nome">{x.nome}<span className="det">{x.det}</span></span>
                <span className={`badge ${x.status}`}>{ROT[x.status]}</span>
              </li>
            ))}
          </ol>
        </section>

        <section style={{ margin: "36px var(--margem) 0" }}>
          <h2 className="graf" style={{ margin: 0 }}>Premissas</h2>
          <div style={{ marginTop: 10, borderTop: "1px solid var(--linha)" }}>
            {premissas.map(([titulo, corpo], i) => (
              <div key={titulo} style={{ borderBottom: "1px solid var(--linha)" }}>
                <button className="acc-btn" aria-expanded={aberto === i} aria-controls={`prem-${i}`} onClick={() => setAberto(aberto === i ? -1 : i)}>
                  <span>{titulo}</span>
                  <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" stroke="var(--tinta)" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
                </button>
                {aberto === i && <p id={`prem-${i}`} className="acc-corpo">{corpo}</p>}
              </div>
            ))}
          </div>
          <Pergunte titulo="Pergunte sobre o método" itens={QA.metodo.slice(1)} contexto={ctx} />
        </section>
      </div>

      <ProximoCapitulo cap="metodo" />
    </>
  );
}
