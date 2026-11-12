// Peças compartilhadas pelas telas (design: documentos/raio-x-design).
import { useEffect, useRef, useState } from "react";
import ICONES from "../icones.json";
import { CAPITULOS } from "../qa.js";
import { useAssistente } from "./Assistente.jsx";

export const MEDIA_COR = (v, media) => (v > media ? "var(--sinal)" : "var(--neutro-claro)");

export function Icone({ kind, size = 24, cor = "var(--tinta)", titulo }) {
  const ic = ICONES[kind] || ICONES.metal;
  return (
    <span role="img" aria-label={titulo ?? ic.label} style={{ display: "inline-flex", flex: "none", width: size, height: size, color: cor }}>
      <svg viewBox="0 0 24 24" width="100%" height="100%" fill="none" stroke="currentColor" strokeWidth={size >= 40 ? 1.25 : 1.5}
        strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={ic.d} /></svg>
    </span>
  );
}

/** Balão com barras: o ícone do assistente (nunca faísca). */
export function Balao({ size = 16, cor = "var(--tinta3)" }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke={cor} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" style={{ flex: "none" }}>
      <path d="M4 5h16v11H9l-5 4z" /><path d="M9 13V10M12 13V8M15 13v-2" />
    </svg>
  );
}

export const Seta = ({ cor = "currentColor", size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" stroke={cor} strokeWidth="1.8" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
);
export const Fechar = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="var(--tinta)" strokeWidth="1.6" strokeLinecap="round" /></svg>
);

/** Perguntas sugeridas embaixo de um gráfico; cada uma abre o assistente já respondendo. */
export function Pergunte({ titulo = "Pergunte sobre este dado", itens, caixa = false, contexto }) {
  const { abrir } = useAssistente();
  return (
    <div className={`pergunte${caixa ? " caixa" : ""}`}>
      {titulo && <div className="cab-p"><Balao />{titulo}</div>}
      {itens.map((qa) => (
        <button key={qa.id} className="q" onClick={(e) => abrir(qa, contexto, e.currentTarget)}>
          {titulo ? qa.q : <span className="com-icone"><Balao />{qa.q}</span>}<span aria-hidden="true" className="seta">→</span>
        </button>
      ))}
    </div>
  );
}

/** Seletor de duas posições (radiogroup; setas do teclado alternam). */
export function Seletor({ opcoes, valor, onChange, rotulo }) {
  const pos = opcoes.findIndex((o) => o.v === valor);
  const tecla = (e) => {
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) {
      e.preventDefault();
      const prox = opcoes[(pos + 1) % opcoes.length];
      onChange(prox.v);
      e.currentTarget.parentElement.querySelectorAll("button")[(pos + 1) % opcoes.length].focus();
    }
  };
  return (
    <div className="seletor" role="radiogroup" aria-label={rotulo} data-pos={pos}>
      <span className="polegar" aria-hidden="true" />
      {opcoes.map((o) => (
        <button key={o.v} role="radio" aria-checked={o.v === valor} tabIndex={o.v === valor ? 0 : -1} onClick={() => onChange(o.v)} onKeyDown={tecla}>
          {o.t}<span>{o.s}</span>
        </button>
      ))}
    </div>
  );
}

/** Folha: bottom sheet no celular, gaveta à direita no desktop. Fecha com Esc, no fundo ou no ×; devolve o foco. */
export function Folha({ aberta, onFechar, rotulo, alta = false, children }) {
  const ref = useRef(null);
  const origem = useRef(null);
  useEffect(() => {
    if (!aberta) return;
    origem.current = document.activeElement;
    const esc = (e) => e.key === "Escape" && onFechar();
    window.addEventListener("keydown", esc);
    document.body.style.overflow = "hidden";
    setTimeout(() => ref.current?.querySelector("[data-foco]")?.focus({ preventScroll: true }), 30);
    return () => {
      window.removeEventListener("keydown", esc);
      document.body.style.overflow = "";
      origem.current?.focus?.({ preventScroll: true });
    };
  }, [aberta]);
  if (!aberta) return null;
  return (
    <>
      <button className="folha-fundo" aria-label="Fechar" onClick={onFechar} tabIndex={-1} />
      <section ref={ref} className={`folha${alta ? " alta" : ""}`} role="dialog" aria-modal="true" aria-label={rotulo}>
        <div className="alca" aria-hidden="true" />
        {children}
      </section>
    </>
  );
}

/** Adiciona a classe "cresce" quando o elemento entra 30% na tela (anima uma vez por visita). */
export function useVisto() {
  const ref = useRef(null);
  const [visto, setVisto] = useState(false);
  useEffect(() => {
    if (!ref.current || visto) return;
    const ob = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVisto(true); ob.disconnect(); } }, { threshold: 0.3 });
    ob.observe(ref.current);
    return () => ob.disconnect();
  }, [visto]);
  return [ref, visto ? "cresce" : "espera"];
}

export function Cabecalho({ cap }) {
  const [menu, setMenu] = useState(false);
  const { abrir } = useAssistente();
  const atual = CAPITULOS.find((c) => c.id === cap);
  useEffect(() => {
    if (!menu) return;
    const esc = (e) => e.key === "Escape" && setMenu(false);
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [menu]);
  return (
    <>
      <header className="cab">
        <div className="cab-in">
          <a className="logo" href="#/tese"><span className="rx" aria-hidden="true">RX</span><span className="nome">Raio-X da Indústria SC</span></a>
          <nav className="nav-desk" aria-label="Capítulos">
            {CAPITULOS.map((c) => <a key={c.id} href={`#/${c.id}`} aria-current={c.id === cap ? "page" : undefined}>{c.nome}</a>)}
          </nav>
          <button className="btn-escuro so-desk" onClick={(e) => abrir(null, atual.contexto, e.currentTarget)}><Balao size={18} cor="#fff" />Perguntar aos dados</button>
          <button className="icone-btn so-mobile" onClick={() => setMenu(true)} aria-label="Capítulos" aria-expanded={menu}>
            <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="var(--tinta)" strokeWidth="1.6" strokeLinecap="round" fill="none" /></svg>
          </button>
        </div>
      </header>
      <nav className="progresso" aria-label="Progresso">
        <div className="trilhos" aria-hidden="true">{CAPITULOS.map((c) => <span key={c.id} className={c.n <= atual.n ? "on" : ""} />)}</div>
        <div className="legenda"><span>Capítulo {atual.n} de 6 · {atual.nome}</span><span>Novo CAGED · set/25–ago/26</span></div>
      </nav>
      {menu && (
        <div className="menu-fundo" onClick={() => setMenu(false)}>
          <div className="menu" role="dialog" aria-label="Capítulos" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 15, fontWeight: 600 }}>Capítulos</span>
              <button className="icone-btn" onClick={() => setMenu(false)} aria-label="Fechar"><Fechar /></button>
            </div>
            <ol>
              {CAPITULOS.map((c) => (
                <li key={c.id}><a href={`#/${c.id}`} aria-current={c.id === cap ? "page" : undefined} onClick={() => setMenu(false)}>
                  <span className="n num">{String(c.n).padStart(2, "0")}</span>{c.nome}</a></li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </>
  );
}

export function ProximoCapitulo({ cap }) {
  const i = CAPITULOS.findIndex((c) => c.id === cap);
  const ant = CAPITULOS[i - 1], seg = CAPITULOS[i + 1];
  return (
    <nav className={`prox${ant ? "" : " so-um"}`} aria-label="Capítulos">
      {ant && <a className="ant" href={`#/${ant.id}`}><span className="r">← Capítulo {ant.n}</span><span className="t">{ant.nome}</span></a>}
      {seg
        ? <a className="seg" href={`#/${seg.id}`}><span className="r">Próximo · Capítulo {seg.n} →</span><span className="t">{seg.titulo}</span></a>
        : <a className="seg" href="#/tese"><span className="r">Voltar ao início</span><span className="t">A tese</span></a>}
    </nav>
  );
}
