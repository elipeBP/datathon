import { useEffect, useState } from "react";
import Mapa from "./componentes/Mapa.jsx";
import Setores from "./componentes/Setores.jsx";
import Quadrantes from "./componentes/Quadrantes.jsx";
import { Escolaridade, Macrofamilias, Salario } from "./componentes/PorQue.jsx";
import { dec, int, pct, sinal, sinalInt } from "./fmt.jsx";

const PREMISSAS = [
  "O CAGED mede fluxo (admissões e desligamentos), não estoque nem vagas abertas. \"Apagão\" é inferido por sinais indiretos: saídas a pedido, saldo, salário de reposição e escolaridade.",
  "Escolaridade e salário são associados aos gargalos; os dados não permitem afirmar causa.",
  "Indústria = seções CNAE B–F, como no boletim da FIESC; análise principal na transformação (C), construção separada.",
  "Salários pela mediana, só celetistas comuns (sem aprendiz, parcial ou intermitente), entre R$ 1.000 e R$ 30.000.",
  "Prêmio de contratação e escolaridade são calculados dentro da mesma ocupação e microrregião e depois ponderados, para não confundir setor com mistura de cargos.",
  "Linhas idênticas foram mantidas (provável contratação em lote), como nos números oficiais; removê-las levaria o saldo de +1.008 para −12.287.",
  "99,96% das admissões vêm como \"tipo ignorado\": não dá para separar primeiro emprego de reemprego.",
  "Recortes abaixo do volume mínimo (300 desligamentos ou movimentos) não entram em ranking. Os limiares são escolha da equipe.",
  "População: Censo 2022. Recorte territorial: microrregiões e mesorregiões do IBGE (divisão de 1989, substituída em 2017, mantida por ser reconhecível).",
  "751 ocupações pequenas (2,4% dos movimentos) ficam como \"Outros\" nas macrofamílias e não entram nas recomendações.",
];

function Status({ resultado }) {
  const r = resultado.toLowerCase();
  const tipo = r.startsWith("aprovado") ? "ok" : r.startsWith("reprovado") ? "falha" : "pend";
  const rotulo = { ok: "Aprovado", falha: "Reprovado", pend: "Pendente" }[tipo];
  const icone = {
    ok: <path d="M3 8.5l3 3 7-7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />,
    falha: <path d="M8 3v6M8 12.5v.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />,
    pend: <circle cx="8" cy="8" r="5" fill="none" stroke="currentColor" strokeWidth="2" />,
  }[tipo];
  return <span className={`status ${tipo}`}><svg viewBox="0 0 16 16" aria-hidden="true">{icone}</svg>{rotulo}</span>;
}

const LEITURA_TESTE = {
  T1: "Reconciliação com o boletim da FIESC (saldo jan–mai/2026)",
  T2a: "A mesma ocupação muda de taxa conforme o setor",
  T2b: "O setor pesa mesmo descontada a mistura de ocupações",
  T3: "Dependência do alimentador de linha (mostramos com e sem)",
  T4: "Estabilidade entre semestres",
  T5: "Não depende da definição de indústria (C × B–E)",
  T6: "Concordância da IA com revisores humanos",
};

export default function App() {
  const [dados, setDados] = useState(null);
  const [geo, setGeo] = useState(null);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    Promise.all([fetch("/dados.json").then((r) => r.json()), fetch("/sc_microrregioes.geojson").then((r) => r.json())])
      .then(([d, g]) => { setDados(d); setGeo(g); })
      .catch((e) => setErro(String(e)));
  }, []);

  if (erro) return <div className="wrap" style={{ padding: 40 }}>Não foi possível carregar os dados: {erro}</div>;
  if (!dados || !geo) return <div className="wrap" style={{ padding: 40, color: "var(--muted)" }}>Carregando…</div>;

  const t = dados.segmentos.find((s) => s.segmento === dados.meta.segmento);
  const tSem = dados.segmentos_sem_alimentador.find((s) => s.segmento === dados.meta.segmento);
  const partAlim = 100 * (1 - tSem.movimentos / t.movimentos);
  const ia = dados.ia;

  return (
    <>
      <header className="topo">
        <div className="wrap">
          <div className="marca">Raio-X da Indústria SC <span>· Datathon CDIA 2026</span></div>
          <nav className="nav" aria-label="Seções">
            <a href="#onde">Onde</a><a href="#setores">Setores</a><a href="#porque">Por quê</a>
            <a href="#oque">O que fazer</a><a href="#metodo">Método</a>
          </nav>
        </div>
      </header>

      <main>
        <section className="hero wrap">
          <p className="eyebrow">Novo CAGED · Santa Catarina · set/2025–ago/2026</p>
          <h1>O apagão da indústria catarinense aparece como <em>rotatividade</em>, não como falta de gente</h1>
          <div className="hero-grid">
            <div>
              <div className="numero-heroi">{pct(t.kpi1)}</div>
              <p>dos desligamentos da indústria de transformação são <strong>a pedido do trabalhador</strong> ({int(t.desligamentos)} desligamentos em 12 meses).</p>
            </div>
            <div className="tiles">
              <div className="tile">
                <p className="rot">Saldo de empregos em 12 meses</p>
                <p className="val">{sinalInt(t.saldo)}</p>
                <p className="nota">em {int(t.movimentos)} movimentações: o setor gira muito e quase não cresce</p>
              </div>
              <div className="tile">
                <p className="rot">Salário de reposição</p>
                <p className="val">{dec(t.kpi3, 3)}</p>
                <p className="nota">quem entra ganha {pct(100 * (1 - t.kpi3))} menos que quem sai, na mesma ocupação e região</p>
              </div>
              <div className="tile">
                <p className="rot">Diferença de escolaridade</p>
                <p className="val">{sinal(t.kpi4, 2)} p.p.</p>
                <p className="nota">quem entra tem a mesma formação de quem sai: o problema não é qualificação formal</p>
              </div>
            </div>
          </div>
        </section>

        <section className="bloco" id="onde">
          <div className="wrap">
            <p className="capitulo">1 · Onde</p>
            <h2>O Oeste cresce e perde gente; o Vale do Itajaí encolhe e perde gente</h2>
            <p className="lead">Troque o indicador do mapa: as saídas a pedido mostram onde o trabalhador vai embora por conta própria (sinal de mercado apertado); o saldo por 10 mil habitantes mostra onde há expansão. A agroindústria do Oeste aparece nos dois.</p>
            <Mapa geo={geo} micros={dados.microrregioes} refKpi1={t.kpi1} />
          </div>
        </section>

        <section className="bloco" id="setores">
          <div className="wrap">
            <p className="capitulo">2 · Quais setores</p>
            <h2>Alimentos é a expansão sob pressão; têxtil e madeira encolhem perdendo gente</h2>
            <p className="lead">Cruzando região e setor, cada combinação cai num de quatro quadrantes. Os vermelhos são o sinal mais próximo de apagão: crescem, mas mais da metade de quem sai pede para sair.</p>
            <Setores grupos={dados.grupos} refKpi1={t.kpi1} />
            <div style={{ height: 16 }} />
            <Quadrantes q={dados.quadrantes} />
            <div className="callout">
              <p><strong>Uma única ocupação, o alimentador de linha de produção, responde por {pct(partAlim, 0)} das movimentações da transformação.</strong> Sem ela, o saldo do setor seria {sinalInt(tSem.saldo)} em vez de {sinalInt(t.saldo)}: a pouca expansão que existe depende de vagas de entrada, as mais fáceis de perder.</p>
            </div>
          </div>
        </section>

        <section className="bloco" id="porque">
          <div className="wrap">
            <p className="capitulo">3 · Por quê</p>
            <h2>Não é escolaridade: é retenção e salário de reposição</h2>
            <p className="lead">A IA (Gemini) agrupou as {int(ia.cbos_llm)} ocupações que cobrem 95% das movimentações em {ia.areas} áreas e {ia.niveis} níveis de formação. Os ofícios da agroindústria e da linha de produção concentram as saídas; quem entra tem a mesma escolaridade de quem sai, mas ganha menos.</p>
            <Macrofamilias macros={dados.macrofamilias} refKpi1={t.kpi1} />
            <div style={{ height: 16 }} />
            <div className="duas">
              <Salario salarios={dados.salario_grupo} premio={t.kpi3} />
              <Escolaridade esc={dados.escolaridade} kpi4={t.kpi4} />
            </div>
          </div>
        </section>

        <section className="bloco" id="oque">
          <div className="wrap">
            <p className="capitulo">4 · O que fazer</p>
            <h2>Três decisões, cada uma com um número para acompanhar no CAGED</h2>
            <p className="lead">Cada recomendação liga uma macrofamília da IA a uma região e a um indicador que sai todo mês no Novo CAGED, para medir se a decisão funcionou.</p>
            <div className="recs">
              {dados.recomendacoes.map((r, i) => {
                const ind = r.indicador_de_acompanhamento || {};
                const base = ind.unidade === "%" ? pct(ind.linha_de_base) : sinalInt(ind.linha_de_base);
                const unidade = ind.unidade && ind.unidade !== "%" ? `${ind.unidade} · ` : "";
                const porque = r.porque.charAt(0).toUpperCase() + r.porque.slice(1);
                return (
                  <article className="cartao rec" key={i}>
                    <div className="n">{i + 1}</div>
                    <h3>{r.acao}</h3>
                    <dl>
                      <div><dt>Onde</dt><dd>{r.regiao}</dd></div>
                      <div><dt>Para quem</dt><dd>{r.macrofamilia}</dd></div>
                      <div><dt>Por quê</dt><dd>{porque}.</dd></div>
                      <div><dt>Quem executa</dt><dd>{r.quem_executa}</dd></div>
                    </dl>
                    <div className="medir">
                      <span className="big">{base}</span>
                      <small>{unidade}linha de base hoje{ind.referencia_sc != null ? ` · SC: ${pct(ind.referencia_sc)}` : ""}<br />{ind.kpi}</small>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </section>

        <section className="bloco" id="metodo">
          <div className="wrap">
            <p className="capitulo">5 · Método</p>
            <h2>Como chegamos aqui, e o que testamos antes de afirmar</h2>
            <div className="passos">
              <div className="cartao passo"><div className="k">3,4 mi</div><p>linhas do Novo CAGED de SC; {int(dados.segmentos.reduce((s, x) => s + x.movimentos, 0))} da indústria (B–F) depois dos filtros</p></div>
              <div className="cartao passo"><div className="k">0,01%</div><p>de diferença para o boletim da FIESC no saldo da transformação (jan–mai/2026)</p></div>
              <div className="cartao passo"><div className="k">{int(ia.cbos_llm)}</div><p>ocupações classificadas pelo {ia.modelo} com lista fechada de categorias; {int(ia.cbos_heranca)} herdadas pela família da CBO</p></div>
              <div className="cartao passo"><div className="k">7</div><p>testes de robustez rodados antes de cada afirmação do diagnóstico</p></div>
            </div>
            <div className="cartao tabela-rolagem">
              <h3>Testes de validação</h3>
              <p className="sub">Teste reprovado não foi escondido: virou premissa declarada ou um segundo cenário no diagnóstico</p>
              <table>
                <thead><tr><th>Teste</th><th>O que verifica</th><th>Recorte</th><th>Obtido</th><th>Resultado</th></tr></thead>
                <tbody>
                  {dados.testes.map((x, i) => (
                    <tr key={i}>
                      <td><strong>{x.teste}</strong></td>
                      <td>{LEITURA_TESTE[x.teste] ?? ""}</td>
                      <td>{x.grupo}</td>
                      <td className="num">{x.obtido}</td>
                      <td><Status resultado={x.resultado} /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="sub" style={{ marginTop: 12 }}>T1 na construção: +54 vagas (0,504%) acima do boletim, no limite da tolerância de 0,5%; declarado e aceito. T3: o ranking muda sem o alimentador de linha, por isso o diagnóstico mostra os dois cenários.</p>
            </div>
            <details>
              <summary>Premissas e limites</summary>
              <ol className="premissas">{PREMISSAS.map((p, i) => <li key={i}>{p}</li>)}</ol>
            </details>
          </div>
        </section>
      </main>

      <footer>
        <div className="wrap">
          Fonte: {dados.meta.fonte}. População: {dados.meta.populacao}. {dados.meta.regioes}. Macrofamílias de ocupação classificadas por IA ({ia.modelo}) com revisão humana. Dados gerados em {dados.meta.gerado_em} pelo pipeline em Python do repositório.
        </div>
      </footer>
    </>
  );
}
