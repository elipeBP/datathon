// Capítulo 1 — Tese (Main.dc.html / Desktop1-Abertura.dc.html)
import { QA } from "../qa.js";
import { Pergunte, Icone, ProximoCapitulo } from "../componentes/base.jsx";
import { dec, int, pct, sinal, sinalInt } from "../fmt.jsx";

export const SETORES = [
  { k: "alimentos", grupo: "Alimentos e bebidas", n: "Alimentos e bebidas", curto: "Alimentos", objs: ["alimentos", "leite", "galinha", "ovo", "garrafa", "avental"] },
  { k: "madeira", grupo: "Madeira e móveis", n: "Madeira e móveis", curto: "Madeira", objs: ["madeira", "pinha", "serrote", "cadeira", "lapis"] },
  { k: "textil", grupo: "Têxtil, confecção e calçados", n: "Têxtil e confecção", curto: "Têxtil", objs: ["textil", "novelo", "agulha", "tesoura", "etiqueta", "fita"] },
  { k: "eletro", grupo: "Eletroeletrônica", n: "Eletro­eletrônica", curto: "Eletroeletrônica", objs: ["eletro", "bobina", "motor", "placa", "lampada"] },
  { k: "plastico", grupo: "Plástico e borracha", n: "Plástico e borracha", curto: "Plástico", objs: ["plastico"] },
  { k: "papel", grupo: "Papel, celulose e gráfica", n: "Papel e gráfica", curto: "Papel", objs: ["papel"] },
  { k: "minerais", grupo: "Minerais não metálicos e cerâmica", n: "Cerâmica e minerais", curto: "Cerâmica", objs: ["minerais"] },
  { k: "quimica", grupo: "Química e farmacêutica", n: "Química e farma", curto: "Química", objs: ["quimica"] },
  { k: "metal", grupo: "Metalmecânica", n: "Metal­mecânica", curto: "Metalmecânica", objs: ["metal", "porca", "chave", "solda", "peca"] },
];

export default function Tese({ dados }) {
  const t = dados.segmentos.find((s) => s.segmento === "Transformação");
  const ctx = { cap: "tese", texto: "Capítulo 1, tese" };
  const [q1, q2, q3] = QA.tese;
  const giro = (100 * t.saldo) / t.movimentos;
  const entra = t.kpi3 * 100;

  return (
    <>
      <div className="tese-topo">
        <section className="abre esq">
          <div className="eyebrow">Tese<span className="so-desk" style={{ display: "none" }}>&nbsp;· Novo CAGED, set/2025 a ago/2026</span></div>
          <h1 style={{ fontSize: undefined }}>O apagão da indústria catarinense aparece como rotatividade, não como falta de gente.</h1>
          <p>Onde a indústria catarinense perde gente, por quê e o que fazer.</p>
          <div className="so-desk" style={{ display: "none", flexDirection: "column", marginTop: 36 }}>
            <div style={{ fontSize: 13, fontWeight: 500, color: "var(--tinta2)" }}>9 setores da transformação analisados</div>
            <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
              {SETORES.map((s) => (
                <a key={s.k} href={`#/setores?s=${s.k}`} className="tile" title={s.n.replace("­", "")} aria-label={s.n.replace("­", "")}
                  style={{ width: 52, height: 52, minHeight: 0, padding: 0, alignItems: "center", justifyContent: "center", borderRadius: 10 }}>
                  <Icone kind={s.k} size={24} />
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="kpi-heroi" aria-labelledby="kpi1">
          <div id="kpi1" className="r">Desligamentos a pedido do trabalhador</div>
          <div className="v num">{pct(t.kpi1)}</div>
          <p className="p">dos <b className="num">{int(t.desligamentos)}</b> desligamentos da indústria de transformação em 12 meses foram pedidos pelo próprio trabalhador.</p>
          <div className="dividida" role="img" aria-label={`${pct(t.kpi1)} a pedido, ${pct(100 - t.kpi1)} outros motivos`}>
            <div style={{ width: `${t.kpi1}%` }} /><div />
          </div>
          <div className="leg-dividida">
            <span><span className="ponto-cor" style={{ background: "var(--sinal)" }} />A pedido <b className="num">{pct(t.kpi1)}</b></span>
            <span><span className="ponto-cor" style={{ background: "var(--neutro-claro)" }} />Outros motivos <b className="num">{pct(100 - t.kpi1)}</b></span>
          </div>
          <div style={{ marginTop: 16, paddingTop: 12, borderTop: "1px solid var(--linha)" }}>
            <Pergunte itens={[q1]} contexto={ctx} />
          </div>
        </section>
      </div>

      <section className="bloco provas" style={{ marginTop: 40 }}>
        <div className="eyebrow">Três provas</div>
        <h2 className="graf">O setor gira muito, cresce pouco e não falta formação</h2>
        <div className="provas-grade">
          <div className="prova">
            <div className="grande num">{sinalInt(t.saldo)}</div>
            <div>
              <div className="txt"><b>Saldo de empregos</b> em 12 meses, em <span className="num">{int(t.movimentos)}</span> movimentações.</div>
              <div role="img" aria-label={`Saldo equivale a ${dec(giro, 2)}% das movimentações`} style={{ position: "relative", height: 6, marginTop: 10, borderRadius: 3, background: "var(--linha)" }}>
                <div style={{ position: "absolute", left: 0, top: -3, width: 2, height: 12, background: "var(--expansao)" }} />
              </div>
              <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>O saldo equivale a {dec(giro, 2)}% do giro.</div>
            </div>
          </div>
          <div className="prova">
            <div className="grande num">{dec(t.kpi3, 3)}</div>
            <div>
              <div className="txt"><b>Salário de reposição:</b> quem entra ganha {pct(100 - entra)} menos que quem sai, na mesma ocupação e região.</div>
              <div className="haltere-mini" role="img" aria-label={`Entra ${dec(t.kpi3, 3)}, sai 1,000`}>
                <div className="eixo" /><div className="liga" style={{ left: "75%", right: 5 }} />
                <div className="p" style={{ left: "75%", background: "var(--sinal)" }} /><div className="p" style={{ left: "calc(100% - 5px)", background: "var(--neutro)" }} />
              </div>
              <div className="muted" style={{ display: "flex", justifyContent: "flex-end", gap: 12, fontSize: 12, marginTop: 4 }}>
                <span><span style={{ color: "var(--sinal)" }}>●</span> Entra {dec(t.kpi3, 3)}</span><span><span style={{ color: "var(--neutro)" }}>●</span> Sai 1,000</span>
              </div>
            </div>
          </div>
          <div className="prova">
            <div className="grande num">{sinal(t.kpi4, 2)}<small> p.p.</small></div>
            <div className="txt"><b>Escolaridade:</b> quem entra estudou o mesmo que quem sai, na mesma ocupação e região. O problema não é formação.</div>
          </div>
        </div>
        <Pergunte titulo="Pergunte sobre estes dados" itens={[q2, q3]} contexto={ctx} />
      </section>

      <section className="bloco so-mobile" style={{ marginTop: 40, display: "block" }}>
        <div className="eyebrow">Recorte</div>
        <h2 className="graf">9 setores da transformação, 20 microrregiões</h2>
        <div className="tiles">
          {SETORES.map((s) => (
            <a key={s.k} className="tile" href={`#/setores?s=${s.k}`}><Icone kind={s.k} size={24} /><span>{s.n}</span></a>
          ))}
        </div>
      </section>

      <p className="fonte bloco" style={{ marginTop: 28 }}>Fonte: Novo CAGED (MTE), Santa Catarina, indústria de transformação, set/2025 a ago/2026.</p>
      <ProximoCapitulo cap="tese" />
    </>
  );
}
