// components/SearchBar.jsx
// Input con autocompletado en tiempo real.
// Cada keystroke llama al endpoint /autocomplete que usa el Trie del backend.

import { useState, useEffect, useRef } from "react";
import { getAutocomplete } from "./client.js";

export default function SearchBar({ placeholder, onSelect, value }) {
  const [input, setInput]         = useState(value || "");
  const [sugerencias, setSugerencias] = useState([]);
  const [abierto, setAbierto]     = useState(false);
  const debounceRef = useRef(null);

  useEffect(() => { setInput(value || ""); }, [value]);

  const handleChange = (e) => {
    const val = e.target.value;
    setInput(val);

    // Debounce: esperamos 200ms antes de llamar al backend
    // para no saturar con cada tecla
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      if (val.length >= 1) {
        const data = await getAutocomplete(val);
        setSugerencias(data.resultados || []);
        setAbierto(true);
      } else {
        setSugerencias([]);
        setAbierto(false);
      }
    }, 200);
  };

  const seleccionar = (nombre) => {
    setInput(nombre);
    setSugerencias([]);
    setAbierto(false);
    onSelect(nombre);
  };

  return (
    <div className="search-wrapper">
      <input
        className="search-input"
        type="text"
        placeholder={placeholder}
        value={input}
        onChange={handleChange}
        onBlur={() => setTimeout(() => setAbierto(false), 150)}
        onFocus={() => sugerencias.length > 0 && setAbierto(true)}
      />
      {abierto && sugerencias.length > 0 && (
        <ul className="autocomplete-list">
          {sugerencias.map((s) => (
            <li key={s.id} onMouseDown={() => seleccionar(s.nombre)}>
              {s.nombre}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
