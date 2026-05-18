// components/RouteResult.jsx
// Muestra el resultado de Dijkstra: camino, tiempo y costo.

export function RouteResult({ data }) {
  if (!data) return null;
  const { camino, total_tiempo_min, total_costo_pesos, modo } = data;

  return (
    <div className="result-card">
      <div className="result-header">
        <span className="result-icon">🗺️</span>
        <h3>Ruta óptima <span className="tag">{modo === "tiempo" ? "⏱ tiempo" : "💰 costo"}</span></h3>
      </div>

      {/* Camino visual con flechas */}
      <div className="route-path">
        {camino.map((lugar, i) => (
          <span key={i} className="route-step">
            <span className="place-pill">{lugar}</span>
            {i < camino.length - 1 && <span className="arrow">→</span>}
          </span>
        ))}
      </div>

      <div className="result-stats">
        <div className="stat">
          <span className="stat-icon">⏱</span>
          <span className="stat-value">{total_tiempo_min} min</span>
          <span className="stat-label">Trayecto</span>
        </div>
        <div className="stat">
          <span className="stat-icon">💰</span>
          <span className="stat-value">${total_costo_pesos} MXN</span>
          <span className="stat-label">Costo</span>
        </div>
        <div className="stat">
          <span className="stat-icon">📍</span>
          <span className="stat-value">{camino.length - 1}</span>
          <span className="stat-label">Paradas</span>
        </div>
      </div>

      <div className="algo-badge">Algoritmo: Dijkstra · O((V+E) log V)</div>
    </div>
  );
}


// components/NearbyResult.jsx
// Lista de atracciones cercanas encontradas por el KD-Tree.

export function NearbyResult({ data }) {
  if (!data || !data.resultados) return null;
  const { resultados, radio_km } = data;

  return (
    <div className="result-card">
      <div className="result-header">
        <span className="result-icon">📡</span>
        <h3>Cercanos en {radio_km} km <span className="tag">{resultados.length} encontrados</span></h3>
      </div>

      {resultados.length === 0 ? (
        <p className="empty-msg">No hay atracciones en ese radio.</p>
      ) : (
        <ul className="nearby-list">
          {resultados.map((r) => (
            <li key={r.id} className="nearby-item">
              <div className="nearby-info">
                <strong>{r.nombre}</strong>
                <span className="tipo-badge">{r.tipo}</span>
              </div>
              <div className="nearby-meta">
                <span>⭐ {r.rating}</span>
                <span>📏 {r.distancia_km} km</span>
                <span>🕐 {r.tiempo_visita_min} min visita</span>
              </div>
            </li>
          ))}
        </ul>
      )}
      <div className="algo-badge">Algoritmo: KD-Tree · O(√N + k) vs O(N) lineal</div>
    </div>
  );
}


// components/MSTResult.jsx
// Árbol de Expansión Mínima generado por Prim.

export function MSTResult({ data }) {
  if (!data || !data.aristas) return null;
  const { aristas, total_tiempo_min, total_costo_pesos, modo } = data;

  return (
    <div className="result-card">
      <div className="result-header">
        <span className="result-icon">🕸️</span>
        <h3>Red mínima de conexión <span className="tag">{modo === "tiempo" ? "⏱ tiempo" : "💰 costo"}</span></h3>
      </div>

      <ul className="mst-list">
        {aristas.map((a, i) => (
          <li key={i} className="mst-item">
            <span className="mst-from">{a.de}</span>
            <span className="mst-arrow">⟶</span>
            <span className="mst-to">{a.hacia}</span>
            <span className="mst-weight">{a.tiempo_min} min · ${a.costo_pesos}</span>
          </li>
        ))}
      </ul>

      <div className="result-stats">
        <div className="stat">
          <span className="stat-icon">⏱</span>
          <span className="stat-value">{total_tiempo_min} min</span>
          <span className="stat-label">Total red</span>
        </div>
        <div className="stat">
          <span className="stat-icon">💰</span>
          <span className="stat-value">${total_costo_pesos} MXN</span>
          <span className="stat-label">Costo total</span>
        </div>
        <div className="stat">
          <span className="stat-icon">🔗</span>
          <span className="stat-value">{aristas.length}</span>
          <span className="stat-label">Aristas MST</span>
        </div>
      </div>
      <div className="algo-badge">Algoritmo: Prim · O(E log V)</div>
    </div>
  );
}
