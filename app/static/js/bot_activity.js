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

function renderChart(series, bucket) {
  const unit = bucket === "day" ? "day" : bucket === "hour" ? "hour" : "minute";

  // 1) перетворення у {x,y} та сорт по часу
  let points = (series || []).map(p => ({
    x: new Date(p.ts).getTime(), // даємо число (ms) — найменш проблемно
    y: Number(p.cnt)
  }));
  points.sort((a, b) => a.x - b.x);

  // 2) діагностика (дивись у консоль 1-2 записи)
  console.log("[bot_activity] points:", points.slice(0, 3), "... len:", points.length);

  const ctx = document.getElementById("activityChart").getContext("2d");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      // без labels — використовуємо {x,y}
      datasets: [{
        label: "Events",
        data: points,
        parsing: false,        // обов’язково для {x,y}
        spanGaps: true,
        tension: 0.25,
        pointRadius: 0,        // не малюємо точки (чіткіше)
        borderWidth: 2         // лінія товстіша, краще видно
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false, // щоб висота не «зажималась»
      animation: false,
      scales: {
        x: {
          type: "time",
          time: { unit },
          ticks: { autoSkip: true, maxTicksLimit: 10 }
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0 } // цілі
        }
      },
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            title: (items) => {
              const t = items?.[0]?.raw?.x;
              return t ? new Date(t).toLocaleString() : "";
            },
            label: (item) => `Count: ${item.raw?.y ?? ""}`
          }
        }
      }
    }
  });
  // фікс висоти (на всяк випадок)
  document.getElementById("activityChart").parentElement.style.height = "320px";
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
