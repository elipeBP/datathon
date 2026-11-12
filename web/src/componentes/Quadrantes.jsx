import { scaleLinear, scaleSqrt } from "d3-scale";
import { Tooltip, int, pct, sinal, sinalInt, useTooltip } from "../fmt.jsx";

const L = 760, A = 460, M = { t: 16, r: 24, b: 44, l: 52 };
export const QUADS = [
  { nome: "Expansão sob pressão", cor: "var(--alerta)", leitura: "cresce e perde gente: o sinal mais próximo de apagão" },
  { nome: "Retenção problemática", cor: "var(--retencao)", leitura: "não cresce e perde gente" },
  { nome: "Expansão saudável", cor: "var(--cinza-1)", leitura: "cresce e retém" },
  { nome: "Estagnado", cor: "var(--cinza-2)", leitura: "baixa dinâmica" },
];
const COR = Object.fromEntries(QUADS.map((q) => [q.nome, q.cor]));
// rótulos diretos só nos pontos da história (seleção, nunca todos), com a posição escolhida para não colidir
const ROTULAR = {
  "Chapecó|Alimentos e bebidas": "cima-esq",
  "Concórdia|Alimentos e bebidas": "direita",
  "Blumenau|Têxtil, confecção e calçados": "baixo",
  "Rio do Sul|Têxtil, confecção e calçados": "esquerda",
};

export default function Quadrantes({ q }) {
  const { tip, mostrar, esconder } = useTooltip();
  const pts = [...q.pontos].sort((a, b) => b.movimentos - a.movimentos); // grandes atrás
  const xs = pts.map((p) => p.kpi2), ys = pts.map((p) => p.kpi1);
  const x = scaleLinear().domain([Math.min(...xs) - 4, Math.max(...xs) + 4]).range([M.l, L - M.r]).nice();
  const y = scaleLinear().domain([Math.min(...ys) - 2, Math.max(...ys) + 2]).range([A - M.b, M.t]).nice();
  const r = scaleSqrt().domain([0, Math.max(...pts.map((p) => p.movimentos))]).range([0, 26]);
  const cont = Object.fromEntries(QUADS.map((qq) => [qq.nome, pts.filter((p) => p.quadrante === qq.nome).length]));
  const titulo = `${cont["Expansão sob pressão"]} polos crescem e perdem gente; ${cont["Retenção problemática"]} não crescem e perdem gente`;

  const tipo = (p) => (
    <>
      <b>{p.micro} · {p.grupo}</b>
      <div className="t-sub">{p.quadrante}</div>
      <div className="linha"><span>Saídas a pedido</span><span>{pct(p.kpi1)}</span></div>
      <div className="linha"><span>Saldo por 10 mil hab.</span><span>{sinal(p.kpi2)}</span></div>
      <div className="linha"><span>Saldo em 12 meses</span><span>{sinalInt(p.saldo)}</span></div>
      <div className="linha"><span>Movimentações</span><span>{int(p.movimentos)}</span></div>
    </>
  );

  return (
    <div className="cartao">
      <h3>{titulo}</h3>
      <p className="sub">Cada bolha é uma microrregião × setor com volume suficiente · tamanho = movimentações · linhas = medianas</p>
      <div className="legenda">
        {QUADS.map((qq) => (
          <span key={qq.nome}><i style={{ background: qq.cor }} />{qq.nome} ({cont[qq.nome]}) · <span style={{ color: "var(--muted)" }}>{qq.leitura}</span></span>
        ))}
      </div>
      <div className="rola"><svg className="largo" viewBox={`0 0 ${L} ${A}`} role="img" aria-label={titulo} onMouseLeave={esconder}>
        {y.ticks(6).map((t) => (
          <g key={`y${t}`}>
            <line className="grade" x1={M.l} x2={L - M.r} y1={y(t)} y2={y(t)} />
            <text className="eixo" x={M.l - 8} y={y(t) + 4} textAnchor="end">{t}%</text>
          </g>
        ))}
        {x.ticks(8).map((t) => (
          <text key={`x${t}`} className="eixo" x={x(t)} y={A - M.b + 18} textAnchor="middle">{t > 0 ? `+${t}` : t}</text>
        ))}
        <text className="eixo" x={(M.l + L - M.r) / 2} y={A - 6} textAnchor="middle">Saldo por 10 mil habitantes (12 meses) →</text>
        <text className="eixo" transform={`translate(12, ${(A - M.b + M.t) / 2}) rotate(-90)`} textAnchor="middle">% das saídas a pedido →</text>
        <line className="ref" x1={x(q.mediana_kpi2)} x2={x(q.mediana_kpi2)} y1={M.t} y2={A - M.b} />
        <line className="ref" x1={M.l} x2={L - M.r} y1={y(q.mediana_kpi1)} y2={y(q.mediana_kpi1)} />
        {pts.map((p) => (
          <circle key={`${p.micro}|${p.grupo}`} cx={x(p.kpi2)} cy={y(p.kpi1)} r={Math.max(4, r(p.movimentos))}
            fill={COR[p.quadrante]} fillOpacity={0.85} stroke="var(--surface)" strokeWidth={2}
            onMouseMove={(e) => mostrar(e, tipo(p))} />
        ))}
        {pts.filter((p) => ROTULAR[`${p.micro}|${p.grupo}`]).map((p) => {
          const pos = ROTULAR[`${p.micro}|${p.grupo}`];
          const rr = Math.max(4, r(p.movimentos)), cx = x(p.kpi2), cy = y(p.kpi1);
          const lugar = {
            cima: [cx, cy - rr - 8, "middle"], "cima-esq": [cx + rr, cy - rr - 8, "end"], baixo: [cx, cy + rr + 16, "middle"],
            direita: [cx + rr + 6, cy + 4, "start"], esquerda: [cx - rr - 6, cy + 4, "end"],
          }[pos];
          return (
            <text key={`r${p.micro}${p.grupo}`} x={lugar[0]} y={lugar[1]} textAnchor={lugar[2]} className="halo"
              style={{ fill: "var(--ink)", fontWeight: 600 }}>
              {p.micro} · {p.grupo.split(",")[0]}
            </text>
          );
        })}
      </svg></div>
      <Tooltip tip={tip} />
    </div>
  );
}
