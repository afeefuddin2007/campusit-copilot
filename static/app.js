/* GSU CampusIT Copilot Frontend Controller */

const state = { conversationHistory: [], kbArticles: [], lastRetrievedChunks: [] };

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initScenarioShortcuts();
  initChatForm();
  loadHealth();
  loadKnowledgeBase();
  loadTelemetryAndEval();
});

function initTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab");
  const panels = document.querySelectorAll(".tab-panel");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      tabButtons.forEach(b => { b.classList.remove("active"); b.setAttribute("aria-selected", "false"); });
      panels.forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      document.getElementById(`tab-${target}`).classList.add("active");
      if (target === "eval") loadTelemetryAndEval();
    });
  });
}

function initScenarioShortcuts() {
  document.querySelectorAll(".scenario-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-prompt");
      document.getElementById("chat-input").value = prompt;
      submitUserMessage(prompt);
    });
  });
  document.getElementById("clear-chat-btn").addEventListener("click", () => {
    state.conversationHistory = [];
    document.getElementById("chat-messages").innerHTML = `
      <div class="message assistant-message">
        <div class="msg-avatar">🐾</div>
        <div class="msg-bubble">
          <div class="msg-meta"><strong>GSU CampusIT Copilot</strong><span class="meta-badge">Session Reset</span></div>
          <div class="msg-content"><p>Conversation memory cleared!</p></div>
        </div>
      </div>
    `;
  });
}

function initChatForm() {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;
    submitUserMessage(msg);
  });
}

async function submitUserMessage(messageText) {
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("send-btn");
  input.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Searching KB...";
  appendMessage("user", messageText);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: messageText, history: state.conversationHistory })
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map(item => item.msg).join("; ")
        : data.detail;
      throw new Error(detail || `Request failed (HTTP ${response.status})`);
    }
    state.lastRetrievedChunks = data.retrieved_chunks || [];
    state.conversationHistory.push({ role: "user", content: messageText });
    state.conversationHistory.push({ role: "assistant", content: data.answer });
    appendAssistantResponse(data);
    renderInspector(data);
  } catch (err) {
    appendMessage("assistant", `⚠️ Error: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Ask Copilot ➤";
  }
}

function appendMessage(role, rawText) {
  const container = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}-message`;
  wrapper.innerHTML = `
    <div class="msg-avatar">${role === "user" ? "🎓" : "🐾"}</div>
    <div class="msg-bubble">
      <div class="msg-meta"><strong>${role === "user" ? "GSU Student" : "GSU CampusIT Copilot"}</strong></div>
      <div class="msg-content"><p>${escapeHtml(rawText)}</p></div>
    </div>
  `;
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function appendAssistantResponse(data) {
  const container = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = "message assistant-message";
  const formattedHtml = formatMarkdownWithCitations(data.answer);
  const badgeText = data.engine_mode === "conversation-helper" ? "Conversation" : data.escalated ? "🚨 Guardrail Escalated" : `✅ Grounded RAG (${data.latency_ms}ms)`;

  let escalationHtml = "";
  if (data.escalated && data.escalation_details) {
    const t = data.escalation_details;
    escalationHtml = `
      <div class="escalation-card">
        <div class="esc-header"><span>📋 ServiceNow Escalation Ticket</span><span class="mono">${escapeHtml(t.ticket_id)}</span></div>
        <div class="esc-grid">
          <div><strong>Priority:</strong> ${escapeHtml(t.priority)}</div>
          <div><strong>Category:</strong> ${escapeHtml(t.category)}</div>
          <div><strong>Assignment Group:</strong> ${escapeHtml(t.assignment_group)}</div>
          <div><strong>Phone:</strong> ${escapeHtml(t.contact_phone)}</div>
        </div>
      </div>
    `;
  }

  wrapper.innerHTML = `
    <div class="msg-avatar">🐾</div>
    <div class="msg-bubble">
      <div class="msg-meta"><strong>GSU CampusIT Copilot</strong><span class="meta-badge">${badgeText}</span></div>
      <div class="msg-content">${formattedHtml}${escalationHtml}</div>
    </div>
  `;
  wrapper.querySelectorAll(".citation-chip").forEach(chip => {
    chip.addEventListener("click", () => highlightInspectorChunk(chip.getAttribute("data-kb")));
  });
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function renderInspector(data, highlightedKbId = null) {
  const container = document.getElementById("inspector-content");
  const chunks = data.retrieved_chunks || [];
  if (!chunks.length) { container.innerHTML = `<p>No chunks retrieved.</p>`; return; }
  const guardBanner = data.escalated
    ? `<div style="background:#fee2e2;color:#991b1b;padding:0.55rem;border-radius:6px;font-size:0.78rem;font-weight:600;margin-bottom:0.75rem;">🛡️ Guardrail: ${escapeHtml(data.escalation_rule)}</div>`
    : `<div style="background:#dcfce7;color:#166534;padding:0.55rem;border-radius:6px;font-size:0.78rem;font-weight:600;margin-bottom:0.75rem;">✅ Top Similarity: ${(data.top_similarity * 100).toFixed(1)}%</div>`;

  container.innerHTML = guardBanner + chunks.map((c, idx) => `
    <div class="chunk-card ${highlightedKbId === c.kb_id || (!highlightedKbId && idx === 0) ? "active-chunk" : ""}" id="insp-${c.kb_id}">
      <div class="chunk-top"><span class="chunk-id">📄 ${escapeHtml(c.kb_id)}</span><span class="sim-pill">${(c.similarity_score * 100).toFixed(1)}%</span></div>
      <div class="chunk-title">${escapeHtml(c.title)}</div>
      <div class="chunk-summary">${escapeHtml(c.summary)}</div>
    </div>
  `).join("");
}

function highlightInspectorChunk(kbId) {
  document.querySelectorAll(".chunk-card").forEach(el => el.classList.remove("active-chunk"));
  const target = document.getElementById(`insp-${kbId}`);
  if (target) target.classList.add("active-chunk");
}

async function loadKnowledgeBase() {
  try {
    const res = await fetch("/api/kb");
    const data = await res.json();
    state.kbArticles = data.articles || [];
    document.getElementById("kb-count-pill").textContent = state.kbArticles.length;
    renderKbGrid(state.kbArticles);
    document.getElementById("kb-search-input").addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      renderKbGrid(state.kbArticles.filter(a => a.kb_id.toLowerCase().includes(q) || a.title.toLowerCase().includes(q)));
    });
  } catch (e) { console.error(e); }
}

function renderKbGrid(articles) {
  document.getElementById("kb-articles-grid").innerHTML = articles.map(a => `
    <article class="kb-article-card">
      <span class="citation-chip">${escapeHtml(a.kb_id)}</span>
      <h3>${escapeHtml(a.title)}</h3>
      <p style="font-size:0.82rem;color:#475569;margin-bottom:0.5rem;">${escapeHtml(a.summary)}</p>
      <ul class="kb-steps-list">${a.steps.map(s => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
    </article>
  `).join("");
}

async function loadTelemetryAndEval() {
  try {
    const res = await fetch("/api/telemetry");
    const data = await res.json();
    if (data.benchmark_report) renderEvalReport(data.benchmark_report);
    renderLiveTelemetry(data.recent_events || []);
  } catch (err) { console.error(err); }

  const runBtn = document.getElementById("run-eval-btn");
  if (runBtn && !runBtn.dataset.bound) {
    runBtn.dataset.bound = "true";
    runBtn.addEventListener("click", async () => {
      runBtn.disabled = true;
      runBtn.textContent = "⏳ Evaluating 120 Scenarios...";
      try {
        const res = await fetch("/api/eval/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sample_size: 120 }) });
        renderEvalReport(await res.json());
      } finally {
        runBtn.disabled = false;
        runBtn.textContent = "▶ Run 120-Question Benchmark Now";
      }
    });
  }
}

function renderEvalReport(report) {
  const m = report.metrics || {};
  document.getElementById("kpi-hit-top3").textContent = `${m.retrieval_hit_rate_top3}%`;
  document.getElementById("kpi-hit-top1").textContent = `Top-1: ${m.retrieval_hit_rate_top1}%`;
  document.getElementById("kpi-citation").textContent = `${m.citation_faithfulness_rate}%`;
  document.getElementById("kpi-esc-acc").textContent = `${m.escalation_accuracy}%`;
  document.getElementById("kpi-esc-pr").textContent = `Precision: ${m.escalation_precision}% | Recall: ${m.escalation_recall}%`;
  document.getElementById("kpi-exec-time").textContent = `Execution Time: ${report.elapsed_seconds}s`;

  document.getElementById("eval-category-tbody").innerHTML = (report.category_breakdown || []).map(c => `
    <tr>
      <td><strong>${escapeHtml(c.category)}</strong></td>
      <td>${c.count}</td>
      <td><span class="status-pass">${c.retrieval_hit_rate}%</span></td>
      <td><span class="status-pass">${c.citation_accuracy}%</span></td>
      <td><span class="status-pass">${c.escalation_accuracy}%</span></td>
    </tr>
  `).join("");
}

function renderLiveTelemetry(events) {
  const tbody = document.getElementById("telemetry-tbody");
  if (!events.length) return;
  tbody.innerHTML = events.map(ev => `
    <tr>
      <td class="mono">${escapeHtml(ev.timestamp)}</td>
      <td>${escapeHtml(ev.query)}</td>
      <td class="mono">${escapeHtml(ev.top_kb)}</td>
      <td class="mono">${(ev.similarity * 100).toFixed(1)}%</td>
      <td>${ev.escalated ? '<span class="status-esc">Escalated</span>' : '<span class="status-pass">Answered</span>'}</td>
    </tr>
  `).join("");
}

function formatMarkdownWithCitations(md) {
  let html = escapeHtml(md);
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/`([^`]+)`/g, '<code class="mono" style="background:#e2e8f0;padding:0.1rem 0.3rem;border-radius:4px;">$1</code>');
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#0039A6;font-weight:600;text-decoration:underline;">$1 ↗</a>');
  html = html.replace(/\[(KB\d+)\]/g, '<button type="button" class="citation-chip" data-kb="$1">📌 $1</button>');
  const blocks = [];
  let listType = null;
  const closeList = () => {
    if (listType) blocks.push(`</${listType}>`);
    listType = null;
  };
  for (const rawLine of html.split("\n")) {
    const line = rawLine.trim();
    const numbered = line.match(/^\d+\.\s+(.*)$/);
    const bullet = line.match(/^-\s+(?:\d+\.\s+)?(.*)$/);
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (numbered || bullet) {
      const type = numbered ? "ol" : "ul";
      if (listType !== type) { closeList(); blocks.push(`<${type}>`); listType = type; }
      blocks.push(`<li>${(numbered || bullet)[1]}</li>`);
    } else {
      closeList();
      if (heading) blocks.push(`<h${heading[1].length}>${heading[2]}</h${heading[1].length}>`);
      else if (line) blocks.push(`<p>${line}</p>`);
    }
  }
  closeList();
  return blocks.join("\n");
}

function escapeHtml(str) {
  return String(str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function loadHealth() {
  const badge = document.getElementById("health-badge");
  try {
    const response = await fetch("/api/health");
    if (!response.ok) throw new Error("Health check failed");
    const health = await response.json();
    badge.textContent = health.chroma_vector_db_active
      ? "● API Ready · ChromaDB Initialized"
      : "● API Ready · Keyword Retrieval";
  } catch (err) {
    badge.textContent = "● API Unavailable";
  }
}
