import { Tooltip, int, pct, sinalInt, useTooltip } from "../fmt.jsx";

// Small multiples: % a pedido (de 0) e saldo (divergente em 0), mesma ordem de linhas. Nunca dois eixos no mesmo plot.
const LARG = 760, ROTULO = 210, PAINEL = 230, VAO = 60, LINHA = 30, TOPO = 28;

export default function Setores({ grupos, refKpi1 }) {
  const { tip, mostrar, esconder } = useTooltip();
  const d = [...grupos].filter((g) => g.kpi1_ok).sort((a, b) => b.kpi1 - a.kpi1);
  const maxK1 = Math.max(...d.map((g) => g.kpi1)) * 1.1;
  const maxSaldo = Math.max(...d.map((g) => Math.abs(g.saldo)));
  const x1 = (v) => ROTULO + (v / maxK1) * PAINEL;
  const x2c = ROTULO + PAINEL + VAO + PAINEL / 2;
  const x2 = (v) => x2c + (v / maxSaldo) * (PAINEL / 2);
  const altura = TOPO + d.length * LINHA + 8;

  const crescemPerdem = d.filter((g) => g.saldo > 0 && g.kpi1 > refKpi1).map((g) => g.grupo);
  const encolhemPerdem = d.filter((g) => g.saldo < 0 && g.kpi1 > refKpi1).map((g) => g.grupo);
  const titulo = `${crescemPerdem.join(" e ")} cresce${crescemPerdem.length > 1 ? "m" : ""} e perde${crescemPerdem.length > 1 ? "m" : ""} gente; ${encolhemPerdem.join(" e ")} encolhe${encolhemPerdem.length > 1 ? "m" : ""} e perde${encolhemPerdem.length > 1 ? "m" : ""} gente`;

  const tipo = (g) => (
    <>
      <b>{g.grupo}</b>
      <div className="linha"><span>Saídas a pedido</span><span>{pct(g.kpi1)}</span></div>
      <div className="linha"><span>Saldo em 12 meses</span><span>{sinalInt(g.saldo)}</span></div>
      <div className="linha"><span>Desligamentos</span><span>{int(g.desligamentos)}</span></div>
      <div className="linha"><span>Sem o alimentador de linha</span><span>{pct(g.kpi1_sem)}</span></div>
    </>
  );

  // barra horizontal com ponta arredondada de 4px, quadrada na base
  const barra = (x0, x1v, y, h, cor) => {
    const esq = Math.min(x0, x1v), w = Math.abs(x1v - x0), r = Math.min(4, w);
    const dir = x1v >= x0;
    const p = dir
      ? `M${esq},${y} h${w - r} q${r},0 ${r},${r} v${h - 2 * r} q0,${r} -${r},${r} h-${w - r} z`
      : `M${esq + w},${y} h-${w - r} q-${r},0 -${r},${r} v${h - 2 * r} q0,${r} ${r},${r} h${w - r} z`;
    return w > 0 ? <path d={p} fill={cor} /> : null;
  };

  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      <p className="sub">Grupos setoriais da transformação · ordenados pelo % de saídas a pedido · vermelho = acima da média de SC ou encolhendo</p>
      <div className="rola"><svg className="largo" viewBox={`0 0 ${LARG} ${altura}`} role="img" aria-label={titulo} onMouseLeave={esconder}>
        <text x={ROTULO} y={14} style={{ fontWeight: 600, fill: "var(--ink)" }}>% das saídas a pedido</text>
        <text x={ROTULO + PAINEL + VAO} y={14} style={{ fontWeight: 600, fill: "var(--ink)" }}>Saldo em 12 meses (vagas)</text>
        <line className="base" x1={ROTULO} x2={ROTULO} y1={TOPO - 6} y2={altura - 4} />
        <line className="base" x1={x2c} x2={x2c} y1={TOPO - 6} y2={altura - 4} />
        <line className="ref" x1={x1(refKpi1)} x2={x1(refKpi1)} y1={TOPO - 6} y2={altura - 4} />
        <text className="eixo" x={x1(refKpi1) + 4} y={TOPO - 8}>SC {pct(refKpi1)}</text>
        {d.map((g, i) => {
          const y = TOPO + i * LINHA;
          const h = 14, yb = y + (LINHA - h) / 2;
          return (
            <g key={g.grupo} onMouseMove={(e) => mostrar(e, tipo(g))}>
              <rect x={0} y={y} width={LARG} height={LINHA} fill="transparent" />
              <text x={ROTULO - 10} y={y + LINHA / 2 + 4} textAnchor="end" style={{ fill: "var(--ink)" }}>{g.grupo}</text>
              {barra(ROTULO, x1(g.kpi1), yb, h, g.kpi1 > refKpi1 ? "var(--alerta)" : "var(--cinza-1)")}
              <text x={x1(g.kpi1) + 6} y={y + LINHA / 2 + 4} className="eixo halo" style={{ fill: "var(--ink-2)" }}>{pct(g.kpi1)}</text>
              {barra(x2c, x2(g.saldo), yb, h, g.saldo < 0 ? "var(--alerta)" : "var(--azul)")}
              <text x={g.saldo >= 0 ? x2(g.saldo) + 6 : x2(g.saldo) - 6} y={y + LINHA / 2 + 4}
                textAnchor={g.saldo >= 0 ? "start" : "end"} className="eixo" style={{ fill: "var(--ink-2)" }}>{sinalInt(g.saldo)}</text>
            </g>
          );
        })}
      </svg></div>
      <Tooltip tip={tip} />
    </div>
  );
}
