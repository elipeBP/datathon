// Estudo em destaque (capítulo Por quê): modelo das saídas a pedido (src/modelo.py).
// Nível 1 — mercado: dispersão das 620 células ocupação × microrregião + médias por faixa + curva do modelo,
// fórmula (MathML nativo) e a derivação do coeficiente até os pontos percentuais. Nível 2 — perfil.
import { useState } from "react";
import { QA } from "../qa.js";
import { Pergunte, useVisto } from "../componentes/base.jsx";
import { useDesktop } from "./Onde.jsx";
import { dec, int } from "../fmt.jsx";

const pp = (v, casas = 1) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${dec(Math.abs(v), casas)}`;
const num = (v, casas = 3) => `${v < 0 ? "−" : ""}${dec(Math.abs(v), casas)}`;
const pv = (p) => (p < 0.001 ? "p < 0,001" : `p = ${dec(p, 3)}`);
const PERFIL = [
  ["escolaridade", "Superior ou mais", "Superior completo"],
  ["sexo", "Mulher", "Mulheres"],
  ["porte", "500 ou mais", "Empresa com 500+ empregados"],
  ["faixa_idade", "18 a 24", "18 a 24 anos"],
  ["escolaridade", "Até fundamental", "Até fundamental"],
  ["porte", "até 19", "Empresa com até 19 empregados"],
  ["faixa_idade", "50 ou mais", "50 anos ou mais"],
];

// ---------------------------------------------------------------- gráfico de dispersão com a curva do modelo
function Dispersao({ g, efeito }) {
  const desktop = useDesktop();
  const [foco, setFoco] = useState(null);
  const W = desktop ? 720 : 360, H = desktop ? 400 : 300;
  const M = { l: desktop ? 44 : 34, r: 14, t: 14, b: desktop ? 44 : 40 };
  const X0 = -30, X1 = 30, Y0 = 10, Y1 = 85;
  const x = (v) => M.l + ((Math.max(X0, Math.min(X1, v)) - X0) / (X1 - X0)) * (W - M.l - M.r);
  const y = (v) => M.t + (1 - (Math.max(Y0, Math.min(Y1, v)) - Y0) / (Y1 - Y0)) * (H - M.t - M.b);
  const maxD = Math.max(...g.pontos.map((p) => p.d));
  const r = (d) => Math.max(1.6, Math.sqrt(d / maxD) * (desktop ? 11 : 7));
  const curva = g.curva.map((c, i) => `${i ? "L" : "M"}${x(c.x).toFixed(1)},${y(c.y).toFixed(1)}`).join(" ");
  const c0 = g.curva.find((c) => Math.abs(c.x) < 0.01), c10 = g.curva.find((c) => Math.abs(c.x - 10) < 0.01);
  const fs = desktop ? 12 : 10;
  const fora = g.pontos.filter((p) => Math.abs(p.x) > 30).length;
  const pts = [...g.pontos].sort((a, b) => b.d - a.d); // grandes atrás
  const ponto = foco != null ? g.pontos[foco] : null;

  return (
    <figure className="dispersao" style={{ margin: 0 }}>
      <div className="legenda-disp">
        <span><i className="l-ponto" />Cada ponto: uma ocupação numa microrregião (tamanho = desligamentos)</span>
        <span><i className="l-media" />Média por faixa de salário</span>
        <span><i className="l-curva" />Modelo, com os outros fatores fixos</span>
      </div>
      <div style={{ position: "relative" }}>
        <svg viewBox={`0 0 ${W} ${H}`} role="img" style={{ display: "block", width: "100%", height: "auto" }}
          aria-label={`Dispersão de ${g.pontos.length} mercados: quanto maior o salário relativo, menor a parcela de saídas a pedido. A curva do modelo cai de ${dec(g.curva[0].y, 1)}% para ${dec(g.curva[g.curva.length - 1].y, 1)}%.`}
          onMouseLeave={() => setFoco(null)}>
          {[20, 40, 60, 80].map((t) => (
            <g key={`y${t}`}>
              <line x1={M.l} x2={W - M.r} y1={y(t)} y2={y(t)} stroke="var(--linha)" />
              <text x={M.l - 6} y={y(t) + 4} textAnchor="end" fontSize={fs - 1} fill="var(--tinta3)" className="num">{t}%</text>
            </g>
          ))}
          {[-30, -20, -10, 0, 10, 20, 30].map((t) => (
            <text key={`x${t}`} x={x(t)} y={H - M.b + 16} textAnchor="middle" fontSize={fs - 1} fill="var(--tinta3)" className="num">{t > 0 ? `+${t}` : t}%</text>
          ))}
          <line x1={x(0)} x2={x(0)} y1={M.t} y2={H - M.b} stroke="var(--borda-forte)" strokeDasharray="3 3" />
          <text x={(M.l + W - M.r) / 2} y={H - 6} textAnchor="middle" fontSize={fs - 1} fill="var(--tinta3)">Salário da ocupação na região × mediana da ocupação em SC</text>
          {desktop && <text transform={`translate(10 ${(M.t + H - M.b) / 2}) rotate(-90)`} textAnchor="middle" fontSize={fs - 1} fill="var(--tinta3)">% das saídas a pedido</text>}

          {pts.map((p) => {
            const i = g.pontos.indexOf(p);
            return <circle key={i} cx={x(p.x)} cy={y(p.y)} r={r(p.d)} fill={foco === i ? "var(--tinta2)" : "var(--neutro-claro)"} fillOpacity={foco === i ? 0.9 : 0.55}
              onMouseEnter={() => setFoco(i)} onClick={() => setFoco(i)} style={{ cursor: "pointer" }} />;
          })}
          <path d={curva} fill="none" stroke="var(--expansao)" strokeWidth={desktop ? 3 : 2.5} strokeLinecap="round" />
          {g.faixas.map((f) => <circle key={f.x} cx={x(f.x)} cy={y(f.y)} r={desktop ? 5.5 : 4.5} fill="var(--tinta)" stroke="#fff" strokeWidth="2" />)}

          {c0 && c10 && (
            <g aria-hidden="true">
              <circle cx={x(0)} cy={y(c0.y)} r="4.5" fill="var(--expansao)" stroke="#fff" strokeWidth="2" />
              <circle cx={x(10)} cy={y(c10.y)} r="4.5" fill="var(--expansao)" stroke="#fff" strokeWidth="2" />
              <path d={`M${x(10) + 8},${y(c0.y)} h10 v${y(c10.y) - y(c0.y)} h-10`} fill="none" stroke="var(--tinta)" strokeWidth="1.2" />
              <line x1={x(0)} x2={x(10) + 8} y1={y(c0.y)} y2={y(c0.y)} stroke="var(--tinta)" strokeWidth="1" strokeDasharray="2 2" />
              <text x={x(10) + 24} y={(y(c0.y) + y(c10.y)) / 2 + 4} fontSize={fs + 1} fontWeight="700" fill="var(--tinta)" className="halo">{pp(efeito)} p.p.</text>
              <text x={x(10) + 24} y={(y(c0.y) + y(c10.y)) / 2 + 4 + fs + 2} fontSize={fs - 1} fill="var(--tinta2)" className="halo">de 0% a +10%</text>
            </g>
          )}
        </svg>
        {ponto && (
          <div className="disp-tip" role="status" style={desktop ? { left: `${(x(ponto.x) / W) * 100}%`, top: `${(y(ponto.y) / H) * 100}%` } : {}}>
            <b>{ponto.o}</b>
            <div>{ponto.m} · {ponto.g}</div>
            <div className="num">Salário {pp(ponto.x)}% vs. SC · {dec(ponto.y, 1)}% a pedido · {int(ponto.d)} desligamentos</div>
          </div>
        )}
      </div>
      <figcaption className="nota-graf">
        {g.pontos.length} mercados com pelo menos 100 desligamentos. Os pontos são dados brutos; a curva é a previsão média do modelo com setor, região, ocupação e perfil fixos.
        {fora > 0 && ` ${fora} mercados acima de +30% aparecem na borda.`} {desktop ? "Passe o mouse num ponto para ver a ocupação." : "Toque num ponto para ver a ocupação."}
      </figcaption>
    </figure>
  );
}

// ---------------------------------------------------------------- fórmulas (MathML)
const Sub = ({ b, s }) => <msub><mi>{b}</mi><mi>{s}</mi></msub>;
const SubM = ({ b, s }) => <math><Sub b={b} s={s} /></math>;
const Beta = ({ k }) => <msub><mi>β</mi><mn>{k}</mn></msub>;
const Ab = () => <mo stretchy="false">(</mo>;
const Fe = () => <mo stretchy="false">)</mo>;
const Ln = ({ children }) => <mrow><mi>ln</mi><mo>⁡</mo><Ab />{children}<Fe /></mrow>;

/** A fórmula do modelo de mercado em três linhas (cabe no celular). */
function FormulaMercado() {
  return (
    <div className="formula-bloco">
      <math display="block"><mrow>
        <mi>logit</mi><mo>⁡</mo><Ab /><Sub b="p" s="c" /><Fe /><mo>=</mo>
        <mi>ln</mi><mo>⁡</mo><mo>(</mo><mfrac><Sub b="p" s="c" /><mrow><mn>1</mn><mo>−</mo><Sub b="p" s="c" /></mrow></mfrac><mo>)</mo>
      </mrow></math>
      <math display="block"><mrow>
        <mo>=</mo><Beta k="0" /><mo>+</mo><Beta k="1" /><Ln><Sub b="s" s="c" /></Ln>
        <mo>+</mo><Beta k="2" /><Ln><Sub b="π" s="c" /></Ln><mo>+</mo><Beta k="3" /><Sub b="g" s="c" />
      </mrow></math>
      <math display="block"><mrow>
        <mo>+</mo><munderover><mo>∑</mo><mrow><mi>k</mi><mo>=</mo><mn>4</mn></mrow><mn>7</mn></munderover><msub><mi>β</mi><mi>k</mi></msub><msub><mi>z</mi><mrow><mi>k</mi><mi>c</mi></mrow></msub>
        <mo>+</mo><msub><mi>γ</mi><mtext>setor</mtext></msub><mo>+</mo><msub><mi>δ</mi><mtext>meso</mtext></msub><mo>+</mo><msub><mi>θ</mi><mtext>ocup</mtext></msub>
      </mrow></math>
    </div>
  );
}

function Derivacao({ d, n }) {
  const or10 = Math.pow(1.1, d.beta1);
  return (
    <ol className="passos-mat">
      <li>
        <div className="t">O coeficiente estimado</div>
        <div className="formula-bloco">
          <math display="block"><mrow>
            <msub><mover><mi>β</mi><mo>^</mo></mover><mn>1</mn></msub><mo>=</mo><mn>{num(d.beta1)}</mn><mspace width="1em" /><mi>z</mi><mo>=</mo>
            <mfrac><msub><mover><mi>β</mi><mo>^</mo></mover><mn>1</mn></msub><mrow><mtext>EP</mtext></mrow></mfrac><mo>=</mo><mn>{num(d.z, 2)}</mn>
          </mrow></math>
          <math display="block"><mrow><mtext>IC 95%: [{num(d.ic_inf)}; {num(d.ic_sup)}]</mtext></mrow></math>
        </div>
        <p>Negativo e a {dec(Math.abs(d.z), 1)} erros-padrão de zero (p &lt; 0,001): quanto maior o salário relativo, menor a chance de a saída ser a pedido. O intervalo de confiança não cruza o zero.</p>
      </li>
      <li>
        <div className="t">Em chances (razão de chances para +10% de salário)</div>
        <div className="formula-bloco">
          <math display="block"><mrow>
            <msup><mn>1,1</mn><msub><mover><mi>β</mi><mo>^</mo></mover><mn>1</mn></msub></msup><mo>=</mo>
            <msup><mi>e</mi><mrow><msub><mover><mi>β</mi><mo>^</mo></mover><mn>1</mn></msub><mo>·</mo><mi>ln</mi><mo>⁡</mo><mn>1,1</mn></mrow></msup>
            <mo>=</mo><mn>{dec(or10, 3)}</mn>
          </mrow></math>
        </div>
        <p>As chances de a saída ser a pedido ficam {dec(100 * (1 - or10), 1)}% menores.</p>
      </li>
      <li>
        <div className="t">Em pontos percentuais: aproximação pela derivada</div>
        <div className="formula-bloco">
          <math display="block"><mrow>
            <mfrac><mrow><mo>∂</mo><mi>p</mi></mrow><mrow><mo>∂</mo><mi>ln</mi><mo>⁡</mo><mi>s</mi></mrow></mfrac><mo>=</mo><Beta k="1" /><mi>p</mi><Ab /><mn>1</mn><mo>−</mo><mi>p</mi><Fe />
            </mrow></math>
          <math display="block"><mrow>
            <mi>Δ</mi><mi>p</mi><mo>≈</mo><Beta k="1" /><mo>·</mo><mi>ln</mi><mo>⁡</mo><mn>1,1</mn><mo>·</mo><mover><mi>p</mi><mo>‾</mo></mover><Ab /><mn>1</mn><mo>−</mo><mover><mi>p</mi><mo>‾</mo></mover><Fe />
          </mrow></math>
          <math display="block"><mrow>
            <mo>=</mo><mn>{num(d.beta1)}</mn><mo>×</mo><mn>{dec(d.ln11, 4)}</mn><mo>×</mo><mn>{dec(d.p_bar, 3)}</mn><mo>×</mo><mn>{dec(1 - d.p_bar, 3)}</mn><mo>≈</mo><mn>{num(d.aprox_pp, 2)}</mn><mtext> p.p.</mtext>
          </mrow></math>
        </div>
      </li>
      <li>
        <div className="t">Em pontos percentuais: cálculo exato (efeito marginal médio)</div>
        <div className="formula-bloco">
          <math display="block"><mrow>
            <mi>Δ</mi><mi>p</mi><mo>=</mo><mfrac><mn>1</mn><mi>N</mi></mfrac><munderover><mo>∑</mo><mrow><mi>c</mi><mo>=</mo><mn>1</mn></mrow><mi>N</mi></munderover>
            <mo>[</mo><mi>Λ</mi><Ab /><msubsup><mi>x</mi><mi>c</mi><mo>′</mo></msubsup><mover><mi>β</mi><mo>^</mo></mover><mo>+</mo><msub><mover><mi>β</mi><mo>^</mo></mover><mn>1</mn></msub><mi>ln</mi><mo>⁡</mo><mn>1,1</mn><Fe />
            <mo>−</mo><mi>Λ</mi><Ab /><msubsup><mi>x</mi><mi>c</mi><mo>′</mo></msubsup><mover><mi>β</mi><mo>^</mo></mover><Fe /><mo>]</mo>
          </mrow></math>
          <math display="block"><mrow><mo>=</mo><mn>{num(d.exato_pp, 2)}</mn><mtext> p.p.</mtext><mspace width="0.8em" /><mtext>(N = {int(n)} células)</mtext></mrow></math>
        </div>
        <p>com <math><mrow><mi>Λ</mi><Ab /><mi>z</mi><Fe /><mo>=</mo><mfrac><mn>1</mn><mrow><mn>1</mn><mo>+</mo><msup><mi>e</mi><mrow><mo>−</mo><mi>z</mi></mrow></msup></mrow></mfrac></mrow></math>. A aproximação e o cálculo exato concordam: é daí que vêm os <b>{pp(d.exato_pp)} p.p.</b></p>
      </li>
    </ol>
  );
}

// ---------------------------------------------------------------- seção
export default function ModeloSecao({ modelo }) {
  const [r1, c1] = useVisto(), [r2, c2] = useVisto();
  const [aberto, setAberto] = useState(false);
  if (!modelo) return null;
  const m = modelo.mercado, pf = modelo.perfil, g = m.grafico, d = g?.derivacao;
  const premio = m.efeitos.find((e) => e.variavel === "log_premio");
  const rob = [{ recorte: "Modelo principal", celulas: m.celulas, efeito_sal10_pp: m.efeito_sal10_pp }, ...m.robustez];
  const maxRob = Math.max(...rob.map((x) => Math.abs(x.efeito_sal10_pp)));
  const linhas = PERFIL.map(([f, n, rot]) => ({ rot, e: pf.efeitos.find((x) => x.fator === f && x.nivel === n) })).filter((x) => x.e);
  const maxP = Math.max(...linhas.map((x) => Math.abs(x.e.dif_pp)));
  const ef1dp = Object.fromEntries(m.efeitos.map((e) => [e.variavel, e.efeito_1dp_pp]));
  const ctx = { cap: "porque", texto: "Capítulo 4, modelo estatístico" };

  return (
    <section className="modelo bloco" aria-labelledby="titulo-modelo">
      <div className="eyebrow">Estudo em destaque · Modelo estatístico</div>
      <h2 id="titulo-modelo" className="graf modelo-h2">Onde a mesma ocupação paga mais que no resto de SC, menos gente pede para sair</h2>
      <p className="muted" style={{ margin: "8px 0 0", maxWidth: "70ch", fontSize: 15 }}>
        Os gráficos acima comparam médias. Aqui, um modelo mede o efeito do salário com setor, região, ocupação e perfil dos trabalhadores fixos, em {int(m.celulas)} mercados de trabalho
        ({int(m.desligamentos)} desligamentos, 75% da transformação).
      </p>

      {g && (
        <div className="estudo-grade">
          <div className="cartao estudo-graf"><Dispersao g={g} efeito={m.efeito_sal10_pp} /></div>
          <aside className="cartao estudo-lado">
            <div className="rot-graf">Resultado</div>
            <div className="modelo-heroi num">{pp(m.efeito_sal10_pp)}<small> p.p.</small></div>
            <p className="modelo-txt">nas saídas a pedido onde a ocupação paga <b>10% acima</b> da mediana dela em SC.</p>
            <dl className="estudo-stats">
              <div><dt>Coeficiente β₁</dt><dd className="num">{num(d.beta1)}</dd></div>
              <div><dt>IC 95%</dt><dd className="num">{num(d.ic_inf, 2)} a {num(d.ic_sup, 2)}</dd></div>
              <div><dt>Significância</dt><dd className="num">{pv(m.p_sal)}</dd></div>
              <div><dt>Deviance explicada</dt><dd className="num">{dec(100 * d.dev_explicada, 0)}%</dd></div>
            </dl>
            <div className="rot-graf" style={{ marginTop: 14 }}>Robustez: o efeito se mantém</div>
            <div ref={r1} className={`linhas ${c1}`} style={{ marginTop: 6 }}>
              {rob.map((x, i) => (
                <div key={x.recorte} className="modelo-linha">
                  <span>{x.recorte.charAt(0).toUpperCase() + x.recorte.slice(1)}</span>
                  <span className="trilho-barra" aria-hidden="true">
                    <span className="b neg" style={{ "--i": i, right: 0, left: "auto", width: `${(Math.abs(x.efeito_sal10_pp) / maxRob) * 100}%`, background: "var(--expansao)" }} />
                  </span>
                  <span className="num v">{pp(x.efeito_sal10_pp)}</span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      )}

      {d && (
        <div className="estudo-mat">
          <article className="cartao mat-cartao">
            <div className="rot-graf">O modelo</div>
            <h3>Logit fracionário com efeitos fixos</h3>
            <FormulaMercado />
            <dl className="legenda-mat">
              <div><dt><SubM b="p" s="c" /></dt><dd>parcela das saídas a pedido na célula c (ocupação × microrregião)</dd></div>
              <div><dt><SubM b="s" s="c" /></dt><dd>mediana salarial da célula ÷ mediana da mesma ocupação em SC (o salário relativo)</dd></div>
              <div><dt><SubM b="π" s="c" /></dt><dd>prêmio de contratação: mediana de quem entra ÷ de quem sai</dd></div>
              <div><dt><SubM b="g" s="c" /></dt><dd>crescimento: saldo ÷ movimentações</dd></div>
              <div><dt><math><msub><mi>z</mi><mrow><mi>k</mi><mi>c</mi></mrow></msub></math></dt><dd>% com superior, % de 14 a 24 anos, % de mulheres, % em empresas com 500+ empregados</dd></div>
              <div><dt><math><mrow><mi>γ</mi><mo>,</mo><mi>δ</mi><mo>,</mo><mi>θ</mi></mrow></math></dt><dd>efeitos fixos de setor, mesorregião e grande grupo da ocupação</dd></div>
            </dl>
            <p className="nota-graf">
              Estimação por quase-verossimilhança binomial (GLM, ligação logit), ponderada pelos desligamentos de cada célula; erros-padrão robustos (HC1).
              {" "}{int(m.celulas)} células, {d.n_params} parâmetros. Feito em Python com statsmodels.
            </p>
          </article>
          <article className="cartao mat-cartao">
            <div className="rot-graf">Do coeficiente ao número</div>
            <h3>Como o β₁ vira {pp(m.efeito_sal10_pp)} pontos percentuais</h3>
            <Derivacao d={d} n={m.celulas} />
          </article>
        </div>
      )}

      <button className="acc-btn" style={{ marginTop: 8 }} aria-expanded={aberto} onClick={() => setAberto(!aberto)}>
        <span>Todos os coeficientes do modelo de mercado</span>
        <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" stroke="var(--tinta)" strokeWidth="1.6" fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </button>
      {aberto && (
        <div className="tabela-rolagem">
          <table className="tab-coef">
            <thead><tr><th>Variável</th><th>β</th><th>IC 95%</th><th>p</th><th>+1 desvio-padrão</th></tr></thead>
            <tbody>
              {m.coefs.map((e) => (
                <tr key={e.variavel}>
                  <td>{e.nome}</td><td className="num">{num(e.coef)}</td><td className="num">{num(e.ic_inf, 2)} a {num(e.ic_sup, 2)}</td>
                  <td className="num">{pv(e.p)}</td><td className="num">{pp(ef1dp[e.variavel], 2)} p.p.</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="nota-graf">O prêmio de contratação não se sustenta quando controlado ({pv(premio.p)}): o que pesa é o nível do salário da ocupação na região, não a diferença entre quem entra e quem sai. Efeitos fixos omitidos da tabela.</p>
        </div>
      )}

      <article className="cartao modelo-cartao" style={{ marginTop: 20 }}>
        <div className="rot-graf">Nível 2 · Perfil de quem sai</div>
        <h3>Quem tem mais chance de a saída ter sido a pedido</h3>
        <div className="perfil-grade">
          <div>
            <div className="formula-bloco">
              <math display="block"><mrow>
                <mi>P</mi><Ab /><msub><mi>y</mi><mi>i</mi></msub><mo>=</mo><mn>1</mn><mo>∣</mo><msub><mi>x</mi><mi>i</mi></msub><Fe /><mo>=</mo>
                <mi>Λ</mi><Ab /><mi>α</mi><mo>+</mo><munder><mo>∑</mo><mi>k</mi></munder><msub><mi>β</mi><mi>k</mi></msub><msub><mi>x</mi><mrow><mi>i</mi><mi>k</mi></mrow></msub><mo>+</mo><mtext>controles</mtext><Fe />
              </mrow></math>
              <math display="block"><mrow><msub><mtext>RC</mtext><mi>k</mi></msub><mo>=</mo><msup><mi>e</mi><msub><mi>β</mi><mi>k</mi></msub></msup></mrow></math>
            </div>
            <p className="modelo-txt">
              Regressão logística em {int(pf.n)} desligamentos: <i>y</i> = 1 se a saída foi a pedido. Fatores: escolaridade, idade, sexo, tamanho da empresa e salário relativo; controles fixos de setor, região, ocupação e mês.
              Validada fora da amostra contra um gradient boosting: AUC {dec(pf.auc_logit, 3)} × {dec(pf.auc_gbm, 3)}. O modelo simples, que dá para explicar, fica perto do complexo.
            </p>
          </div>
          <div>
            <div className="sub-graf" style={{ marginTop: 0 }}>Diferença na probabilidade prevista, em p.p., vs. ensino médio, homem, 30 a 39 anos, empresa de 100 a 499</div>
            <div ref={r2} className={`linhas ${c2}`} style={{ marginTop: 8 }}>
              {linhas.map(({ rot, e }, i) => {
                const w = (Math.abs(e.dif_pp) / maxP) * 50;
                return (
                  <div key={rot} className="modelo-linha" role="img" aria-label={`${rot}: ${pp(e.dif_pp)} pontos percentuais`}>
                    <span>{rot}</span>
                    <span className="trilho-barra" aria-hidden="true">
                      <span className="media" style={{ left: "50%", borderLeftStyle: "solid", borderColor: "var(--borda-forte)" }} />
                      <span className={`b${e.dif_pp < 0 ? " neg" : ""}`} style={{ "--i": i, left: `${e.dif_pp < 0 ? 50 - w : 50}%`, width: `${w}%`, background: e.dif_pp > 0 ? "var(--sinal)" : "var(--neutro)" }} />
                    </span>
                    <span className="num v">{pp(e.dif_pp)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <p className="nota-graf">Entre quem saiu, quem ganha bem acima da mediana sai mais por demissão da empresa (viés de seleção); por isso o efeito do salário é lido no modelo de mercado, acima.</p>
      </article>

      <p className="fonte" style={{ marginTop: 12 }}>Associação, não causa. O CAGED não traz tempo de casa, que costuma pesar na decisão de sair. Relatório completo em reports/modelo_saida_pedido.md.</p>
      <Pergunte titulo="Pergunte sobre o modelo" itens={["porque-8", "porque-4", "porque-5"].map((id) => QA.porque.find((x) => x.id === id)).filter(Boolean)} contexto={ctx} />
    </section>
  );
}
