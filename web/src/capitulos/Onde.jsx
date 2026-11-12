// Capítulo 2 — Onde (Tela2-Onde.dc.html / Desktop2-Onde.dc.html). Contorno real das microrregiões (IBGE).
import { useEffect, useMemo, useState } from "react";
import { geoMercator, geoPath } from "d3-geo";
import { QA, qaRegiao } from "../qa.js";
import { Balao, Fechar, Folha, Pergunte, ProximoCapitulo, Seletor, useVisto } from "../componentes/base.jsx";
import { useAssistente } from "../componentes/Assistente.jsx";
import { int, pct, sinal, sinalInt } from "../fmt.jsx";

const W = 352, H = 246;
const SEQ = [[45, "#F3E3DF", "< 45%"], [50, "#EDB9A8", "45–50%"], [55, "#E38A72", "50–55%"], [60, "#D63F2C", "55–60%"], [999, "#A12A1C", "≥ 60%"]];
const DIV = [[-25, "#D63F2C", "< −25"], [-5, "#EBA593", "−25 a −5"], [5, "#E9EBEE", "−5 a 5"], [25, "#96B0D8", "5 a 25"], [999, "#2D5DA8", "> 25"]];
const faixa = (v, bins) => (bins.find((b) => v < b[0]) || bins[bins.length - 1])[1];

export function useDesktop() {
  const q = typeof window !== "undefined" ? window.matchMedia("(min-width: 960px)") : null;
  const [d, setD] = useState(q ? q.matches : false);
  useEffect(() => {
    if (!q) return;
    const f = (e) => setD(e.matches);
    q.addEventListener("change", f);
    return () => q.removeEventListener("change", f);
  }, []);
  return d;
}

function Ficha({ m, media, onFechar, desktop }) {
  const { abrir } = useAssistente();
  const acima = m.kpi1 > media, cresce = m.kpi2 > 0;
  const leitura = (acima ? "Perde mais gente que a média de SC" : "Perde menos gente que a média de SC") + (cresce ? " e a indústria cresce." : " e a indústria encolhe.");
  const ctx = { cap: "onde", texto: `Capítulo 2, mapa · ${m.nome}`, regiao: m.nome };
  return (
    <div style={desktop ? {} : { padding: "8px 16px 16px" }} aria-live={desktop ? "polite" : undefined}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12, padding: desktop ? "20px 20px 16px" : 0 }}>
        <div>
          <div className="muted" style={{ fontSize: 12 }}>Microrregião · {m.meso}</div>
          <div style={{ fontSize: desktop ? 26 : 22, lineHeight: 1.2, fontWeight: 600 }}>{m.nome}</div>
        </div>
        {!desktop && <button className="icone-btn" onClick={onFechar} aria-label="Fechar" style={{ margin: "-6px -8px 0 0" }}><Fechar /></button>}
      </div>
      <div className="dupla" style={desktop ? { gap: 0, borderTop: "1px solid var(--linha)" } : { marginTop: 12 }}>
        <div className="caixa-num" style={desktop ? { background: "none", borderRadius: 0, borderRight: "1px solid var(--linha)", padding: "16px 20px" } : {}}>
          <div className="r">Saídas a pedido</div>
          <div className="v num">{pct(m.kpi1)}</div>
          <div className="mini-barra"><div style={{ width: `${(m.kpi1 / 70) * 100}%`, background: acima ? "var(--sinal)" : "var(--neutro)" }} /><div className="media" style={{ left: `${(media / 70) * 100}%` }} /></div>
          <div className="muted num" style={{ fontSize: 11.5, marginTop: 6 }}>{m.kpi1 >= media ? "+" : "−"}{pct(Math.abs(m.kpi1 - media)).replace("%", "")} p.p. vs. média SC</div>
        </div>
        <div className="caixa-num" style={desktop ? { background: "none", borderRadius: 0, padding: "16px 20px" } : {}}>
          <div className="r">Saldo /10 mil hab.</div>
          <div className="v num">{sinal(m.kpi2)}</div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, marginTop: 8, fontSize: 12 }}>
            <span className="ponto-cor" style={{ background: cresce ? "var(--expansao)" : "var(--sinal)" }} />{cresce ? "cresce" : "encolhe"} · {sinalInt(m.saldo)} vagas
          </div>
        </div>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", padding: desktop ? "12px 20px" : "10px 0", marginTop: desktop ? 0 : 4, borderTop: desktop ? "1px solid var(--linha)" : 0, borderBottom: desktop ? 0 : "1px solid var(--linha)", fontSize: 14 }}>
        <span style={{ color: "var(--tinta2)" }}>Movimentações (12 meses)</span><span className="num" style={{ fontWeight: 600 }}>{int(m.movimentos)}</span>
      </div>
      <p style={desktop ? { margin: 0, padding: "14px 20px", borderTop: "1px solid var(--linha)", fontSize: 15, lineHeight: 1.45, background: "var(--superficie)" } : { margin: "10px 0 0", fontSize: 14.5, lineHeight: 1.4 }}>{leitura}</p>
      <div style={{ display: "flex", gap: 8, padding: desktop ? "14px 20px 18px" : 0, marginTop: desktop ? 0 : 10, borderTop: desktop ? "1px solid var(--linha)" : 0 }}>
        <a className="btn-claro" href="#/setores" style={{ flex: 1 }}>Ver setores</a>
        <button className="btn-escuro" style={{ flex: 1 }} onClick={() => { onFechar?.(); abrir(qaRegiao(m, media), ctx); }}><Balao size={16} cor="#fff" />Perguntar</button>
      </div>
    </div>
  );
}

export default function Onde({ dados, geo }) {
  const desktop = useDesktop();
  const [modo, setModo] = useState("apagao");
  const micros = dados.microrregioes;
  const [sel, setSel] = useState(() => (micros.find((x) => x.nome === "Chapecó") || micros[0]).cod); // mesmo padrão do design
  const [ficha, setFicha] = useState(false);
  const [refRank, classeRank] = useVisto();
  const media = dados.segmentos.find((s) => s.segmento === "Transformação").kpi1;
  const porCod = useMemo(() => Object.fromEntries(micros.map((m) => [m.cod, m])), [micros]);
  const proj = useMemo(() => geoMercator().fitExtent([[4, 4], [W - 4, H - 4]], geo), [geo]);
  const caminho = useMemo(() => geoPath(proj), [proj]);
  const centro = (cod) => { const f = geo.features.find((x) => x.properties.codarea === cod); return f ? caminho.centroid(f) : [0, 0]; };
  const isA = modo === "apagao";
  const m = porCod[sel];
  const pin = centro(sel);
  const [oeste, vale] = [centro(micros.find((x) => x.nome === "São Miguel do Oeste")?.cod), centro(micros.find((x) => x.nome === "Blumenau")?.cod)];

  const ordem = [...micros].sort((a, b) => (isA ? b.kpi1 - a.kpi1 : b.kpi2 - a.kpi2));
  const maxAbs = Math.max(...micros.map((x) => Math.abs(x.kpi2)));
  const topoSaldo = [...micros].sort((a, b) => b.kpi2 - a.kpi2);
  const titRank = isA ? `${ordem[0].nome} lidera as saídas a pedido` : `${topoSaldo[0].nome} é a que mais cresce; ${topoSaldo[topoSaldo.length - 1].nome}, a que mais encolhe`;
  const escolher = (cod) => { setSel(cod); if (!desktop) setFicha(true); };
  const ctx = { cap: "onde", texto: "Capítulo 2, mapa" };

  const mapa = (
    <figure className="mapa">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={isA ? "Mapa de SC: % de saídas a pedido por microrregião" : "Mapa de SC: saldo de empregos por 10 mil habitantes"}>
        <g strokeLinejoin="round">
          {geo.features.map((f) => {
            const r = porCod[f.properties.codarea];
            const on = f.properties.codarea === sel && (ficha || desktop);
            return r ? (
              <path key={f.properties.codarea} className="reg" d={caminho(f)} fill={isA ? faixa(r.kpi1, SEQ) : faixa(r.kpi2, DIV)}
                stroke={on ? "#14171C" : "#FFFFFF"} strokeWidth={on ? (desktop ? 0.9 : 1.6) : desktop ? 0.45 : 0.7}
                onClick={() => escolher(r.cod)} onMouseEnter={desktop ? () => setSel(r.cod) : undefined}>
                <title>{`${r.nome}: ${pct(r.kpi1)} a pedido, ${sinal(r.kpi2)} por 10 mil hab.`}</title>
              </path>
            ) : null;
          })}
        </g>
        {(() => {
          // Rótulos no espaço vazio abaixo do Oeste (divisa com o RS), com linhas-guia até as regiões.
          const fs = desktop ? 6.5 : 9.5, lh = fs * 1.15;
          const yO = H * 0.6, yV = H * 0.84, xV = W * 0.1;
          const fimV = xV + (desktop ? 58 : 84);
          return (
            <>
              <g aria-hidden="true" fill="none" stroke="var(--tinta3)" strokeWidth={desktop ? 0.5 : 0.8}>
                <path d={`M${oeste[0]} ${yO - fs - 2} L${oeste[0]} ${oeste[1] + 8}`} />
                <path d={`M${fimV} ${yV - fs / 3} C ${vale[0] - 70} ${yV - fs / 3}, ${vale[0] - 20} ${vale[1] + 50}, ${vale[0]} ${vale[1] + 6}`} />
              </g>
              <g aria-hidden="true" fontFamily="IBM Plex Sans, sans-serif" fontSize={fs} fill="#14171C">
                <text className="halo" x={4} y={yO} fontWeight="600">Oeste</text>
                <text className="halo" x={4} y={yO + lh} fill="#3A404B">cresce e perde gente</text>
                <text className="halo" x={xV} y={yV} fontWeight="600">Vale do Itajaí</text>
                <text className="halo" x={xV} y={yV + lh} fill="#3A404B">encolhe e perde gente</text>
              </g>
            </>
          );
        })()}
        {(ficha || desktop) && <circle cx={pin[0]} cy={pin[1]} r={desktop ? 3 : 4.5} fill="#14171C" stroke="#fff" strokeWidth={desktop ? 1.2 : 2} />}
        {desktop && m && (
          <text className="halo" x={pin[0] + (pin[0] > W * 0.7 ? -6 : 6)} y={pin[1] - 6} textAnchor={pin[0] > W * 0.7 ? "end" : "start"}
            fontFamily="IBM Plex Sans, sans-serif" fontSize="6.5" fontWeight="600" fill="#14171C" aria-hidden="true">
            {m.nome}: {isA ? pct(m.kpi1) : sinal(m.kpi2)}
          </text>
        )}
      </svg>
      <figcaption className="muted" style={{ fontSize: 12, marginTop: 6 }}>
        Microrregiões do IBGE. {desktop ? "Passe o mouse ou clique numa região." : "Toque numa região para ver os números."}
      </figcaption>
      <div style={{ marginTop: 14, maxWidth: 520 }}>
        <div style={{ fontSize: 12.5, fontWeight: 500, color: "var(--tinta2)", marginBottom: 6 }}>
          {isA ? "% dos desligamentos a pedido" : "Saldo por 10 mil hab. · vermelho encolhe, azul cresce"}
        </div>
        <div className="legenda-mapa">
          {(isA ? SEQ : DIV).map((b) => <div key={b[2]}><div className="cor" style={{ background: b[1] }} /><div className="t num">{b[2]}</div></div>)}
        </div>
      </div>
    </figure>
  );

  const seletor = (
    <Seletor rotulo="Indicador do mapa" valor={modo} onChange={setModo}
      opcoes={[{ v: "apagao", t: "Saídas a pedido", s: "apagão" }, { v: "saldo", t: "Saldo por 10 mil hab.", s: "expansão" }]} />
  );

  return (
    <>
      <div className="abre" style={desktop ? { display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24, alignItems: "end" } : {}}>
        <div>
          <div className="eyebrow">Onde{desktop ? " · 20 microrregiões" : ""}</div>
          <h1>O Oeste cresce e perde gente; o Vale do Itajaí encolhe e perde gente.</h1>
        </div>
        {desktop && seletor}
      </div>
      {!desktop && <div style={{ margin: "20px 16px 0" }}>{seletor}</div>}

      {desktop ? (
        <section className="bloco" style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 24, marginTop: 28, alignItems: "start" }}>
          <div>{mapa}<Pergunte titulo="Pergunte sobre este mapa" itens={QA.onde.slice(0, 2)} caixa contexto={ctx} /></div>
          <aside className="cartao" style={{ position: "sticky", top: 92 }}>{m && <Ficha m={m} media={media} desktop />}</aside>
        </section>
      ) : (
        <>
          <div className="bloco" style={{ marginTop: 18 }}>{mapa}</div>
          <div className="bloco"><Pergunte titulo="Pergunte sobre este mapa" itens={QA.onde.slice(0, 2)} caixa contexto={ctx} /></div>
        </>
      )}

      <section className="bloco" style={{ marginTop: 36 }}>
        <div className="eyebrow">Ranking</div>
        <h2 className="graf">{titRank}</h2>
        <div className="sub-graf">{isA ? "% dos desligamentos a pedido, por microrregião" : "Saldo de empregos por 10 mil habitantes"}</div>
        <ol ref={refRank} className={`linhas ${classeRank}`} style={{ listStyle: "none", margin: "12px 0 0", padding: 0, ...(desktop ? { display: "grid", gridTemplateColumns: "1fr 1fr", gridAutoFlow: "column", gridTemplateRows: "repeat(10, auto)", columnGap: 48 } : {}) }}>
          {ordem.map((r, i) => {
            const w = isA ? (r.kpi1 / 70) * 100 : (Math.abs(r.kpi2) / maxAbs) * 50;
            const left = isA ? 0 : r.kpi2 >= 0 ? 50 : 50 - w;
            return (
              <li key={r.cod}>
                <button className="linha-btn" onClick={() => escolher(r.cod)} onMouseEnter={desktop ? () => setSel(r.cod) : undefined}
                  style={{ gridTemplateColumns: desktop ? "26px 170px 1fr 64px" : "22px 118px 1fr 52px", background: r.cod === sel && desktop ? "var(--superficie)" : undefined }}>
                  <span className="num muted" style={{ fontSize: 12 }}>{String(i + 1).padStart(2, "0")}</span>
                  <span style={{ fontSize: 14, lineHeight: 1.2 }}>{r.nome}</span>
                  <span className="trilho-barra" aria-hidden="true">
                    <span className="media" style={{ left: `${isA ? (media / 70) * 100 : 50}%` }} />
                    <span className={`b${!isA && r.kpi2 < 0 ? " neg" : ""}`} style={{ "--i": i, left: `${left}%`, width: `${w}%`, background: isA ? (r.kpi1 > media ? "var(--sinal)" : "var(--neutro-claro)") : r.kpi2 >= 0 ? "var(--expansao)" : "var(--sinal)" }} />
                  </span>
                  <span className="v num">{isA ? pct(r.kpi1) : sinal(r.kpi2)}</span>
                </button>
              </li>
            );
          })}
        </ol>
        <p className="nota-graf">{isA ? `Linha tracejada: média de SC (${pct(media)}). Vermelho: acima da média.` : "Linha tracejada: zero. Azul cresce, vermelho encolhe."}</p>
        <Pergunte titulo="" itens={[QA.onde[2]]} contexto={ctx} />
        <p className="fonte" style={{ marginTop: 16 }}>Fonte: Novo CAGED (MTE), indústria de transformação, set/2025 a ago/2026. Microrregiões: IBGE.</p>
      </section>

      <ProximoCapitulo cap="onde" />

      {!desktop && (
        <Folha aberta={ficha && !!m} onFechar={() => setFicha(false)} rotulo={m ? m.nome : "Microrregião"}>
          {m && <Ficha m={m} media={media} onFechar={() => setFicha(false)} />}
        </Folha>
      )}
    </>
  );
}
