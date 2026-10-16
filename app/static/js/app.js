
"use strict";

const state = {
    page: 1,
    hasNext: false,
    pageSize: 10,
    parameters: null,
    saving: false,
};

const elements = {
    connectionStatus: document.getElementById("connection-status"),
    systemStatus: document.getElementById("system-status"),
    chlorineRange: document.getElementById("chlorine-range"),
    chlorineUnit: document.getElementById("chlorine-unit"),
    phRange: document.getElementById("ph-range"),
    form: document.getElementById("measurement-form"),
    chlorineInput: document.getElementById("chlorine-value"),
    phInput: document.getElementById("ph-value"),
    message: document.getElementById("form-message"),
    submitButton: document.getElementById("submit-button"),
    historyBody: document.getElementById("history-body"),
    pageInfo: document.getElementById("page-info"),
    previousButton: document.getElementById("previous-button"),
    nextButton: document.getElementById("next-button"),
    refreshButton: document.getElementById("refresh-button"),
};

function setConnection(connected) {
    const dot = document.querySelector(".status-dot");

    elements.connectionStatus.textContent = connected
        ? "Conectado"
        : "Sin conexión";

    dot.classList.toggle("connected", connected);
    dot.classList.toggle("disconnected", !connected);
    elements.systemStatus.textContent = connected ? "Operativo" : "Sin conexión";
}

function showMessage(message, type = "") {
    elements.message.textContent = message;
    elements.message.className = "message";

    if (type) {
        elements.message.classList.add(type);
    }
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...options.headers,
        },
    });

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("El servidor devolvió una respuesta no válida.");
    }

    if (!response.ok) {
        throw new Error(
            result.error || result.message || `Error HTTP ${response.status}.`
        );
    }

    return result;
}

function formatNumber(value, maximumFractionDigits = 3) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "—";
    }

    return new Intl.NumberFormat("es-CO", {
        maximumFractionDigits,
    }).format(number);
}

function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Fecha no válida";
    }

    return new Intl.DateTimeFormat("es-CO", {
        timeZone: "America/Bogota",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
    }).format(date);
}

function formatStatus(status) {
    return status || "—";
}

function createCell(text, status = false) {
    const cell = document.createElement("td");
    cell.textContent = text;

    if (status) {
        const normalized = String(text).toUpperCase();

        if (
            normalized === "CUMPLE" ||
            normalized === "DENTRO DEL RANGO"
        ) {
            cell.style.color = "#15803d";
            cell.style.fontWeight = "700";
        } else if (
            normalized === "NO CUMPLE" ||
            normalized === "BAJO" ||
            normalized === "ALTO" ||
            normalized === "INVÁLIDO"
        ) {
            cell.style.color = "#b91c1c";
            cell.style.fontWeight = "700";
        } else if (normalized === "SIN DATOS") {
            cell.style.color = "#64748b";
        }
    }

    return cell;
}

async function loadParameters() {
    const result = await apiRequest("/api/parameters");
    const parameters = result.parameters;

    if (!parameters || !parameters.chlorine || !parameters.ph) {
        throw new Error("La respuesta de parámetros está incompleta.");
    }

    state.parameters = parameters;

    const chlorine = parameters.chlorine;
    const ph = parameters.ph;

    elements.chlorineRange.textContent =
        `${formatNumber(chlorine.evaluation_min)} – ` +
        `${formatNumber(chlorine.evaluation_max)}`;

    elements.chlorineUnit.textContent =
        `Rango de evaluación (${chlorine.unit || "sin unidad"})`;

    elements.phRange.textContent =
        `${formatNumber(ph.evaluation_min)} – ` +
        `${formatNumber(ph.evaluation_max)}`;

    document.getElementById("chlorine-help").textContent =
        `Rango permitido: ${formatNumber(chlorine.evaluation_min)}–` +
        `${formatNumber(chlorine.evaluation_max)} ${chlorine.unit || ""}`.trim();

    document.getElementById("ph-help").textContent =
        `Rango permitido: ${formatNumber(ph.evaluation_min)}–` +
        `${formatNumber(ph.evaluation_max)}`;

    // Los límites definitivos también se validan en el backend.
    elements.chlorineInput.max = String(chlorine.simulation_max >= 0
        ? Math.max(Number(chlorine.simulation_max), Number(chlorine.evaluation_max))
        : chlorine.evaluation_max);

    elements.phInput.max = String(Math.max(
        Number(ph.simulation_max),
        Number(ph.evaluation_max)
    ));
}

function renderHistory(items) {
    elements.historyBody.replaceChildren();

    if (!items || items.length === 0) {
        const row = document.createElement("tr");
        const cell = createCell("Todavía no hay mediciones registradas.");
        cell.colSpan = 7;
        cell.className = "empty-state";
        row.appendChild(cell);
        elements.historyBody.appendChild(row);
        return;
    }

    for (const item of items) {
        const row = document.createElement("tr");

        row.appendChild(createCell(formatDate(item.measured_at)));
        row.appendChild(createCell(
            item.record_type === "automatic" ? "Automática" : "Manual"
        ));
        row.appendChild(createCell(formatNumber(item.chlorine_value)));
        row.appendChild(createCell(formatStatus(item.chlorine_status), true));
        row.appendChild(createCell(formatNumber(item.ph_value)));
        row.appendChild(createCell(formatStatus(item.ph_status), true));
        row.appendChild(createCell(formatStatus(item.overall_status), true));

        elements.historyBody.appendChild(row);
    }
}

async function loadHistory() {
    const result = await apiRequest(
        `/api/measurements?page=${encodeURIComponent(state.page)}`
    );

    renderHistory(result.items);

    state.page = result.page;
    state.pageSize = result.page_size;
    state.hasNext = result.has_next;

    elements.pageInfo.textContent = `Página ${state.page}`;
    elements.previousButton.disabled = state.page <= 1;
    elements.nextButton.disabled = !state.hasNext;
}

async function refreshData() {
    try {
        await Promise.all([loadParameters(), loadHistory()]);
        setConnection(true);
    } catch (error) {
        setConnection(false);
        showMessage(error.message, "error");
    }
}

function getOptionalNumber(input, label) {
    const raw = input.value.trim();

    if (!raw) {
        return null;
    }

    const normalized = raw.replace(",", ".");
    const number = Number(normalized);

    if (!Number.isFinite(number) || number < 0) {
        throw new Error(`${label}: ingresa un número válido no negativo.`);
    }

    return number;
}

async function submitMeasurement(event) {
    event.preventDefault();

    if (state.saving) {
        return;
    }

    let chlorine;
    let ph;

    try {
        chlorine = getOptionalNumber(
            elements.chlorineInput,
            "Cloro residual libre"
        );
        ph = getOptionalNumber(elements.phInput, "pH");

        if (chlorine === null && ph === null) {
            throw new Error("Ingresa al menos un valor de cloro o pH.");
        }
    } catch (error) {
        showMessage(error.message, "error");
        return;
    }

    state.saving = true;
    elements.submitButton.disabled = true;
    elements.submitButton.textContent = "Guardando...";
    showMessage("Guardando la medición...");

    try {
        const result = await apiRequest("/api/measurements", {
            method: "POST",
            body: JSON.stringify({
                chlorine_value: chlorine,
                ph_value: ph,
            }),
        });

        showMessage(result.message || "Medición guardada.", "success");
        elements.form.reset();

        state.page = 1;

        await loadParameters();
        await loadHistory();
        setConnection(true);
    } catch (error) {
        showMessage(error.message, "error");
    } finally {
        state.saving = false;
        elements.submitButton.disabled = false;
        elements.submitButton.textContent = "Guardar medición";
    }
}

elements.form.addEventListener("submit", submitMeasurement);

elements.refreshButton.addEventListener("click", async () => {
    elements.refreshButton.disabled = true;

    try {
        await refreshData();
    } finally {
        elements.refreshButton.disabled = false;
    }
});

elements.previousButton.addEventListener("click", async () => {
    if (state.page <= 1) {
        return;
    }

    state.page -= 1;

    try {
        await loadHistory();
    } catch (error) {
        state.page += 1;
        showMessage(error.message, "error");
    }
});

elements.nextButton.addEventListener("click", async () => {
    if (!state.hasNext) {
        return;
    }

    state.page += 1;

    try {
        await loadHistory();
    } catch (error) {
        state.page -= 1;
        showMessage(error.message, "error");
    }
});

refreshData();
