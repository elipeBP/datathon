// Formatação pt-BR e hooks compartilhados.
import { useEffect, useState } from "react";

const nf = (casas) => new Intl.NumberFormat("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
export const int = (v) => nf(0).format(Math.round(v));
export const dec = (v, casas = 1) => nf(casas).format(v);
export const pct = (v, casas = 1) => `${dec(v, casas)}%`;
export const sinal = (v, casas = 1) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${dec(Math.abs(v), casas)}`;
export const sinalInt = (v) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${int(Math.abs(v))}`;
export const reais = (v) => `R$ ${int(v)}`;

/** true quando o tema escuro está ativo (sistema operacional). */
export function useEscuro() {
  const q = typeof window !== "undefined" ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  const [escuro, setEscuro] = useState(q ? q.matches : false);
  useEffect(() => {
    if (!q) return;
    const f = (e) => setEscuro(e.matches);
    q.addEventListener("change", f);
    return () => q.removeEventListener("change", f);
  }, []);
  return escuro;
}

/** Tooltip que segue o ponteiro dentro de um contêiner com position: relative. */
export function useTooltip() {
  const [tip, setTip] = useState(null);
  const mostrar = (e, conteudo) => {
    const caixa = e.currentTarget.closest(".cartao") ?? e.currentTarget.parentElement;
    const r = caixa.getBoundingClientRect();
    setTip({ x: e.clientX - r.left, y: e.clientY - r.top, largura: r.width, conteudo });
  };
  return { tip, mostrar, esconder: () => setTip(null) };
}

export function Tooltip({ tip }) {
  if (!tip) return null;
  const esquerda = tip.x > tip.largura * 0.6;
  return (
    <div className="tooltip" role="status"
      style={{ left: tip.x, top: tip.y, transform: `translate(${esquerda ? "calc(-100% - 14px)" : "14px"}, -50%)` }}>
      {tip.conteudo}
    </div>
  );
}
