import { useEffect, useRef, useState } from "react";
import { FAQ } from "../../api/_base.js";

// Assistente de dúvidas. As perguntas sugeridas respondem localmente (sem rede, sem gastar cota);
// as demais vão para /api/perguntar, que aplica os guardrails e chama o Gemini.
// Abre direto com ?perguntar na URL (para QR code na apresentação).

const BOAS_VINDAS = "Oi! Pergunte sobre o estudo: regiões, setores, salários, escolaridade, a IA que usamos ou as recomendações.";

function Negrito({ texto }) {
  return texto.split(/(\*\*[^*]+\*\*)/g).map((p, i) => (p.startsWith("**") ? <strong key={i}>{p.slice(2, -2)}</strong> : p));
}

export default function Assistente() {
  const [aberto, setAberto] = useState(() => typeof window !== "undefined" && new URLSearchParams(window.location.search).has("perguntar"));
  const [msgs, setMsgs] = useState([{ papel: "assistente", texto: BOAS_VINDAS, origem: "boas-vindas" }]);
  const [texto, setTexto] = useState("");
  const [carregando, setCarregando] = useState(false);
  const fimRef = useRef(null);
  const entradaRef = useRef(null);

  useEffect(() => { fimRef.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [msgs, carregando]);
  useEffect(() => {
    if (!aberto) return;
    entradaRef.current?.focus({ preventScroll: true });
    const esc = (e) => e.key === "Escape" && setAberto(false);
    window.addEventListener("keydown", esc);
    return () => window.removeEventListener("keydown", esc);
  }, [aberto]);

  const usadas = new Set(msgs.filter((m) => m.papel === "usuario").map((m) => m.texto));
  const sugestoes = FAQ.filter((f) => !usadas.has(f.pergunta)).slice(0, 3);

  async function enviar(pergunta) {
    const p = pergunta.trim();
    if (!p || carregando) return;
    setTexto("");
    const pronta = FAQ.find((f) => f.pergunta === p);
    if (pronta) {
      setMsgs((m) => [...m, { papel: "usuario", texto: p }, { papel: "assistente", texto: pronta.resposta, origem: "faq" }]);
      return;
    }
    const historico = msgs.filter((m) => m.origem !== "boas-vindas").slice(-8).map(({ papel, texto }) => ({ papel, texto }));
    setMsgs((m) => [...m, { papel: "usuario", texto: p }]);
    setCarregando(true);
    try {
      const r = await fetch("/api/perguntar", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: p, historico }),
      });
      const j = await r.json().catch(() => ({}));
      setMsgs((m) => [...m, { papel: "assistente", texto: j.resposta || j.erro || "Não consegui responder agora.", origem: j.origem || "erro" }]);
    } catch {
      setMsgs((m) => [...m, { papel: "assistente", texto: "Sem conexão com o assistente. As perguntas sugeridas funcionam mesmo assim.", origem: "erro" }]);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <>
      {!aberto && (
        <button className="assist-fab" onClick={() => setAberto(true)} aria-label="Abrir assistente de dúvidas">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /><path d="M8 9.5h8M8 12.5h5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          Pergunte aos dados
        </button>
      )}
      {aberto && (
        <div className="assist-painel" role="dialog" aria-label="Assistente de dúvidas" aria-modal="false">
          <header className="assist-topo">
            <div>
              <strong>Pergunte aos dados</strong>
              <span>Responde só com os números do estudo</span>
            </div>
            <button onClick={() => setAberto(false)} aria-label="Fechar assistente">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
            </button>
          </header>
          <div className="assist-msgs" aria-live="polite">
            {msgs.map((m, i) => (
              <div key={i} className={`assist-msg ${m.papel}`}>
                <p><Negrito texto={m.texto} /></p>
                {m.origem === "ia" && <small>Gerada por IA (Gemini) a partir da base do estudo</small>}
                {m.origem === "faq" && <small>Resposta da equipe</small>}
              </div>
            ))}
            {carregando && <div className="assist-msg assistente"><p className="assist-digitando" aria-label="Pensando"><i /><i /><i /></p></div>}
            <div ref={fimRef} />
          </div>
          {sugestoes.length > 0 && (
            <div className="assist-sugestoes">
              {sugestoes.map((f) => <button key={f.pergunta} onClick={() => enviar(f.pergunta)} disabled={carregando}>{f.pergunta}</button>)}
            </div>
          )}
          <form className="assist-entrada" onSubmit={(e) => { e.preventDefault(); enviar(texto); }}>
            <input ref={entradaRef} value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={400}
              placeholder="Ex.: e no setor de madeira?" aria-label="Sua pergunta" />
            <button type="submit" disabled={carregando || texto.trim().length < 3} aria-label="Enviar">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </button>
          </form>
        </div>
      )}
    </>
  );
}
