// Capítulo 4 — Por quê (Tela4-PorQue.dc.html)
import { QA } from "../qa.js";
import { Pergunte, ProximoCapitulo, useVisto } from "../componentes/base.jsx";
import { pct, sinal } from "../fmt.jsx";

const NIVEL = { "Qualificação até 200h": "até 200h", "Qualificação acima de 200h": "acima de 200h", "Técnico": "técnico", "Superior": "superior" };
const reais = (v) => `R$ ${Math.round(v).toLocaleString("pt-BR")}`;

export default function PorQue({ dados }) {
  const t = dados.segmentos.find((s) => s.segmento === "Transformação");
  const media = t.kpi1;
  const ctx = { cap: "porque", texto: "Capítulo 4, por quê" };
  const [r1, c1] = useVisto(), [r2, c2] = useVisto(), [r3, c3] = useVisto();

  // As macrofamílias com mais desligamentos (volume), ordenadas pelo % a pedido.
  const fam = dados.macrofamilias.filter((m) => m.kpi1_ok).sort((a, b) => b.desligamentos - a.desligamentos).slice(0, 8).sort((a, b) => b.kpi1 - a.kpi1);
  const sal = [...dados.salario_grupo].map((s) => ({ ...s, gap: (s.admitidos / s.desligados - 1) * 100 })).sort((a, b) => a.gap - b.gap);
  const lo = 2000, hi = 2600, pos = (v) => Math.max(0, Math.min(100, ((v - lo) / (hi - lo)) * 100));
  const todosMenos = sal.every((s) => s.admitidos < s.desligados);
  const faixas = ["Até fundamental", "Médio", "Superior incompleto", "Superior ou mais"];
  const esc = (tipo, f) => dados.escolaridade.find((e) => e.tipo === tipo && e.faixa === f)?.pct ?? 0;
  const ia = dados.ia;

  return (
    <>
      <section className="abre">
        <div className="eyebrow">Por quê</div>
        <h1>Não é escolaridade: é retenção e salário de reposição.</h1>
        <p>Quem sai pede para sair, quem entra ganha menos e estudou o mesmo. Três gráficos, uma conclusão.</p>
      </section>

      <div className="porque-grade">
        <section className="graf-sec" style={{ marginTop: 32 }}>
          <div className="rot-graf">Gráfico 1 de 3</div>
          <h2 className="graf" style={{ marginTop: 4 }}>Os ofícios da agroindústria lideram as saídas a pedido</h2>
          <div className="sub-graf">Ocupações agrupadas por IA (área × nível de formação) · as {fam.length} com mais desligamentos</div>
          <div ref={r1} className={`linhas ${c1}`} style={{ marginTop: 10 }}>
            {fam.map((m, i) => (
              <div className="fam" key={m.area + m.nivel}>
                <div className="topo">
                  <span style={{ fontSize: 14, lineHeight: 1.3 }}>{m.area} <span className="muted" style={{ fontSize: 12, whiteSpace: "nowrap" }}>{NIVEL[m.nivel]}</span></span>
                  <span className="num" style={{ fontSize: 13.5, fontWeight: 600 }}>{pct(m.kpi1)}</span>
                </div>
                <div className="trilho-barra" style={{ height: 10, marginTop: 6 }} aria-hidden="true">
                  <span className="media" style={{ left: `${(media / 70) * 100}%` }} />
                  <span className="b" style={{ "--i": i, top: 1, left: 0, width: `${(m.kpi1 / 70) * 100}%`, background: m.kpi1 > media ? "var(--sinal)" : "var(--neutro-claro)" }} />
                </div>
              </div>
            ))}
          </div>
          <p className="nota-graf">Linha tracejada: média de SC ({pct(media)}). Vermelho: acima da média.</p>
          <div className="ia-caixa">
            <span className="ic" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--tinta)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M4 6h16M4 12h10M4 18h7" /><path d="M16 15l2 2 4-4" /></svg>
            </span>
            <div>
              <div style={{ fontSize: 13.5, fontWeight: 600 }}>Como as ocupações foram agrupadas</div>
              <p style={{ margin: "4px 0 0", fontSize: 13.5, lineHeight: 1.45, color: "var(--tinta2)" }}>
                <b className="num">{ia.cbos_llm}</b> ocupações classificadas por IA (Gemini) em <b className="num">{ia.areas}</b> áreas e <b className="num">{ia.niveis}</b> níveis de formação, com lista fechada e revisão humana.
              </p>
            </div>
          </div>
          <Pergunte titulo="" itens={[QA.porque[1]]} contexto={ctx} />
        </section>

        <section className="graf-sec">
          <div className="rot-graf">Gráfico 2 de 3</div>
          <h2 className="graf" style={{ marginTop: 4 }}>{todosMenos ? "Em todos os setores, quem entra ganha menos que quem sai" : "Na maioria dos setores, quem entra ganha menos que quem sai"}</h2>
          <div style={{ display: "flex", gap: 14, fontSize: 12.5, color: "var(--tinta2)", marginTop: 6, flexWrap: "wrap" }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--sinal)" }} />Quem entra</span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ width: 9, height: 9, borderRadius: "50%", background: "var(--neutro)" }} />Quem sai</span>
            <span className="muted">salário mediano</span>
          </div>
          <div ref={r2} className={`linhas ${c2}`} style={{ marginTop: 10 }}>
            {sal.map((d, i) => (
              <div key={d.grupo} role="img" aria-label={`${d.grupo}: entra ${reais(d.admitidos)}, sai ${reais(d.desligados)}`} style={{ padding: "9px 0 7px", borderBottom: "1px solid var(--linha)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <span style={{ fontSize: 14 }}>{d.grupo}</span><span className="num" style={{ fontSize: 13.5, fontWeight: 600 }}>−{pct(Math.abs(d.gap))}</span>
                </div>
                <div style={{ position: "relative", height: 16, margin: "4px 6px 0" }}>
                  <div style={{ position: "absolute", left: 0, right: 0, top: 7, height: 2, background: "var(--trilho)" }} />
                  <div className="b" style={{ "--i": i, position: "absolute", top: 7, height: 2, background: "var(--tinta2)", left: `${pos(d.admitidos)}%`, width: `${pos(d.desligados) - pos(d.admitidos)}%`, transformOrigin: "right center" }} />
                  <div style={{ position: "absolute", top: 3, width: 10, height: 10, marginLeft: -5, borderRadius: "50%", background: "var(--sinal)", left: `${pos(d.admitidos)}%` }} />
                  <div style={{ position: "absolute", top: 3, width: 10, height: 10, marginLeft: -5, borderRadius: "50%", background: "var(--neutro)", left: `${pos(d.desligados)}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="num muted" style={{ display: "flex", justifyContent: "space-between", margin: "6px 6px 0", fontSize: 11.5 }}><span>R$ 2.000</span><span>R$ 2.300</span><span>R$ 2.600</span></div>
          <p className="nota-graf">Celetistas comuns, salários de R$ 1.000 a R$ 30.000. Na mesma ocupação e região, a reposição paga {pct(100 - t.kpi3 * 100)} menos (prêmio {t.kpi3.toFixed(3).replace(".", ",")}).</p>
          <Pergunte titulo="" itens={[QA.porque[0]]} contexto={ctx} />
        </section>

        <section className="graf-sec">
          <div className="rot-graf">Gráfico 3 de 3</div>
          <h2 className="graf" style={{ marginTop: 4 }}>Quem entra estudou praticamente o mesmo que quem sai</h2>
          <div className="sub-graf">% por escolaridade · barra de cima: entra; de baixo: sai</div>
          <div ref={r3} className={`linhas ${c3}`} style={{ marginTop: 10 }}>
            {faixas.map((f, i) => (
              <div className="esc-linha" key={f}>
                <span className="n">{f}</span>
                <span className="b" style={{ "--i": i, width: `${esc("Admitidos", f)}%`, background: "var(--neutro)", transformOrigin: "left center" }} /><span className="v num">{pct(esc("Admitidos", f))}</span>
                <span className="b" style={{ "--i": i, width: `${esc("Desligados", f)}%`, background: "var(--neutro-claro)", transformOrigin: "left center" }} /><span className="v num">{pct(esc("Desligados", f))}</span>
              </div>
            ))}
          </div>
          <div className="resumo">
            <span className="v num">{sinal(t.kpi4, 2)} <small>p.p.</small></span>
            <span style={{ fontSize: 14, lineHeight: 1.4 }}>de diferença no ensino superior, comparando na mesma ocupação e região. A formação não explica a saída.</span>
          </div>
          <Pergunte titulo="" itens={[QA.porque[2]]} contexto={ctx} />
          <p className="fonte" style={{ marginTop: 16 }}>Fonte: Novo CAGED (MTE), indústria de transformação, set/2025 a ago/2026.</p>
        </section>
      </div>

      <ProximoCapitulo cap="porque" />
    </>
  );
}
