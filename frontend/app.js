const API_BASE_URL =
  window.APP_CONFIG?.API_BASE_URL || "http://127.0.0.1:8000";

const queryInput = document.getElementById("query");
const sourceInput = document.getElementById("source");
const yearInput = document.getElementById("year");
const documentTypeInput = document.getElementById("documentType");

const limitInput = document.getElementById("limit");
const hybridLimitInput = document.getElementById("hybridLimit");
const denseLimitInput = document.getElementById("denseLimit");
const bm25LimitInput = document.getElementById("bm25Limit");

const askButton = document.getElementById("askButton");
const retrieveButton = document.getElementById("retrieveButton");
const resetButton = document.getElementById("resetButton");
const healthButton = document.getElementById("healthButton");
const exampleButtons = document.querySelectorAll(".example-button");

const backendDot = document.getElementById("backendDot");
const backendText = document.getElementById("backendText");

const statusBox = document.getElementById("status");
const answerSection = document.getElementById("answerSection");
const answerBox = document.getElementById("answer");
const sourcesSection = document.getElementById("sourcesSection");
const sourcesBox = document.getElementById("sources");

function buildFilters() {
  const filters = {};

  if (sourceInput.value) {
    filters.source = sourceInput.value;
  }

  if (yearInput.value) {
    filters.year = Number(yearInput.value);
  }

  if (documentTypeInput.value) {
    filters.document_type = documentTypeInput.value;
  }

  return Object.keys(filters).length > 0 ? filters : null;
}

function getNumberValue(input, fallback) {
  const value = Number(input.value);

  if (Number.isNaN(value) || value <= 0) {
    return fallback;
  }

  return value;
}

function buildRequestBody() {
  return {
    query: queryInput.value.trim(),
    filters: buildFilters(),
    limit: getNumberValue(limitInput, 5),
    hybrid_limit: getNumberValue(hybridLimitInput, 20),
    dense_limit: getNumberValue(denseLimitInput, 30),
    bm25_limit: getNumberValue(bm25LimitInput, 30),
  };
}

function showStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.classList.remove("hidden");

  if (isError) {
    statusBox.classList.add("error");
  } else {
    statusBox.classList.remove("error");
  }
}

function hideStatus() {
  statusBox.classList.add("hidden");
  statusBox.classList.remove("error");
  statusBox.textContent = "";
}

function hideResults() {
  answerSection.classList.add("hidden");
  sourcesSection.classList.add("hidden");

  answerBox.innerHTML = "";
  sourcesBox.innerHTML = "";
}

function setButtonsDisabled(isDisabled) {
  askButton.disabled = isDisabled;
  retrieveButton.disabled = isDisabled;
  resetButton.disabled = isDisabled;
  healthButton.disabled = isDisabled;

  exampleButtons.forEach((button) => {
    button.disabled = isDisabled;
  });
}

function formatScore(score) {
  if (score === null || score === undefined) {
    return "N/A";
  }

  const number = Number(score);

  if (Number.isNaN(number)) {
    return "N/A";
  }

  return number.toFixed(4);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderAnswer(answer) {
  answerBox.innerHTML = "";

  const container = document.createElement("div");
  container.className = "answer-list";

  const lines = answer
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  lines.forEach((line) => {
    const item = document.createElement("div");
    item.className = "answer-item";

    const escapedLine = escapeHtml(line);

    const withCitations = escapedLine.replace(
      /\[(\d+)\]/g,
      '<span class="citation">[$1]</span>'
    );

    item.innerHTML = withCitations;
    container.appendChild(item);
  });

  answerBox.appendChild(container);
  answerSection.classList.remove("hidden");
}

function renderResultSummary(mode, sourceCount, durationMs) {
  const summary = document.createElement("div");
  summary.className = "result-summary";

  const modeLabel = mode === "/query" ? "Full RAG answer" : "Retrieval only";

  summary.textContent = `${modeLabel} completed in ${durationMs} ms. Sources returned: ${sourceCount}.`;

  sourcesBox.prepend(summary);
}

function renderSources(sources) {
  sourcesBox.innerHTML = "";

  if (!sources || sources.length === 0) {
    sourcesBox.innerHTML = "<p>No sources returned.</p>";
    sourcesSection.classList.remove("hidden");
    return;
  }

  sources.forEach((source) => {
    const card = document.createElement("div");
    card.className = "source-card";

    const documentName = escapeHtml(source.document_name ?? "Unknown document");
    const sourceName = escapeHtml(source.source ?? "Unknown");
    const documentType = escapeHtml(source.document_type ?? "Unknown");
    const textPreview = escapeHtml(source.text_preview ?? "");

    card.innerHTML = `
      <details ${source.index === 1 ? "open" : ""}>
        <summary>[${source.index}] ${documentName}</summary>

        <div class="badges">
          <span class="badge">Source: ${sourceName}</span>
          <span class="badge">Year: ${source.year ?? "Unknown"}</span>
          <span class="badge">Type: ${documentType}</span>
          <span class="badge">Chunk: ${source.chunk_id ?? "Unknown"}</span>
        </div>

        <div class="preview">
          ${textPreview}
        </div>

        <div class="score-grid">
          <div class="score-item">
            <span class="score-label">Reranker</span>
            <span class="score-value">${formatScore(source.reranker_score)}</span>
          </div>

          <div class="score-item">
            <span class="score-label">RRF</span>
            <span class="score-value">${formatScore(source.rrf_score)}</span>
          </div>

          <div class="score-item">
            <span class="score-label">Dense</span>
            <span class="score-value">${formatScore(source.dense_score)}</span>
          </div>

          <div class="score-item">
            <span class="score-label">BM25</span>
            <span class="score-value">${formatScore(source.bm25_score)}</span>
          </div>
        </div>
      </details>
    `;

    sourcesBox.appendChild(card);
  });

  sourcesSection.classList.remove("hidden");
}

async function sendRequest(endpoint) {
  const requestBody = buildRequestBody();

  if (!requestBody.query) {
    hideResults();
    showStatus("Please enter a question.", true);
    return;
  }

  const startTime = performance.now();

  hideResults();

  if (endpoint === "/query") {
    showStatus("Generating answer with retrieval, reranking, and LLM...");
  } else {
    showStatus("Retrieving and reranking sources...");
  }

  setButtonsDisabled(true);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    const durationMs = Math.round(performance.now() - startTime);

    hideStatus();

    if (data.answer) {
      renderAnswer(data.answer);
    }

    renderSources(data.sources || []);
    renderResultSummary(endpoint, data.sources ? data.sources.length : 0, durationMs);
  } catch (error) {
    hideResults();
    showStatus(error.message, true);
  } finally {
    setButtonsDisabled(false);
  }
}

function resetForm() {
  queryInput.value = "";
  sourceInput.value = "";
  yearInput.value = "";
  documentTypeInput.value = "";

  limitInput.value = "5";
  hybridLimitInput.value = "20";
  denseLimitInput.value = "30";
  bm25LimitInput.value = "30";

  hideResults();
  hideStatus();
}

async function checkBackendHealth() {
  showStatus("Checking backend health...");
  setButtonsDisabled(true);

  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error("Backend health check failed.");
    }

    backendDot.className = "backend-dot ok";
    backendText.textContent = `Backend online · ${data.chunks_loaded} chunks`;

    showStatus(`Backend is running. Chunks loaded: ${data.chunks_loaded}`);
  } catch (error) {
    backendDot.className = "backend-dot error";
    backendText.textContent = "Backend offline";

    showStatus("Backend is not reachable. Make sure uvicorn api.main:app is running.", true);
  } finally {
    setButtonsDisabled(false);
  }
}

askButton.addEventListener("click", () => {
  sendRequest("/query");
});

retrieveButton.addEventListener("click", () => {
  sendRequest("/retrieve");
});

resetButton.addEventListener("click", () => {
  resetForm();
});

healthButton.addEventListener("click", () => {
  checkBackendHealth();
});

exampleButtons.forEach((button) => {
  button.addEventListener("click", () => {
    queryInput.value = button.dataset.query || "";
    sourceInput.value = button.dataset.source || "";
    yearInput.value = button.dataset.year || "";
    documentTypeInput.value = button.dataset.documentType || "";

    hideResults();
    hideStatus();
  });
});

checkBackendHealth();
