import { useMemo, useState } from "react";
import { geoMercator, geoPath } from "d3-geo";
import { scaleLinear } from "d3-scale";
import { interpolateLab } from "d3-interpolate";
import { Tooltip, dec, int, pct, sinal, sinalInt, useEscuro, useTooltip } from "../fmt.jsx";

const L = 640, A = 400;

// Sequencial de um tom (vermelho) para "% a pedido"; divergente vermelho–cinza–azul para o saldo.
const PALETAS = {
  claro: { seq: ["#f7e4e1", "#b4302f"], neg: "#c53b3a", meio: "#f0efec", pos: "#1c5cab", insuf: "#ecebe6", borda: "#fcfcfb" },
  escuro: { seq: ["#3b2a29", "#f07170"], neg: "#e66767", meio: "#383835", pos: "#5598e7", insuf: "#262624", borda: "#1a1a19" },
};

export default function Mapa({ geo, micros, refKpi1 }) {
  const [kpi, setKpi] = useState("kpi1");
  const [foco, setFoco] = useState(null);
  const escuro = useEscuro();
  const p = escuro ? PALETAS.escuro : PALETAS.claro;
  const { tip, mostrar, esconder } = useTooltip();

  const porCod = useMemo(() => Object.fromEntries(micros.map((m) => [m.cod, m])), [micros]);
  const caminho = useMemo(() => geoPath(geoMercator().fitSize([L, A], geo)), [geo]);

  const ok = (m) => (kpi === "kpi1" ? m.kpi1_ok : m.kpi2_ok);
  const vals = micros.filter(ok).map((m) => m[kpi]);
  const cor = useMemo(() => {
    if (kpi === "kpi1") {
      return scaleLinear().domain([Math.min(...vals), Math.max(...vals)]).range(p.seq).interpolate(interpolateLab);
    }
    const lim = Math.max(...vals.map(Math.abs));
    return scaleLinear().domain([-lim, 0, lim]).range([p.neg, p.meio, p.pos]).interpolate(interpolateLab);
  }, [kpi, escuro, micros]);

  const ordenadas = [...micros].sort((a, b) => b[kpi] - a[kpi]);
  const topo = ordenadas[0], fundo = ordenadas[ordenadas.length - 1];
  const titulo = kpi === "kpi1"
    ? `${topo.nome} lidera: ${pct(topo.kpi1)} das saídas são a pedido`
    : `${topo.nome} é o polo de expansão (${sinal(topo.kpi2)} por 10 mil hab.); ${fundo.nome} é o que mais encolhe (${sinal(fundo.kpi2)})`;
  const maxAbs = Math.max(...micros.map((m) => Math.abs(m[kpi] - (kpi === "kpi1" ? refKpi1 : 0))));

  const conteudoTip = (m) => (
    <>
      <b>{m.nome}</b>
      <div className="t-sub">{m.meso}</div>
      <div className="linha"><span>Saídas a pedido</span><span>{pct(m.kpi1)}</span></div>
      <div className="linha"><span>Saldo por 10 mil hab.</span><span>{sinal(m.kpi2)}</span></div>
      <div className="linha"><span>Saldo em 12 meses</span><span>{sinalInt(m.saldo)}</span></div>
      <div className="linha"><span>Movimentações</span><span>{int(m.movimentos)}</span></div>
    </>
  );

  return (
    <div className="mapa-grid">
      <div className="cartao">
        <div className="segmentado" role="group" aria-label="Indicador do mapa">
          <button aria-pressed={kpi === "kpi1"} onClick={() => setKpi("kpi1")}>Saídas a pedido · apagão</button>
          <button aria-pressed={kpi === "kpi2"} onClick={() => setKpi("kpi2")}>Saldo por 10 mil hab. · expansão</button>
        </div>
        <h3>{titulo}</h3>
        <p className="sub">Indústria de transformação por microrregião do IBGE · 12 meses</p>
        <svg viewBox={`0 0 ${L} ${A}`} role="img" aria-label={titulo} onMouseLeave={() => { esconder(); setFoco(null); }}>
          {geo.features.map((f) => {
            const m = porCod[f.properties.codarea];
            const preench = m && ok(m) ? cor(m[kpi]) : p.insuf;
            return (
              <path key={f.properties.codarea} d={caminho(f)} fill={preench}
                stroke={foco === f.properties.codarea ? "var(--ink)" : p.borda}
                strokeWidth={foco === f.properties.codarea ? 2 : 1.2} strokeLinejoin="round"
                onMouseMove={(e) => { if (m) { mostrar(e, conteudoTip(m)); setFoco(m.cod); } }} />
            );
          })}
        </svg>
        <div className="gradiente" aria-hidden="true">
          {kpi === "kpi1" ? (
            <>
              <span>{pct(Math.min(...vals), 0)}</span>
              <span className="faixa" style={{ background: `linear-gradient(90deg, ${p.seq[0]}, ${p.seq[1]})` }} />
              <span>{pct(Math.max(...vals), 0)} das saídas a pedido</span>
            </>
          ) : (
            <>
              <span>encolhe</span>
              <span className="faixa" style={{ background: `linear-gradient(90deg, ${p.neg}, ${p.meio}, ${p.pos})` }} />
              <span>cresce</span>
            </>
          )}
        </div>
        <Tooltip tip={tip} />
      </div>

      <div className="cartao">
        <h3>{kpi === "kpi1" ? "Ranking: % das saídas a pedido" : "Ranking: saldo por 10 mil habitantes"}</h3>
        <p className="sub">{kpi === "kpi1" ? `Barra = distância da média de SC (${pct(refKpi1)})` : "Barra = saldo de 12 meses por 10 mil habitantes"}</p>
        <ol className="ranking">
          {ordenadas.map((m) => {
            const d = m[kpi] - (kpi === "kpi1" ? refKpi1 : 0);
            const w = (Math.abs(d) / maxAbs) * 50;
            const destaque = kpi === "kpi1" ? (d > 0 ? "var(--alerta)" : "var(--cinza-1)") : (d > 0 ? "var(--azul)" : "var(--alerta)");
            return (
              <li key={m.cod} className={foco === m.cod ? "ativo" : ""}
                onMouseEnter={() => setFoco(m.cod)} onMouseLeave={() => setFoco(null)}>
                <span className="nome" title={`${m.nome} · ${m.meso}`}>{m.nome}</span>
                <span className="trilho" aria-hidden="true">
                  <b className={d < 0 ? "neg" : ""} style={{ width: `${w}%`, left: d < 0 ? `${50 - w}%` : "50%", background: destaque }} />
                  <span style={{ position: "absolute", left: "50%", top: -2, bottom: -2, width: 1, background: "var(--axis)" }} />
                </span>
                <span className="num">{kpi === "kpi1" ? pct(m.kpi1) : sinal(m.kpi2)}</span>
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
