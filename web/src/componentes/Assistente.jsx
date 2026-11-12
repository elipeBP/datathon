// Assistente "Perguntar aos dados" (design: Assistente.dc.html + Notas.dc.html).
// Perguntas prontas respondem na hora (qa.js); perguntas livres vão para /api/perguntar (guardrails + Gemini).
// Abre direto com ?perguntar na URL (QR code na apresentação).
import { createContext, useContext, useRef, useState } from "react";
import { CAPITULOS, QA, TODAS } from "../qa.js";
import { Balao, Fechar, Folha } from "./base.jsx";

const Ctx = createContext(null);
export const useAssistente = () => useContext(Ctx);

const normalizar = (s) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9 ]/g, " ").replace(/\s+/g, " ").trim();

export function AssistenteProvider({ cap, children }) {
  const inicial = typeof window !== "undefined" && new URLSearchParams(window.location.search).has("perguntar");
  const [aberto, setAberto] = useState(inicial);
  const [ctx, setCtx] = useState(null);
  const [trocas, setTrocas] = useState([]);
  const abortar = useRef(null);

  const capAtual = CAPITULOS.find((c) => c.id === cap) || CAPITULOS[0];
  const contexto = ctx || { cap: capAtual.id, texto: capAtual.contexto };

  function abrir(qa, novoCtx) {
    setCtx(novoCtx ? { cap: capAtual.id, texto: capAtual.contexto, ...(typeof novoCtx === "string" ? { texto: novoCtx } : novoCtx) } : null);
    if (qa) setTrocas((t) => [...t, { ...qa, origem: "pronta" }]);
    setAberto(true);
  }

  async function perguntar(texto) {
    const p = texto.trim();
    if (p.length < 3) return;
    const pronta = TODAS.find((x) => normalizar(x.q) === normalizar(p));
    if (pronta) { setTrocas((t) => [...t, { ...pronta, origem: "pronta" }]); return; }
    const historico = trocas.slice(-4).flatMap((x) => [{ papel: "usuario", texto: x.q }, { papel: "assistente", texto: x.a || "" }]);
    const id = `livre-${Date.now()}`;
    setTrocas((t) => [...t, { id, q: p, carregando: true }]);
    const ctl = new AbortController();
    abortar.current = ctl;
    try {
      const r = await fetch("/api/perguntar", {
        method: "POST", signal: ctl.signal, headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: p, historico, contexto: { cap: contexto.cap, capitulo: contexto.texto, regiao: contexto.regiao, setor: contexto.setor } }),
      });
      const j = await r.json().catch(() => ({}));
      setTrocas((t) => t.map((x) => (x.id === id ? {
        ...x, carregando: false, a: j.resposta || j.erro || "Não consegui responder agora.", src: j.fonte, origem: j.origem || "erro",
        bars: j.grafico?.bars, chartTitle: j.grafico?.titulo, sugestoes: Array.isArray(j.sugestoes) ? j.sugestoes : null,
      } : x)));
    } catch (e) {
      const parou = e.name === "AbortError";
      setTrocas((t) => t.map((x) => (x.id === id ? { ...x, carregando: false, a: parou ? "Resposta interrompida." : "Sem conexão com o assistente. As perguntas sugeridas funcionam mesmo assim.", origem: "erro" } : x)));
    } finally {
      abortar.current = null;
    }
  }

  const feitas = new Set(trocas.map((x) => x.id));
  const feitasTexto = new Set(trocas.map((x) => normalizar(x.q)));
  const ultima = trocas[trocas.length - 1];
  // Depois de uma resposta da IA, as sugestões de continuação dela vêm primeiro; senão, as perguntas prontas do capítulo.
  const daIA = (ultima?.sugestoes || []).filter((q) => !feitasTexto.has(normalizar(q))).map((q, i) => ({ id: `sug-${ultima.id}-${i}`, q, livre: true }));
  const prontas = [...(QA[contexto.cap] || []), ...TODAS].filter((x, i, arr) => !feitas.has(x.id) && arr.findIndex((y) => y.id === x.id) === i);
  const outras = [...daIA, ...prontas].slice(0, 3);

  return (
    <Ctx.Provider value={{ abrir }}>
      {children}
      <button className="ai-fab" onClick={() => abrir(null)} aria-label="Perguntar aos dados">
        <Balao size={20} cor="#fff" />Perguntar aos dados
      </button>
      <Folha aberta={aberto} onFechar={() => { abortar.current?.abort(); setAberto(false); }} rotulo="Perguntar aos dados" alta>
        <Painel contexto={contexto} trocas={trocas} outras={outras} carregando={trocas.some((x) => x.carregando)}
          onPerguntar={perguntar} onEscolher={(qa) => (qa.livre ? perguntar(qa.q) : setTrocas((t) => [...t, { ...qa, origem: "pronta" }]))}
          onParar={() => abortar.current?.abort()} onFechar={() => { abortar.current?.abort(); setAberto(false); }} />
      </Folha>
    </Ctx.Provider>
  );
}

function Painel({ contexto, trocas, outras, carregando, onPerguntar, onEscolher, onParar, onFechar }) {
  const [texto, setTexto] = useState("");
  const fim = useRef(null);
  const rolar = () => setTimeout(() => fim.current?.scrollIntoView({ behavior: "smooth", block: "end" }), 40);
  return (
    <>
      <div className="ai-topo">
        <div className="marca">
          <span className="ic" aria-hidden="true"><Balao size={18} cor="var(--tinta)" /></span>
          <div><div className="t">Perguntar aos dados</div><div className="c">Assistente de IA · contexto: {contexto.texto}</div></div>
        </div>
        <button className="icone-btn" onClick={onFechar} aria-label="Fechar"><Fechar /></button>
      </div>

      <div className="ai-corpo" aria-live="polite">
        {trocas.length === 0 && (
          <p style={{ margin: 0, fontSize: 15, color: "var(--tinta2)" }}>
            Pergunte sobre regiões, setores, salários, escolaridade, a IA usada ou as recomendações. Eu respondo só com os números deste estudo e sempre mostro a fonte.
          </p>
        )}
        {trocas.map((x) => (
          <div className="ai-troca" key={x.id + (x.origem || "")}>
            <div className="ai-pergunta"><div>{x.q}</div></div>
            <div className="ai-resposta">
              <div className="eyebrow" style={{ fontSize: 11 }}>Resposta</div>
              {x.carregando ? (
                <div className="ai-carregando" aria-label="Processando"><i /><i /><i /></div>
              ) : (
                <>
                  {(x.a || "").split(/\n\s*\n/).map((par, i) => (
                    <p key={i} style={{ animationDelay: `${i * 120}ms` }}>{par.split(/(\*\*[^*]+\*\*)/g).map((t, k) => (t.startsWith("**") ? <b key={k}>{t.slice(2, -2)}</b> : t))}</p>
                  ))}
                  {x.bars && (
                    <div className="ai-graf">
                      <div className="t">{x.chartTitle}</div>
                      {x.bars.map((b) => (
                        <div className="l" key={b.l}><span>{b.l}</span><span className="tr"><span style={{ width: `${Math.min(100, b.w)}%`, background: b.c }} /></span><span className="num" style={{ textAlign: "right", fontWeight: 600 }}>{b.v}</span></div>
                      ))}
                    </div>
                  )}
                  {x.src && (
                    <div className="ai-fonte">
                      <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="var(--tinta3)" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3h9l4 4v14H6z" /><path d="M14 3v5h5M9 13h7M9 17h5" /></svg>
                      <span><b>Fonte:</b> {x.src}</span>
                    </div>
                  )}
                  {x.origem === "ia" && <div className="ai-aviso-ia">Resposta gerada pela IA (Gemini) a partir da base do estudo; os números foram conferidos automaticamente.</div>}
                </>
              )}
            </div>
          </div>
        ))}
        {outras.length > 0 && (
          <div className="ai-outras">
            <div className="eyebrow" style={{ fontSize: 11 }}>{trocas.length ? "Outras perguntas" : "Perguntas sugeridas"}</div>
            {outras.map((o) => (
              <button key={o.id} className="q" onClick={() => { onEscolher(o); rolar(); }}>{o.q}<span aria-hidden="true" className="seta">→</span></button>
            ))}
          </div>
        )}
        <div ref={fim} />
      </div>

      <div className="ai-pe">
        <form onSubmit={(e) => { e.preventDefault(); if (carregando) return; onPerguntar(texto); setTexto(""); rolar(); }}>
          <label htmlFor="pergunta" className="so-leitor">Escreva sua pergunta</label>
          <input id="pergunta" data-foco type="text" value={texto} maxLength={400} onChange={(e) => setTexto(e.target.value)}
            placeholder="Pergunte sobre regiões, setores…" autoComplete="off" />
          {carregando ? (
            <button type="button" className="enviar" onClick={onParar} aria-label="Parar resposta">
              <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2" fill="#fff" /></svg>
            </button>
          ) : (
            <button type="submit" className="enviar" aria-label="Enviar pergunta" disabled={texto.trim().length < 3}>
              <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke="#fff" strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          )}
        </form>
        <p>Respostas geradas por IA a partir dos dados deste site. Confira os números nos gráficos.</p>
      </div>
    </>
  );
}
