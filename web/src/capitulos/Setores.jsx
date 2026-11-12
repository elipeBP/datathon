// Capítulo 3 — Setores (Tela3-Setores.dc.html)
import { useEffect, useRef, useState } from "react";
import { QA, qaSetor } from "../qa.js";
import { Balao, Icone, Pergunte, ProximoCapitulo, useVisto } from "../componentes/base.jsx";
import { useAssistente } from "../componentes/Assistente.jsx";
import { SETORES } from "./Tese.jsx";
import { pct, sinalInt } from "../fmt.jsx";

const QUAD = {
  ex: { nome: "Cresce e perde gente", cor: "var(--sinal)", fg: "#fff" },
  re: { nome: "Não cresce e perde gente", cor: "var(--retencao)", fg: "#fff" },
  cr: { nome: "Cresce e retém", cor: "var(--expansao)", fg: "#fff" },
  es: { nome: "Estagnado", cor: "var(--neutro-claro)", fg: "var(--tinta)" },
};
const reais = (v) => `R$ ${Math.round(v).toLocaleString("pt-BR")}`;

export default function Setores({ dados, param }) {
  const { abrir } = useAssistente();
  const media = dados.segmentos.find((s) => s.segmento === "Transformação").kpi1;
  const t = dados.segmentos.find((s) => s.segmento === "Transformação");
  const tSem = dados.segmentos_sem_alimentador.find((s) => s.segmento === "Transformação");
  const sal = Object.fromEntries(dados.salario_grupo.map((x) => [x.grupo, x]));
  const lista = SETORES.map((s) => ({ ...s, g: dados.grupos.find((x) => x.grupo === s.grupo) })).filter((s) => s.g).sort((a, b) => b.g.kpi1 - a.g.kpi1);
  const [sel, setSel] = useState(() => (lista.find((s) => s.k === param?.get("s")) || lista[0]).k);
  const [refBarras, classeBarras] = useVisto();
  const chipsRef = useRef(null);
  const cartaoRef = useRef(null);

  useEffect(() => {
    chipsRef.current?.querySelector('[aria-selected="true"]')?.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" });
  }, [sel]);
  useEffect(() => { const k = param?.get("s"); if (k && lista.some((s) => s.k === k)) setSel(k); }, [param?.get("s")]);

  const cur = lista.find((s) => s.k === sel);
  const g = cur.g, sg = sal[g.grupo];
  const acima = g.kpi1 > media, cresce = g.saldo > 0;
  const quad = cresce ? (acima ? "ex" : "cr") : (acima ? "re" : "es");
  const gap = sg ? (sg.admitidos / sg.desligados - 1) * 100 : 0;
  const lo = 2000, hi = 2600, pos = (v) => ((v - lo) / (hi - lo)) * 100;
  const cabecalho = { ex: "cresce e perde gente.", re: "não cresce e perde gente.", cr: "cresce e retém.", es: "não cresce, mas retém." }[quad];
  const ctx = { cap: "setores", texto: "Capítulo 3, setores" };
  const partAlim = 100 * (1 - tSem.movimentos / t.movimentos);
  const piores = lista.filter((s) => s.g.kpi1 > media).map((s) => s.curto.toLowerCase());
  const tituloH1 = `${piores.slice(0, -1).join(", ").replace(/^./, (c) => c.toUpperCase())} e ${piores.at(-1)} perdem mais gente que a média.`;

  const escolher = (k, rolar) => {
    setSel(k);
    if (rolar && window.matchMedia("(max-width: 959px)").matches) setTimeout(() => cartaoRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  };

  return (
    <>
      <section className="abre">
        <div className="eyebrow">Setores</div>
        <h1>{tituloH1}</h1>
      </section>

      <div className="setores-grade">
        <div className="esq">
          <section className="bloco-m" style={{ margin: "22px 0 0" }}>
            <div className="bloco-m-in" style={{ padding: "0 var(--margem-m, 0)" }}>
              <div style={{ fontSize: 12.5, fontWeight: 500, color: "var(--tinta2)" }}>% dos desligamentos a pedido · toque num setor para abrir</div>
              <div ref={refBarras} className={`linhas ${classeBarras}`} style={{ marginTop: 8 }}>
                {lista.map((s, i) => (
                  <button key={s.k} className="linha-btn" onClick={() => escolher(s.k, true)} aria-pressed={s.k === sel}
                    style={{ gridTemplateColumns: "20px 104px 1fr 48px", background: s.k === sel ? "var(--superficie)" : undefined }}>
                    <Icone kind={s.k} size={18} cor="var(--tinta3)" />
                    <span style={{ fontSize: 14, lineHeight: 1.2, fontWeight: s.k === sel ? 600 : 400 }}>{s.curto}</span>
                    <span className="trilho-barra" aria-hidden="true">
                      <span className="media" style={{ left: `${(media / 70) * 100}%` }} />
                      <span className="b" style={{ "--i": i, left: 0, width: `${(s.g.kpi1 / 70) * 100}%`, background: s.g.kpi1 > media ? "var(--sinal)" : "var(--neutro-claro)" }} />
                    </span>
                    <span className="v num">{pct(s.g.kpi1)}</span>
                  </button>
                ))}
              </div>
              <p className="nota-graf">Linha tracejada: média de SC ({pct(media)}). Vermelho: acima da média.</p>
              <Pergunte titulo="Pergunte sobre este gráfico" itens={QA.setores.slice(0, 2)} caixa contexto={ctx} />
            </div>
          </section>
        </div>

        <div className="dir" ref={cartaoRef} style={{ scrollMarginTop: 72 }}>
          <section style={{ marginTop: 36 }}>
            <div className="eyebrow">Detalhe</div>
            <h2 className="graf">Escolha um setor</h2>
            <div className="chips" role="tablist" aria-label="Setores" ref={chipsRef}>
              {lista.map((s) => (
                <button key={s.k} role="tab" className="chip" aria-selected={s.k === sel} onClick={() => escolher(s.k)}>{s.curto}</button>
              ))}
            </div>
          </section>

          <article className="cartao troca" key={sel} role="tabpanel" aria-label={g.grupo}>
            <div className="cartao-topo">
              <span className="ic-caixa"><Icone kind={cur.k} size={28} /></span>
              <div>
                <div style={{ fontSize: 19, lineHeight: 1.25, fontWeight: 600 }}>{g.grupo}</div>
                <div style={{ fontSize: 14.5, lineHeight: 1.4, color: "var(--tinta2)", marginTop: 2 }}>{cur.curto} {cabecalho}</div>
              </div>
            </div>
            <div className="oficios">
              <span className="r">Ofícios</span>
              <span className="lista">{cur.objs.map((o) => <Icone key={o} kind={o} size={20} cor="var(--tinta3)" />)}</span>
            </div>
            <div className="dupla" style={{ gap: 0 }}>
              <div className="celula" style={{ borderRight: "1px solid var(--linha)", borderBottom: "1px solid var(--linha)" }}>
                <div className="muted" style={{ fontSize: 12 }}>Saídas a pedido</div>
                <div className="num" style={{ fontSize: 30, lineHeight: 1.15, fontWeight: 600 }}>{pct(g.kpi1)}</div>
                <div className="mini-barra"><div style={{ width: `${(g.kpi1 / 70) * 100}%`, background: acima ? "var(--sinal)" : "var(--neutro)" }} /><div className="media" style={{ left: `${(media / 70) * 100}%` }} /></div>
                <div className="muted num" style={{ fontSize: 11.5, marginTop: 6 }}>{g.kpi1 >= media ? "+" : "−"}{pct(Math.abs(g.kpi1 - media)).replace("%", "")} p.p. vs. média SC</div>
              </div>
              <div className="celula" style={{ borderBottom: "1px solid var(--linha)" }}>
                <div className="muted" style={{ fontSize: 12 }}>Saldo em 12 meses</div>
                <div className="num" style={{ fontSize: 30, lineHeight: 1.15, fontWeight: 600 }}>{sinalInt(g.saldo)}</div>
                <div style={{ display: "inline-flex", alignItems: "center", gap: 6, marginTop: 8, fontSize: 12 }}>
                  <span className="ponto-cor" style={{ background: cresce ? "var(--expansao)" : "var(--sinal)" }} />vagas · {cresce ? "cresce" : "encolhe"}
                </div>
              </div>
            </div>
            {sg && (
              <div className="celula" style={{ borderBottom: "1px solid var(--linha)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <span className="muted" style={{ fontSize: 12 }}>Salário mediano · entra × sai</span>
                  <span className="num" style={{ fontSize: 15, fontWeight: 600 }}>−{pct(Math.abs(gap))} para quem entra</span>
                </div>
                <div role="img" aria-label={`Quem entra ganha ${reais(sg.admitidos)}, quem sai ganhava ${reais(sg.desligados)}`} style={{ position: "relative", height: 18, margin: "10px 6px 0" }}>
                  <div style={{ position: "absolute", left: 0, right: 0, top: 8, height: 2, background: "var(--linha)" }} />
                  <div style={{ position: "absolute", top: 8, height: 2, background: "var(--tinta2)", left: `${pos(sg.admitidos)}%`, width: `${pos(sg.desligados) - pos(sg.admitidos)}%` }} />
                  <div style={{ position: "absolute", top: 4, width: 10, height: 10, marginLeft: -5, borderRadius: "50%", background: "var(--sinal)", left: `${pos(sg.admitidos)}%` }} />
                  <div style={{ position: "absolute", top: 4, width: 10, height: 10, marginLeft: -5, borderRadius: "50%", background: "var(--neutro)", left: `${pos(sg.desligados)}%` }} />
                </div>
                <div className="num" style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginTop: 4 }}>
                  <span><span style={{ color: "var(--sinal)" }}>●</span> Entra {reais(sg.admitidos)}</span><span><span style={{ color: "var(--neutro)" }}>●</span> Sai {reais(sg.desligados)}</span>
                </div>
              </div>
            )}
            <div className="celula">
              <div className="muted" style={{ fontSize: 12 }}>Quadrante</div>
              <div className="quad-grade" role="img" aria-label={`Quadrante: ${QUAD[quad].nome}`}>
                <span className="vert">perde mais</span>
                {["ex", "re"].map((k) => <div key={k} className="q-cel" style={k === quad ? { background: QUAD[k].cor, color: QUAD[k].fg, borderColor: QUAD[k].cor } : {}}>{QUAD[k].nome}</div>)}
                <span className="vert">retém</span>
                {["cr", "es"].map((k) => <div key={k} className="q-cel" style={k === quad ? { background: QUAD[k].cor, color: QUAD[k].fg, borderColor: QUAD[k].cor } : {}}>{QUAD[k].nome}</div>)}
                <span /><span className="hor">cresce</span><span className="hor">encolhe</span>
              </div>
              <p className="muted" style={{ fontSize: 11.5, margin: "8px 0 0" }}>Corte do setor: saldo acima/abaixo de zero × saídas a pedido acima/abaixo de {pct(media)}.</p>
              <button className="btn-escuro" style={{ width: "100%", marginTop: 12 }}
                onClick={() => abrir(qaSetor(g, sg, media, cur.curto), { ...ctx, texto: `Capítulo 3, setores · ${cur.curto}`, setor: g.grupo })}>
                <Balao size={16} cor="#fff" />Perguntar sobre este setor
              </button>
            </div>
          </article>
        </div>
      </div>

      <aside className="destaque" style={{ margin: "36px var(--margem) 0" }}>
        <div className="eyebrow">Destaque</div>
        <div className="v num">{pct(partAlim, 0)}</div>
        <p style={{ margin: "8px 0 0", fontSize: 15.5, lineHeight: 1.45, maxWidth: 560 }}>de todas as movimentações são de uma única ocupação: o <b>alimentador de linha de produção</b>.</p>
        <div role="img" aria-label={`${pct(partAlim, 0)} das movimentações`} style={{ display: "flex", gap: 2, height: 8, marginTop: 14, maxWidth: 560 }}>
          <div style={{ width: `${partAlim}%`, borderRadius: "4px 0 0 4px", background: "var(--sinal)" }} /><div style={{ flex: 1, borderRadius: "0 4px 4px 0", background: "var(--tinta2)" }} />
        </div>
        <p className="num" style={{ margin: "14px 0 0", paddingTop: 12, borderTop: "1px solid var(--tinta2)", fontSize: 14.5, maxWidth: 560 }}>
          Sem ela, o saldo seria <b style={{ fontSize: 17 }}>{sinalInt(tSem.saldo)}</b> em vez de {sinalInt(t.saldo)}.
        </p>
        <div style={{ maxWidth: 560 }}><Pergunte titulo="" itens={[QA.setores[2]]} contexto={ctx} /></div>
      </aside>

      <ProximoCapitulo cap="setores" />
    </>
  );
}
