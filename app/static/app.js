const HORIZONS = [1, 3, 5, 10];
const MAX_EVOLUTION_STEP = 10;
const COLORS = ["#2e7d32", "#1565c0", "#ef6c00", "#6a1b9a"];

let states = [];
let charts = { bars: null, lines: null };

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  const entities = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };
  return String(value).replace(/[&<>"']/g, (char) => entities[char]);
}

function showError(message) {
  const errorBox = byId("error-message");
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  const errorBox = byId("error-message");
  errorBox.textContent = "";
  errorBox.hidden = true;
}

function renderMatrixTable(nextStates, matrix) {
  states = nextStates;
  const header = document.querySelector("#matrix-table thead");
  header.innerHTML =
    "<tr><th scope=\"col\">Desde / Hacia</th>" +
    nextStates.map((state) => `<th scope="col">${escapeHtml(state)}</th>`).join("") +
    "</tr>";

  byId("matrix-body").innerHTML = matrix
    .map(
      (row, rowIndex) =>
        `<tr><th scope="row">${escapeHtml(nextStates[rowIndex])}</th>` +
        row
          .map(
            (value, columnIndex) =>
              `<td><input type="number" step="any" value="${Number(value)}" ` +
              `data-row="${rowIndex}" data-col="${columnIndex}" ` +
              `aria-label="${escapeHtml(nextStates[rowIndex])} a ${escapeHtml(nextStates[columnIndex])}" /></td>`
          )
          .join("") +
        "</tr>"
    )
    .join("");
}

function readMatrixFromDOM() {
  const inputs = Array.from(document.querySelectorAll("#matrix-body input[data-row]"));
  if (inputs.length === 0) {
    throw new Error("No hay una matriz de transición para validar.");
  }

  const size = Math.round(Math.sqrt(inputs.length));
  if (size * size !== inputs.length || size < 3) {
    throw new Error("La matriz debe ser cuadrada y tener al menos 3 estados.");
  }

  const matrix = Array.from({ length: size }, () => Array(size).fill(0));

  for (const input of inputs) {
    const row = Number(input.dataset.row);
    const column = Number(input.dataset.col);
    const raw = input.value.trim();
    const value = Number(raw);

    if (raw === "" || !Number.isFinite(value)) {
      throw new Error(`El valor de la fila ${row + 1}, columna ${column + 1} no es numérico.`);
    }
    if (value < 0 || value > 1) {
      throw new Error(`El valor de la fila ${row + 1}, columna ${column + 1} debe estar entre 0 y 1.`);
    }
    matrix[row][column] = value;
  }

  for (let row = 0; row < size; row += 1) {
    const sum = matrix[row].reduce((total, value) => total + value, 0);
    if (Math.abs(sum - 1) > 1e-9) {
      throw new Error(`La fila ${row + 1} suma ${sum.toFixed(6)}; cada fila debe sumar 1.`);
    }
  }

  return matrix;
}

async function loadModel() {
  try {
    const response = await fetch("/api/model");
    if (!response.ok) {
      throw new Error("el servidor no devolvió el modelo");
    }
    const model = await response.json();
    byId("initial-state").innerHTML = model.states
      .map((state) => `<option value="${escapeHtml(state)}">${escapeHtml(state)}</option>`)
      .join("");
    renderMatrixTable(model.states, model.matrix);
  } catch (error) {
    showError(`No se pudo cargar el modelo: ${error.message}.`);
  }
}

function renderResults(payload) {
  const columns = ["Estado", ...HORIZONS.map((step) => `P(${step})`)];
  if (payload.stationary) {
    columns.push("Estacionaria");
  }
  byId("results-head").innerHTML =
    "<tr>" + columns.map((column) => `<th scope="col">${escapeHtml(column)}</th>`).join("") + "</tr>";

  byId("results-body").innerHTML = payload.states
    .map((state, index) => {
      const cells = HORIZONS.map(
        (step) => `<td>${Number(payload.distributions[String(step)][index]).toFixed(4)}</td>`
      );
      if (payload.stationary) {
        cells.push(`<td>${Number(payload.stationary[index]).toFixed(4)}</td>`);
      }
      return `<tr><th scope="row">${escapeHtml(state)}</th>${cells.join("")}</tr>`;
    })
    .join("");
}

function renderCharts(payload) {
  if (typeof Chart === "undefined") {
    showError("Chart.js no está disponible; los valores numéricos siguen visibles en la tabla.");
    return;
  }

  if (charts.bars) {
    charts.bars.destroy();
  }
  if (charts.lines) {
    charts.lines.destroy();
  }

  const barDatasets = HORIZONS.map((step, index) => ({
    label: `${step} pasos`,
    data: payload.states.map(
      (_, stateIndex) => Number(payload.distributions[String(step)][stateIndex])
    ),
    backgroundColor: COLORS[index % COLORS.length],
  }));
  if (payload.stationary) {
    barDatasets.push({
      label: "Estacionaria",
      data: payload.stationary,
      backgroundColor: "#9e9e9e",
    });
  }

  charts.bars = new Chart(byId("chart-bars"), {
    type: "bar",
    data: { labels: payload.states, datasets: barDatasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 1,
          ticks: { callback: (value) => Number(value).toFixed(1) },
        },
      },
      plugins: { legend: { position: "bottom" } },
    },
  });

  if (!payload.evolution) {
    return;
  }

  const labels = Array.from({ length: MAX_EVOLUTION_STEP + 1 }, (_, step) => step);
  const lineDatasets = payload.states.map((state, index) => ({
    label: state,
    data: labels.map((step) => Number(payload.evolution[state][step])),
    borderColor: COLORS[index % COLORS.length],
    backgroundColor: COLORS[index % COLORS.length],
    tension: 0.25,
    pointRadius: 2,
  }));

  if (payload.stationary) {
    payload.states.forEach((state, index) => {
      lineDatasets.push({
        label: `Estacionaria · ${state}`,
        data: labels.map(() => Number(payload.stationary[index])),
        borderColor: COLORS[index % COLORS.length],
        borderDash: [6, 4],
        pointRadius: 0,
      });
    });
  }

  charts.lines = new Chart(byId("chart-lines"), {
    type: "line",
    data: { labels: labels, datasets: lineDatasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { min: 0, max: 1 } },
      plugins: { legend: { position: "bottom" } },
    },
  });
}

async function calculate(event) {
  event.preventDefault();
  clearError();

  let matrix;
  try {
    matrix = readMatrixFromDOM();
  } catch (error) {
    showError(error.message);
    return;
  }

  const payload = {
    initial_state: byId("initial-state").value,
    steps: HORIZONS,
    matrix: matrix,
    include_evolution: true,
    max_evolution_step: MAX_EVOLUTION_STEP,
    include_stationary: byId("include-stationary").checked,
  };

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail =
        typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      throw new Error(detail || "No se pudo calcular la predicción.");
    }
    renderResults(data);
    renderCharts(data);
  } catch (error) {
    showError(`No se pudo calcular: ${error.message}`);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  byId("prediction-form").addEventListener("submit", calculate);
  loadModel();
});
