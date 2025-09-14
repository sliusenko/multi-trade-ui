console.log("[forecast_vs_actual.js] loaded");

// Якщо вже маєш глобальні утиліти — використовуй їх. Інакше прості локальні:
async function asJson(x) {
  if (x && typeof x === "object" && "ok" in x && typeof x.json === "function") {
    if (!x.ok) {
      const text = await x.text().catch(()=>"");
      throw new Error(`HTTP ${x.status} ${text}`);
    }
    return await x.json();
  }
  return x;
}
function buildQuerySafe(params) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params || {})) {
    if (v == null) continue;
    const s = String(v).trim();
    if (!s || ["all","всі","усі"].includes(s.toLowerCase())) continue;
    q.append(k, s);
  }
  const qs = q.toString();
  return qs ? `?${qs}` : "";
}

let chart;
function renderChart(points, meta) {
  const ctx = document.getElementById("chart");
  if (chart) chart.destroy();

  const labels    = points.map(p => p.ts);
  const predicted = points.map(p => p.predicted_price);
  const actual    = points.map(p => p.actual_price);

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Прогноз", data: predicted, tension: .25, borderWidth: 2, spanGaps: true },
        { label: "Факт",    data: actual,    tension: .25, borderDash: [6,4], borderWidth: 2, pointRadius: 0, spanGaps: true },
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

async function loadChart() {
  const exchange = document.getElementById("exchange").value.trim();
  const pair = document.getElementById("pair").value.trim();
  const timeframe = document.getElementById("timeframe").value.trim();
  const interval = document.getElementById("interval").value;

  const res = await fetch(`/api/forecast_vs_actual_long?exchange=${exchange}&pair=${pair}&timeframe=${timeframe}&interval=${interval}`);
  const data = await res.json();
  const rows = data.rows || [];

  const ctx = document.getElementById("chartCanvas").getContext("2d");

  const labels = rows.map(r => new Date(r.ts_hour));
  const predicted = rows.map(r => r.predicted_price);
  const actual = rows.map(r => r.actual_price);

  if (window.chartInstance) {
    window.chartInstance.destroy();
  }

  window.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Predicted",
          data: predicted,
          borderColor: "blue",
          fill: false
        },
        {
          label: "Actual",
          data: actual,
          borderColor: "orange",
          borderDash: [5, 5],
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      scales: {
        x: {
          type: "time",
          time: {
            unit: "hour"
          }
        },
        y: {
          beginAtZero: false
        }
      }
    }
  });
}


async function loadAndRender() {
  const exchange  = document.getElementById("exchange").value.trim();
  const pair      = document.getElementById("pair").value.trim();
  const timeframe = document.getElementById("timeframe").value.trim();
  const interval  = document.getElementById("interval").value;
  const flh_tf    = document.getElementById("flh_timeframe").value;

  const url = "/api/forecast-vs-actual/data" + buildQuerySafe({
    exchange, pair, timeframe, interval, flh_timeframe: flh_tf
  });

  const resp = await asJson(fetch(url));
  const points = resp.points || [];

  const empty = document.getElementById("empty");
  if (!points.length) {
    empty.classList.remove("d-none");
    if (chart) chart.destroy();
    return;
  }
  empty.classList.add("d-none");
  renderChart(points, resp);
}

document.getElementById("controls").addEventListener("submit", (e) => {
  e.preventDefault();
  loadAndRender().catch(err => alert(err.message));
});

// Експорт CSV
document.getElementById("btnExport").addEventListener("click", () => {
  const exchange  = document.getElementById("exchange").value.trim();
  const pair      = document.getElementById("pair").value.trim();
  const timeframe = document.getElementById("timeframe").value.trim();
  const interval  = document.getElementById("interval").value;
  const flh_tf    = document.getElementById("flh_timeframe").value;

  const url = "/api/forecast_vs_actual_long" + buildQuerySafe({
    exchange, pair, timeframe, interval, flh_timeframe: flh_tf
  });

  fetch(url).then(r=>r.json()).then(resp=>{
    const rows = resp.points || [];
    if (!rows.length) return alert("Немає даних для експорту.");
    const header = "ts,predicted_price,actual_price\n";
    const body = rows.map(r => `${r.ts},${r.predicted_price ?? ""},${r.actual_price ?? ""}`).join("\n");
    const blob = new Blob([header + body], {type: "text/csv;charset=utf-8;"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `${pair}_${exchange}_${interval}_forecast_vs_actual.csv`;
    a.click();
    URL.revokeObjectURL(a.href);
  }).catch(err=>alert(err.message));
});

// авто-рендер стартових значень
loadAndRender().catch(console.error);
