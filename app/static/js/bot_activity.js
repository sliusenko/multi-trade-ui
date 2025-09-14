console.log("[bot_activity] loaded");

// утилітки
function fmtDTLocal(d) {
  // yyyy-MM-ddTHH:mm для <input type="datetime-local">
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
function qs(obj) {
  const p = new URLSearchParams();
  Object.entries(obj).forEach(([k, v]) => {
    if (v != null && String(v).trim() !== "") p.append(k, v);
  });
  return p.toString() ? "?" + p.toString() : "";
}
async function jget(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

let chart;

async function loadOptions() {
  const data = await jget("/api/bot-activity/options");
  const fill = (select, arr) => {
    select.innerHTML = `<option value="">All</option>` + arr.map(x => `<option value="${x}">${x}</option>`).join("");
  };
  fill(document.getElementById("f_exchange"), data.exchanges || []);
  fill(document.getElementById("f_pair"), data.pairs || []);
  fill(document.getElementById("f_signal_type"), data.signal_types || []);
}

function getFilters() {
  return {
    exchange: document.getElementById("f_exchange").value || "",
    pair: document.getElementById("f_pair").value || "",
    signalType: document.getElementById("f_signal_type").value || "",
    from: document.getElementById("f_from").value ? new Date(document.getElementById("f_from").value).toISOString() : "",
    to: document.getElementById("f_to").value ? new Date(document.getElementById("f_to").value).toISOString() : "",
    limit: 300
  };
}

async function loadData() {
  const filters = getFilters();
  const url = "/api/bot-activity/data" + qs(filters);
  const data = await jget(url);
  renderTable(data.rows || []);
  renderChart(data.series || []);
}

function renderTable(rows) {
  const tb = document.querySelector("#tbl tbody");
  tb.innerHTML = rows.map(r => `
    <tr>
      <td>${new Date(r.timestamp).toLocaleString()}</td>
      <td>${r.exchange}</td>
      <td>${r.pair}</td>
      <td>${r.signal}</td>
      <td><span class="badge text-bg-secondary">${r.signal_type}</span></td>
    </tr>
  `).join("");
}

function renderChart(series) {
  const labels = series.map(p => new Date(p.ts));
  const values = series.map(p => p.cnt);

  const ctx = document.getElementById("activityChart").getContext("2d");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Events",
        data: values,
        fill: false,
        tension: 0.25
      }]
    },
    options: {
      responsive: true,
      parsing: false,
      scales: {
        x: { type: "time", time: { unit: "minute" } },
        y: { beginAtZero: true }
      },
      plugins: {
        legend: { display: true }
      }
    }
  });
}

function setQuickRange(hours) {
  const to = new Date();
  const from = new Date(to.getTime() - hours*3600*1000);
  document.getElementById("f_to").value = fmtDTLocal(to);
  document.getElementById("f_from").value = fmtDTLocal(from);
}

(async function init() {
  // дефолт: останні 24 години
  setQuickRange(24);
  await loadOptions();

  document.getElementById("btn_apply").addEventListener("click", loadData);
  document.getElementById("btn_last24h").addEventListener("click", () => { setQuickRange(24); loadData(); });
  document.getElementById("btn_last7d").addEventListener("click", () => { setQuickRange(24*7); loadData(); });

  await loadData();
})();
