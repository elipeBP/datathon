// Capítulo 5 — O que fazer (Tela5-OQueFazer.dc.html). Lê app/recomendacoes.yaml via dados.json.
import { QA } from "../qa.js";
import { Balao, Icone, ProximoCapitulo, Seta, useVisto } from "../componentes/base.jsx";
import { useAssistente } from "../componentes/Assistente.jsx";
import { pct, sinalInt } from "../fmt.jsx";

const negrito = (s) => s.split(/(\*\*[^*]+\*\*)/g).map((t, k) => (t.startsWith("**") ? <b key={k} className="num">{t.slice(2, -2)}</b> : t));

function Comparacao({ itens, i0 }) {
  const divergente = itens.some((x) => x.valor < 0);
  if (divergente) {
    const max = Math.max(...itens.map((x) => Math.abs(x.valor)));
    return (
      <div className="comp" role="img" aria-label={itens.map((x) => `${x.rotulo} ${x.texto}`).join(", ")} style={{ gridTemplateColumns: "104px 1fr 1fr", rowGap: 6 }}>
        {itens.map((x, i) => (
          x.valor < 0 ? [
            <span key={`r${i}`}>{x.rotulo}</span>,
            <span key={`b${i}`} style={{ display: "flex", justifyContent: "flex-end", borderRight: "1px solid var(--tinta)" }}>
              <span className="b neg" style={{ "--i": i0 + i, display: "block", height: 8, borderRadius: "4px 0 0 4px", background: `var(--${x.cor})`, width: `${(Math.abs(x.valor) / max) * 100}%`, transformOrigin: "right center" }} />
            </span>,
            <span key={`v${i}`} className="num" style={{ paddingLeft: 6, fontWeight: 600 }}>{x.texto}</span>,
          ] : [
            <span key={`r${i}`}>{x.rotulo}</span>,
            <span key={`v${i}`} className="num" style={{ textAlign: "right", paddingRight: 6, fontWeight: 600, borderRight: "1px solid var(--tinta)" }}>{x.texto}</span>,
            <span key={`b${i}`}><span className="b" style={{ "--i": i0 + i, display: "block", height: 8, borderRadius: "0 4px 4px 0", background: `var(--${x.cor})`, width: `${(x.valor / max) * 100}%` }} /></span>,
          ]
        ))}
      </div>
    );
  }
  return (
    <div className="comp" role="img" aria-label={itens.map((x) => `${x.rotulo} ${x.texto}`).join(", ")}>
      {itens.map((x, i) => [
        <span key={`r${i}`}>{x.rotulo}</span>,
        <span key={`b${i}`}><span className="b" style={{ "--i": i0 + i, display: "block", height: 8, borderRadius: 4, background: `var(--${x.cor})`, width: `${(x.valor / 70) * 100}%` }} /></span>,
        <span key={`v${i}`} className="num" style={{ textAlign: "right", fontWeight: 600 }}>{x.texto}</span>,
      ])}
    </div>
  );
}

export default function OQueFazer({ dados }) {
  const { abrir } = useAssistente();
  const [ref, classe] = useVisto();
  const ctx = { cap: "oque", texto: "Capítulo 5, recomendações" };
  const perguntas = QA.oque;

  return (
    <>
      <section className="abre">
        <div className="eyebrow">O que fazer</div>
        <h1>Três ações, cada uma com um número para acompanhar.</h1>
      </section>

      <div className={`recs ${classe}`} ref={ref}>
        {dados.recomendacoes.map((r, i) => {
          const ind = r.indicador_de_acompanhamento || {};
          const base = ind.unidade === "%" ? pct(ind.linha_de_base) : sinalInt(ind.linha_de_base);
          const qa = perguntas[i];
          return (
            <article className="cartao rec" key={i}>
              <div className="rec-topo">
                <div>
                  <span className="rec-n num">{i + 1}</span>
                  <h2>{r.titulo_curto || r.acao}</h2>
                </div>
                <span className="ic-caixa" style={{ width: "auto", minWidth: 44, height: 44, padding: "0 8px", gap: 2 }}>
                  {(r.icones || []).map((k, j) => (
                    <span key={k} style={{ display: "inline-flex", alignItems: "center" }}>
                      {j > 0 && <Seta cor="var(--tinta3)" size={14} />}
                      <Icone kind={k} size={r.icones.length > 1 ? 22 : 26} cor={j === 0 && r.icones.length > 1 ? "var(--tinta3)" : "var(--tinta)"} />
                    </span>
                  ))}
                </span>
              </div>
              <dl>
                <div className="fld"><dt>Onde</dt><dd>{r.onde_curto || r.regiao}</dd></div>
                <div className="fld"><dt>Para quem</dt><dd>{r.macrofamilia} <span className="muted" style={{ fontSize: 12.5 }}>(macrofamília da IA)</span></dd></div>
                <div className="fld"><dt>Por quê</dt><dd>{negrito(r.porque_curto || r.porque)}</dd></div>
                <div className="fld"><dt>Quem executa</dt><dd>{r.quem_executa}</dd></div>
                {r.evidencia_modelo && (
                  <div className="fld"><dt>Modelo</dt><dd style={{ fontSize: 13.5, color: "var(--tinta2)" }}>{r.evidencia_modelo}</dd></div>
                )}
              </dl>
              {r.comparacao && <Comparacao itens={r.comparacao} i0={i * 2} />}
              <div className="empurra">
                <div className="base-linha">
                  <div>
                    <div className="r">Linha de base</div>
                    <div className="s">{ind.unidade === "%" ? "% de saídas a pedido" : "vagas na eletroeletrônica"} · meta: {r.meta || "acompanhar"}</div>
                  </div>
                  <div className="v num">{base}</div>
                </div>
                {qa && (
                  <button className="q-rodape" onClick={() => abrir(qa, ctx)}>
                    <span className="com-icone" style={{ display: "inline-flex", alignItems: "center", gap: 8 }}><Balao />{qa.q}</span><span aria-hidden="true" className="muted">→</span>
                  </button>
                )}
              </div>
            </article>
          );
        })}
      </div>

      <p className="fonte bloco" style={{ marginTop: 20 }}>
        As linhas de base saem do Novo CAGED e podem ser reapuradas todo mês com o mesmo método.{" "}
        <button className="link-q" onClick={() => abrir(perguntas[3], ctx)} style={{ border: 0, background: "none", padding: 0, textDecoration: "underline", color: "var(--tinta)", fontSize: 12 }}>Como acompanhar?</button>
      </p>
      <ProximoCapitulo cap="oque" />
    </>
  );
}
