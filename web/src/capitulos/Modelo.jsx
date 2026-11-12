// Seção "O que o modelo mostra" (capítulo Por quê): modelo das saídas a pedido em dois níveis (src/modelo.py).
import { QA } from "../qa.js";
import { Pergunte, useVisto } from "../componentes/base.jsx";
import { dec, int } from "../fmt.jsx";

const pp = (v, casas = 1) => `${v > 0 ? "+" : v < 0 ? "−" : ""}${dec(Math.abs(v), casas)}`;
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

export default function ModeloSecao({ modelo }) {
  const [r1, c1] = useVisto(), [r2, c2] = useVisto();
  if (!modelo) return null;
  const m = modelo.mercado, pf = modelo.perfil;
  const premio = m.efeitos.find((e) => e.variavel === "log_premio");
  const rob = [{ recorte: "Modelo principal", celulas: m.celulas, efeito_sal10_pp: m.efeito_sal10_pp }, ...m.robustez];
  const maxRob = Math.max(...rob.map((x) => Math.abs(x.efeito_sal10_pp)));
  const linhas = PERFIL.map(([f, n, rot]) => ({ rot, e: pf.efeitos.find((x) => x.fator === f && x.nivel === n) })).filter((x) => x.e);
  const maxP = Math.max(...linhas.map((x) => Math.abs(x.e.dif_pp)));
  const ctx = { cap: "porque", texto: "Capítulo 4, modelo estatístico" };

  return (
    <section className="modelo bloco" aria-labelledby="titulo-modelo">
      <div className="eyebrow">Modelo estatístico</div>
      <h2 id="titulo-modelo" className="graf" style={{ maxWidth: "34ch" }}>Pagar acima do mercado da região está associado a menos pedidos de demissão</h2>
      <p className="muted" style={{ margin: "8px 0 0", maxWidth: "70ch", fontSize: 15 }}>
        Os gráficos acima comparam médias. O modelo mede cada fator com os outros fixos, em dois níveis: o mercado (mesma ocupação em cada microrregião) e o perfil de quem saiu.
      </p>

      <div className="modelo-grade">
        <article className="cartao modelo-cartao">
          <div className="rot-graf">Nível 1 · Mercado</div>
          <h3>Onde a mesma ocupação paga 10% acima da mediana de SC</h3>
          <div className="modelo-heroi num">{pp(m.efeito_sal10_pp)}<small> p.p.</small></div>
          <p className="modelo-txt">na parcela de saídas a pedido, com setor, região e perfil dos trabalhadores fixos ({pv(m.p_sal)}). {int(m.celulas)} mercados, {int(m.desligamentos)} desligamentos.</p>
          <div className="rot-graf" style={{ marginTop: 16 }}>O resultado se mantém em todos os testes</div>
          <div ref={r1} className={`linhas ${c1}`} style={{ marginTop: 8 }}>
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
          <p className="nota-graf">O prêmio de contratação (quem entra × quem sai) não se sustenta quando controlado ({pv(premio.p)}): o que pesa é o nível do salário da ocupação na região, não a diferença entre quem entra e quem sai.</p>
        </article>

        <article className="cartao modelo-cartao">
          <div className="rot-graf">Nível 2 · Perfil</div>
          <h3>Quem tem mais chance de a saída ter sido a pedido</h3>
          <p className="modelo-txt" style={{ marginTop: 6 }}>Na mesma ocupação e região, em pontos percentuais em relação à referência (ensino médio, homem, 30 a 39 anos, empresa de 100 a 499 empregados).</p>
          <div ref={r2} className={`linhas ${c2}`} style={{ marginTop: 10 }}>
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
          <p className="nota-graf">
            Regressão logística em {int(pf.n)} desligamentos, com controles de setor, região, ocupação e mês. Validada fora da amostra contra um gradient boosting
            (AUC {dec(pf.auc_logit, 3)} × {dec(pf.auc_gbm, 3)}). Entre quem saiu, quem ganha bem acima da mediana sai mais por demissão da empresa; por isso o efeito do salário é lido no Nível 1.
          </p>
        </article>
      </div>

      <p className="fonte" style={{ marginTop: 12 }}>Associação, não causa. O CAGED não traz tempo de casa, que costuma pesar na decisão de sair. Detalhes em reports/modelo_saida_pedido.md.</p>
      <Pergunte titulo="Pergunte sobre o modelo" itens={[QA.porque.find((x) => x.id === "porque-4"), QA.porque.find((x) => x.id === "porque-5")]} contexto={ctx} />
    </section>
  );
}
