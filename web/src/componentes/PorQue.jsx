import { Tooltip, dec, int, pct, reais, sinal, sinalInt, useTooltip } from "../fmt.jsx";

const NIVEL = { "Qualificação até 200h": "até 200h", "Qualificação acima de 200h": "acima de 200h", "Técnico": "técnico", "Superior": "superior" };

function barraH(x0, x1, y, h, cor) {
  const w = Math.max(0, x1 - x0), r = Math.min(4, w);
  return <path d={`M${x0},${y} h${w - r} q${r},0 ${r},${r} v${h - 2 * r} q0,${r} -${r},${r} h-${w - r} z`} fill={cor} />;
}

/** KPI 1 por macrofamília (área × nível gerados pela IA). */
export function Macrofamilias({ macros, refKpi1 }) {
  const { tip, mostrar, esconder } = useTooltip();
  const d = macros.filter((m) => m.kpi1_ok).sort((a, b) => b.desligamentos - a.desligamentos).slice(0, 12)
    .sort((a, b) => b.kpi1 - a.kpi1);
  const L = 860, ROT = 300, LIN = 28, TOPO = 24, A = TOPO + d.length * LIN + 6;
  const max = Math.max(...d.map((m) => m.kpi1)) * 1.18;
  const x = (v) => ROT + (v / max) * (L - ROT - 10);
  const topo = d[0];
  const titulo = `${topo.area} (${NIVEL[topo.nivel]}) lidera: ${pct(topo.kpi1)} saem a pedido`;
  const tipo = (m) => (
    <>
      <b>{m.area}</b>
      <div className="t-sub">Nível: {m.nivel}</div>
      <div className="linha"><span>Saídas a pedido</span><span>{pct(m.kpi1)}</span></div>
      <div className="linha"><span>Desligamentos</span><span>{int(m.desligamentos)}</span></div>
      <div className="linha"><span>Saldo em 12 meses</span><span>{sinalInt(m.saldo)}</span></div>
      {m.kpi3 != null && <div className="linha"><span>Prêmio de contratação</span><span>{dec(m.kpi3, 3)}</span></div>}
    </>
  );
  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      <p className="sub">As 12 macrofamílias com mais desligamentos · área × nível de formação classificados pela IA</p>
      <div className="rola"><svg className="largo" viewBox={`0 0 ${L} ${A}`} role="img" aria-label={titulo} onMouseLeave={esconder}>
        <line className="base" x1={ROT} x2={ROT} y1={TOPO - 6} y2={A - 2} />
        <line className="ref" x1={x(refKpi1)} x2={x(refKpi1)} y1={TOPO - 6} y2={A - 2} />
        <text className="eixo" x={x(refKpi1) + 4} y={TOPO - 10}>SC {pct(refKpi1)}</text>
        {d.map((m, i) => {
          const y = TOPO + i * LIN;
          return (
            <g key={m.area + m.nivel} onMouseMove={(e) => mostrar(e, tipo(m))}>
              <rect x={0} y={y} width={L} height={LIN} fill="transparent" />
              <text x={ROT - 8} y={y + LIN / 2 + 4} textAnchor="end" style={{ fill: "var(--ink)" }}>
                {m.area}
                <tspan style={{ fill: "var(--muted)" }}> · {NIVEL[m.nivel]}</tspan>
              </text>
              {barraH(ROT, x(m.kpi1), y + 7, 14, m.kpi1 > refKpi1 ? "var(--alerta)" : "var(--cinza-1)")}
              <text className="eixo halo" x={x(m.kpi1) + 6} y={y + LIN / 2 + 4} style={{ fill: "var(--ink-2)" }}>{pct(m.kpi1)}</text>
            </g>
          );
        })}
      </svg></div>
      <Tooltip tip={tip} />
    </div>
  );
}

/** Salário mediano de admissão × desligamento por setor (haltere). */
export function Salario({ salarios, premio }) {
  const { tip, mostrar, esconder } = useTooltip();
  const d = [...salarios].sort((a, b) => (a.admitidos / a.desligados) - (b.admitidos / b.desligados));
  const L = 480, ROT = 190, LIN = 26, TOPO = 24, A = TOPO + d.length * LIN + 26;
  const vals = d.flatMap((s) => [s.admitidos, s.desligados]);
  const min = Math.floor(Math.min(...vals) / 100) * 100 - 50, max = Math.ceil(Math.max(...vals) / 100) * 100 + 50;
  const x = (v) => ROT + ((v - min) / (max - min)) * (L - ROT - 16);
  const menos = d.filter((s) => s.admitidos < s.desligados).length;
  const titulo = menos === d.length ? `Em todos os ${d.length} setores, quem entra ganha menos que quem sai`
    : `Em ${menos} de ${d.length} setores, quem entra ganha menos que quem sai`;
  const ticks = []; for (let t = Math.ceil(min / 200) * 200; t <= max; t += 200) ticks.push(t);
  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      <p className="sub">Salário mediano · celetistas comuns, R$ 1.000 a R$ 30.000 · na mesma ocupação e região, a reposição paga {pct(100 * (1 - premio))} menos (prêmio {dec(premio, 3)})</p>
      <div className="legenda">
        <span><i style={{ background: "var(--azul)" }} />Admitidos</span>
        <span><i style={{ background: "var(--cinza-1)" }} />Desligados</span>
      </div>
      <svg viewBox={`0 0 ${L} ${A}`} role="img" aria-label={titulo} onMouseLeave={esconder}>
        {ticks.map((t) => (
          <g key={t}>
            <line className="grade" x1={x(t)} x2={x(t)} y1={TOPO - 8} y2={A - 22} />
            <text className="eixo" x={x(t)} y={A - 6} textAnchor="middle">{int(t)}</text>
          </g>
        ))}
        {d.map((s, i) => {
          const y = TOPO + i * LIN + LIN / 2;
          return (
            <g key={s.grupo} onMouseMove={(e) => mostrar(e, (
              <>
                <b>{s.grupo}</b>
                <div className="linha"><span>Admitidos</span><span>{reais(s.admitidos)}</span></div>
                <div className="linha"><span>Desligados</span><span>{reais(s.desligados)}</span></div>
                <div className="linha"><span>Diferença</span><span>{sinal(100 * (s.admitidos / s.desligados - 1))}%</span></div>
              </>))}>
              <rect x={0} y={y - LIN / 2} width={L} height={LIN} fill="transparent" />
              <text x={ROT - 10} y={y + 4} textAnchor="end" style={{ fill: "var(--ink)" }}>{s.grupo.length > 28 ? `${s.grupo.slice(0, 27)}…` : s.grupo}</text>
              <line x1={x(s.admitidos)} x2={x(s.desligados)} y1={y} y2={y} stroke="var(--axis)" strokeWidth={2} />
              <circle cx={x(s.desligados)} cy={y} r={5} fill="var(--cinza-1)" stroke="var(--surface)" strokeWidth={2} />
              <circle cx={x(s.admitidos)} cy={y} r={5} fill="var(--azul)" stroke="var(--surface)" strokeWidth={2} />
            </g>
          );
        })}
      </svg>
      <Tooltip tip={tip} />
    </div>
  );
}

/** Escolaridade de admitidos × desligados: colunas agrupadas. */
export function Escolaridade({ esc, kpi4 }) {
  const { tip, mostrar, esconder } = useTooltip();
  const faixas = ["Até fundamental", "Médio", "Superior incompleto", "Superior ou mais"];
  const v = (tipo, f) => esc.find((e) => e.tipo === tipo && e.faixa === f)?.pct ?? 0;
  const L = 480, A = 300, B = A - 40, TOPO = 24, grupo = (L - 40) / faixas.length, w = 22;
  const max = Math.max(...faixas.flatMap((f) => [v("Admitidos", f), v("Desligados", f)])) * 1.12;
  const y = (p) => B - (p / max) * (B - TOPO);
  const titulo = `Quem entra tem a mesma escolaridade de quem sai (${sinal(kpi4, 2)} p.p. com superior)`;
  const coluna = (cx, valor, cor, chave, tipo) => {
    const top = y(valor), h = B - top, r = Math.min(4, h);
    return (
      <g key={chave} onMouseMove={(e) => mostrar(e, (<><b>{tipo}</b><div className="linha"><span>{chave.split("|")[0]}</span><span>{pct(valor)}</span></div></>))}>
        <path d={`M${cx},${B} v-${h - r} q0,-${r} ${r},-${r} h${w - 2 * r} q${r},0 ${r},${r} v${h - r} z`} fill={cor} />
        <rect x={cx - 4} y={TOPO} width={w + 8} height={B - TOPO} fill="transparent" />
      </g>
    );
  };
  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      <p className="sub">Distribuição por escolaridade na transformação · sem "não identificado" · por isso o gargalo não é falta de formação formal</p>
      <div className="legenda">
        <span><i className="barra" style={{ background: "var(--azul)" }} />Admitidos</span>
        <span><i className="barra" style={{ background: "var(--cinza-1)" }} />Desligados</span>
      </div>
      <svg viewBox={`0 0 ${L} ${A}`} role="img" aria-label={titulo} onMouseLeave={esconder}>
        <line className="base" x1={20} x2={L - 20} y1={B} y2={B} />
        {faixas.map((f, i) => {
          const cx = 20 + i * grupo + grupo / 2;
          const a = v("Admitidos", f), d = v("Desligados", f);
          return (
            <g key={f}>
              {coluna(cx - w - 1, a, "var(--azul)", `${f}|a`, "Admitidos")}
              {coluna(cx + 1, d, "var(--cinza-1)", `${f}|d`, "Desligados")}
              <text className="eixo" x={cx} y={Math.min(y(a), y(d)) - 6} textAnchor="middle" style={{ fill: "var(--ink-2)" }}>{pct(a, 0)}</text>
              <text x={cx} y={B + 18} textAnchor="middle">{f}</text>
            </g>
          );
        })}
      </svg>
      <Tooltip tip={tip} />
    </div>
  );
}
