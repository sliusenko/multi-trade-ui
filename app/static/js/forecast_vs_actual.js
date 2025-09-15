console.log("[forecast_vs_actual.js] loaded");

// Утиліта: безпечний fetch + парсинг JSON
async function asJson(x) {
  if (x && typeof x === "object" && "ok" in x && typeof x.json === "function") {
    if (!x.ok) {
      const text = await x.text().catch(() => "");
      throw new Error(`HTTP ${x.status} ${text}`);
    }
    return await x.json();
  }
  return x;
}

// Побудова query-строки з параметрів
function buildQuerySafe(params) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params || {})) {
    if (v == null) continue;
    const s = String(v).trim();
    if (!s || ["all", "всі", "усі"].includes(s.toLowerCase())) continue;
    q.append(k, s);
  }
  return q.toString() ? "?" + q.toString() : "";
}

let chart = null;

// Побудова графіку
function renderChart(points, meta) {
  const ctx = document.getElementById("chart");
  if (chart) chart.destroy();

  const labels = points.map(p => p.ts);
  const predicted = points.map(p => p.predicted_price);
  const actual = points.map(p => p.actual_price);

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Прогноз",
          data: predicted,
          tension: 0.25,
          borderWidth: 2,
          spanGaps: true,
        },
        {
          label: "Факт",
          data: actual,
          tension: 0.25,
          borderDash: [6, 4],
          borderWidth: 2,
          pointRadius: 0,
          spanGaps: true,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#cfe3ff" }},
        title: {
          display: true,
          text: `${meta.pair} (${meta.exchange.toUpperCase()}, ${meta.timeframe}) — Прогноз vs Факт (${meta.interval})`,
          color: "#e9eef5"
        },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: {
            title: (items) => luxon.DateTime.fromISO(items[0].label).toFormat("yyyy-LL-dd HH:mm")
          }
        }
      },
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          type: "time",
          time: { unit: "hour" },
          ticks: { color: "#9bb2d1" },
          grid: { color: "rgba(155,178,209,0.1)" }
        },
        y: {
          ticks: { color: "#9bb2d1" },
          grid: { color: "rgba(155,178,209,0.1)" }
        }
      }
    }
  });
}

// Основна логіка завантаження і побудови графіку
async function loadAndRender() {
  const exchange = document.getElementById("exchange").value.trim();
  const pair = document.getElementById("pair").value.trim();
  const timeframe = document.getElementById("timeframe").value.trim();
  const interval = document.getElementById("interval").value;
  const flh_tf = document.getElementById("flh_timeframe").value;
  const user_id = document.getElementById("user_id").value.trim();

  const url = "/api/forecast_vs_actual_long" + buildQuerySafe({
    exchange, pair, timeframe, interval, flh_timeframe: flh_tf, user_id
  });

  const resp = await asJson(fetch(url));
  const points = resp.points ?? [];

  const empty = document.getElementById("empty");
  if (!points.length) {
    empty.classList.remove("d-none");
    if (chart) chart.destroy();
    return;
  }

  empty.classList.add("d-none");
  renderChart(points, resp);
}

// Обробка сабміту форми
document.getElementById("controls").addEventListener("submit", (e) => {
  e.preventDefault();
  loadAndRender().catch(err => alert("❌ Помилка: " + err.message));
});

// Експорт CSV
document.getElementById("btnExport").addEventListener("click", () => {
  const exchange = document.getElementById("exchange").value.trim();
  const pair = document.getElementById("pair").value.trim();
  const timeframe = document.getElementById("timeframe").value.trim();
  const interval = document.getElementById("interval").value;
  const flh_tf = document.getElementById("flh_timeframe").value;
  const user_id = document.getElementById("user_id").value.trim();

  const url = "/api/forecast_vs_actual_long" + buildQuerySafe({
    exchange, pair, timeframe, interval, flh_timeframe: flh_tf, user_id
  });

  fetch(url).then(r => r.json()).then(resp => {
    const rows = resp.points ?? [];
    if (!rows.length) return alert("Немає даних для експорту.");

    const header = "ts,predicted_price,actual_price\n";
    const body = rows.map(r =>
      `${r.ts},${r.predicted_price ?? ""},${r.actual_price ?? ""}`
    ).join("\n");

    const blob = new Blob([header + body], { type: "text/csv;charset=utf-8;" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${pair}_${exchange}_${interval}_forecast_vs_actual.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }).catch(err => alert("❌ Експорт не вдалось: " + err.message));
});

// Автоматичне завантаження на старті
window.addEventListener("DOMContentLoaded", () => {
  loadAndRender().catch(console.error);
});
