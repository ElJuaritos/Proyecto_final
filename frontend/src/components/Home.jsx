// pages/Home.jsx
// Página principal: orquesta los cuatro módulos de funcionalidad.

import { useState, useEffect } from "react";
import SearchBar from "./SearchBar.jsx";
import { RouteResult, NearbyResult, MSTResult } from "./Results.jsx";
import {
  getAtracciones,
  postShortestPath,
  getMST,
  postNearby,
} from "../client.js";

export default function Home() {
  const [atracciones, setAtracciones] = useState([]);
  const [activeTab, setActiveTab]     = useState("ruta");

  // Estado: Ruta más corta
  const [origen, setOrigen]       = useState("");
  const [destino, setDestino]     = useState("");
  const [modoRuta, setModoRuta]   = useState("tiempo");
  const [rutaResult, setRutaResult] = useState(null);
  const [rutaError, setRutaError]   = useState("");
  const [loadingRuta, setLoadingRuta] = useState(false);

  // Estado: Cercanos
  const [lat, setLat]       = useState("");
  const [lon, setLon]       = useState("");
  const [radio, setRadio]   = useState(5);
  const [nearbyResult, setNearbyResult] = useState(null);
  const [loadingNearby, setLoadingNearby] = useState(false);

  // Estado: MST
  const [modoPrim, setModoPrim]   = useState("tiempo");
  const [mstResult, setMstResult] = useState(null);
  const [loadingMST, setLoadingMST] = useState(false);

  useEffect(() => {
    getAtracciones().then(setAtracciones);
  }, []);

  // ── Handlers ─────────────────────────────────────────────────────

  const calcularRuta = async () => {
    if (!origen || !destino) return;
    setLoadingRuta(true);
    setRutaError("");
    setRutaResult(null);
    try {
      const data = await postShortestPath(origen, destino, modoRuta);
      setRutaResult(data);
    } catch (e) {
      setRutaError(e.message);
    } finally {
      setLoadingRuta(false);
    }
  };

  const calcularCercanos = async () => {
    if (!lat || !lon) return;
    setLoadingNearby(true);
    const data = await postNearby(parseFloat(lat), parseFloat(lon), parseFloat(radio));
    setNearbyResult(data);
    setLoadingNearby(false);
  };

  // Rellena coordenadas desde un select de atracciones conocidas
  const seleccionarAtraccionBase = (nombre) => {
    const a = atracciones.find(x => x.nombre === nombre);
    if (a) { setLat(String(a.latitud)); setLon(String(a.longitud)); }
  };

  const calcularMST = async () => {
    setLoadingMST(true);
    const data = await getMST(modoPrim);
    setMstResult(data);
    setLoadingMST(false);
  };

  // ── Render ────────────────────────────────────────────────────────
  const tabs = [
    { id: "ruta",    label: "🗺️ Ruta óptima",   algo: "Dijkstra" },
    { id: "cercanos",label: "📡 Cercanos",        algo: "KD-Tree" },
    { id: "mst",     label: "🕸️ Red mínima",     algo: "Prim" },
  ];

  return (
    <main className="home">
      {/* Hero */}
      <header className="hero">
        <div className="hero-tag">Estructuras de Datos · Algoritmos de Grafos</div>
        <h1 className="hero-title">City<span>Explorer</span></h1>
        <p className="hero-sub">Turismo inteligente con Dijkstra · Prim · KD-Tree · Trie</p>
      </header>

      {/* Tabs */}
      <nav className="tabs">
        {tabs.map(t => (
          <button
            key={t.id}
            className={`tab-btn ${activeTab === t.id ? "active" : ""}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
            <span className="tab-algo">{t.algo}</span>
          </button>
        ))}
      </nav>

      {/* Panel: Ruta más corta */}
      {activeTab === "ruta" && (
        <section className="panel">
          <div className="panel-header">
            <h2>Ruta más corta entre dos atracciones</h2>
            <p className="panel-desc">
              Implementado con <strong>Dijkstra</strong> + <code>heapq</code>.
              Complejidad: <code>O((V+E) log V)</code>
            </p>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Origen</label>
              <SearchBar
                placeholder="Ej: Zócalo"
                onSelect={setOrigen}
                value={origen}
              />
            </div>
            <div className="form-field">
              <label>Destino</label>
              <SearchBar
                placeholder="Ej: Chapultepec"
                onSelect={setDestino}
                value={destino}
              />
            </div>
            <div className="form-field">
              <label>Optimizar por</label>
              <div className="toggle-group">
                <button
                  className={modoRuta === "tiempo" ? "toggle active" : "toggle"}
                  onClick={() => setModoRuta("tiempo")}
                >⏱ Tiempo</button>
                <button
                  className={modoRuta === "costo" ? "toggle active" : "toggle"}
                  onClick={() => setModoRuta("costo")}
                >💰 Costo</button>
              </div>
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={calcularRuta}
            disabled={!origen || !destino || loadingRuta}
          >
            {loadingRuta ? "Calculando..." : "Calcular ruta →"}
          </button>

          {rutaError && <div className="error-msg">⚠ {rutaError}</div>}
          <RouteResult data={rutaResult} />
        </section>
      )}

      {/* Panel: Cercanos */}
      {activeTab === "cercanos" && (
        <section className="panel">
          <div className="panel-header">
            <h2>Atracciones cercanas</h2>
            <p className="panel-desc">
              Búsqueda espacial con <strong>KD-Tree 2D</strong>.
              Complejidad: <code>O(√N + k)</code> vs <code>O(N)</code> lineal.
            </p>
          </div>

          <div className="form-field">
            <label>Partir desde una atracción conocida</label>
            <select
              className="select-input"
              onChange={(e) => seleccionarAtraccionBase(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>Selecciona una atracción…</option>
              {atracciones.map(a => (
                <option key={a.id} value={a.nombre}>{a.nombre}</option>
              ))}
            </select>
          </div>

          <div className="form-grid">
            <div className="form-field">
              <label>Latitud</label>
              <input className="text-input" type="number" step="0.0001"
                value={lat} onChange={e => setLat(e.target.value)}
                placeholder="19.4326" />
            </div>
            <div className="form-field">
              <label>Longitud</label>
              <input className="text-input" type="number" step="0.0001"
                value={lon} onChange={e => setLon(e.target.value)}
                placeholder="-99.1332" />
            </div>
            <div className="form-field">
              <label>Radio (km): <strong>{radio}</strong></label>
              <input type="range" min="1" max="20" value={radio}
                onChange={e => setRadio(e.target.value)} className="slider" />
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={calcularCercanos}
            disabled={!lat || !lon || loadingNearby}
          >
            {loadingNearby ? "Buscando..." : "Buscar cercanos →"}
          </button>

          <NearbyResult data={nearbyResult} />
        </section>
      )}

      {/* Panel: MST */}
      {activeTab === "mst" && (
        <section className="panel">
          <div className="panel-header">
            <h2>Red mínima de conexión</h2>
            <p className="panel-desc">
              <strong>Prim</strong> genera el Árbol de Expansión Mínima (MST):
              la red que conecta todas las atracciones con el menor costo total.
              Complejidad: <code>O(E log V)</code>
            </p>
          </div>

          <div className="form-field">
            <label>Minimizar por</label>
            <div className="toggle-group">
              <button
                className={modoPrim === "tiempo" ? "toggle active" : "toggle"}
                onClick={() => setModoPrim("tiempo")}
              >⏱ Tiempo total</button>
              <button
                className={modoPrim === "costo" ? "toggle active" : "toggle"}
                onClick={() => setModoPrim("costo")}
              >💰 Costo total</button>
            </div>
          </div>

          <button
            className="btn-primary"
            onClick={calcularMST}
            disabled={loadingMST}
          >
            {loadingMST ? "Calculando..." : "Generar red mínima →"}
          </button>

          <MSTResult data={mstResult} />
        </section>
      )}
    </main>
  );
}
