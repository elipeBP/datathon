// Raio-X da Indústria SC — 6 capítulos navegáveis por hash (#/tese, #/onde, …).
// Os números vêm de public/dados.json, gerado pelo pipeline em Python (src/exportar_web.py).
import { useEffect, useState } from "react";
import { CAPITULOS } from "./qa.js";
import { AssistenteProvider } from "./componentes/Assistente.jsx";
import { Cabecalho } from "./componentes/base.jsx";
import Tese from "./capitulos/Tese.jsx";
import Onde from "./capitulos/Onde.jsx";
import Setores from "./capitulos/Setores.jsx";
import PorQue from "./capitulos/PorQue.jsx";
import OQueFazer from "./capitulos/OQueFazer.jsx";
import Metodo from "./capitulos/Metodo.jsx";

const TELAS = { tese: Tese, onde: Onde, setores: Setores, porque: PorQue, oque: OQueFazer, metodo: Metodo };

function lerHash() {
  const [rota, query = ""] = window.location.hash.replace(/^#\/?/, "").split("?");
  const cap = CAPITULOS.some((c) => c.id === rota) ? rota : "tese";
  return { cap, param: new URLSearchParams(query) };
}

export default function App() {
  const [dados, setDados] = useState(null);
  const [geo, setGeo] = useState(null);
  const [erro, setErro] = useState(null);
  const [rota, setRota] = useState(lerHash);

  useEffect(() => {
    Promise.all([fetch("/dados.json").then((r) => r.json()), fetch("/sc_microrregioes.geojson").then((r) => r.json())])
      .then(([d, g]) => { setDados(d); setGeo(g); })
      .catch((e) => setErro(String(e)));
    const mudou = () => { setRota(lerHash()); window.scrollTo({ top: 0 }); };
    window.addEventListener("hashchange", mudou);
    return () => window.removeEventListener("hashchange", mudou);
  }, []);

  useEffect(() => {
    const c = CAPITULOS.find((x) => x.id === rota.cap);
    document.title = c.n === 1 ? "Raio-X da Indústria SC" : `${c.nome} · Raio-X da Indústria SC`;
  }, [rota.cap]);

  if (erro) return <p style={{ padding: 24 }}>Não foi possível carregar os dados: {erro}</p>;
  if (!dados || !geo) return <p style={{ padding: 24, color: "var(--tinta3)" }}>Carregando…</p>;

  const Tela = TELAS[rota.cap];
  return (
    <AssistenteProvider cap={rota.cap}>
      <Cabecalho cap={rota.cap} />
      <main className="pagina" key={rota.cap}>
        <Tela dados={dados} geo={geo} param={rota.param} />
      </main>
      <footer className="pagina">
        <div className="rodape-site">
          Fonte: {dados.meta.fonte}. População: {dados.meta.populacao}. {dados.meta.regioes}. Ocupações agrupadas por IA ({dados.ia.modelo}) com lista fechada e revisão humana.
          Projeto do Datathon CDIA 2026; números gerados pelo pipeline em Python do repositório em {dados.meta.gerado_em}.
        </div>
      </footer>
    </AssistenteProvider>
  );
}
