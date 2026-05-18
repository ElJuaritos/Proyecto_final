// api/client.js
// Todas las llamadas al backend en un solo lugar.
// Si el puerto cambia, solo hay que editar aquí.

const BASE_URL = "http://localhost:8000/api";

export async function getAtracciones() {
  const res = await fetch(`${BASE_URL}/atracciones`);
  return res.json();
}

export async function getAutocomplete(prefix) {
  if (!prefix || prefix.length < 1) return { resultados: [] };
  const res = await fetch(`${BASE_URL}/autocomplete?prefix=${encodeURIComponent(prefix)}`);
  return res.json();
}

export async function postShortestPath(origen, destino, modo = "tiempo") {
  const res = await fetch(`${BASE_URL}/shortest-path`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ origen, destino, modo }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Error al calcular ruta");
  }
  return res.json();
}

export async function getMST(modo = "tiempo") {
  const res = await fetch(`${BASE_URL}/mst?modo=${modo}`);
  return res.json();
}

export async function postNearby(latitud, longitud, radio_km = 5) {
  const res = await fetch(`${BASE_URL}/nearby`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitud, longitud, radio_km }),
  });
  return res.json();
}
