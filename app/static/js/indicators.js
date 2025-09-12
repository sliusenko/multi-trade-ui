// ===== Config =====
const API_ENDPOINT = "/api/analysis_data";

const INDICATORS = [
  "price","change","rsi","rsi_z","adx","plus_di","minus_di","rsi_z_sell_threshold","rsi_z_buy_threshold",
  "volume","ma_vol_5","ma_vol_10","avg_volume","macd","macd_signal","macd_prev",
  "macd_signal_prev","sma_50","sma_200","volatility","delta_price","acceleration",
  "open","close","high","low","price_z","volume_z","macd_diff_z","volatility_z",
  "sma_50_trend","sma_200_trend","sma_50_trend_strength","sma_200_trend_strength"
];

const DEFAULT_SELECTED = ["price","rsi_z","rsi_z_buy_threshold","rsi_z_sell_threshold","volume"];
const SECOND_AXIS_SUGGEST = new Set(["price","open","high","low","close","volume"]);

const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

function createCheckboxes() {
  const grid = $("#indicatorsCheckboxes");
  grid.innerHTML = "";
  INDICATORS.forEach(ind => {
    const id = `chk_${ind}`;
    const wrap = document.createElement("div");
    wrap.className = "form-check form-check-sm";
    wrap.innerHTML = `
      <input class="form-check-input" type="checkbox" name="indicators" value="${ind}" id="${id}">
      <label class="form-check-label" for="${id}">${ind}</label>
    `;
    grid.appendChild(wrap);
    const input = wrap.querySelector("input");
    if (DEFAULT_SELECTED.includes(ind)) input.checked = true;

    // second Y on double-click
    input.addEventListener("dblclick", () => {
      input.dataset.axis = input.dataset.axis === "y2" ? "" : "y2";
      input.parentElement.querySelector("label").classList.toggle("text-info");
    });

    if (SECOND_AXIS_SUGGEST.has(ind)) {
      input.dataset.axis = "y2";
      input.parentElement.querySelector("label").classList.add("text-info");
    }
  });
}

function qsFromForm(form) {
  const fd = new FormData(form);
  const params = new URLSearchParams();
  for (const [k, v] of fd.entries()) {
    if (!v) continue;
    if (k === "indicators") continue;
    params.append(k, v);
  }
  return params;
}

function applyQuickRange(tag) {
  const to = new Date();
  const from = new Date();
  const num = parseInt(tag);
  if (tag.endsWith("d")) from.setDate(to.getDate() - num);
  else if (tag.endsWith("h")) from.setHours(to.getHours() - num);

  const iso = (d) => {
    const pad = (x) => String(x).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };
  const form = $("#filtersForm");
  form.from.value = iso(from);
  form.to.value = iso(to);
}

function toCsv(rows) {
  if (!rows?.length) return "";
  const cols = ["timestamp", ...INDICATORS];
  const header = cols.join(",");
  const body = rows.map(r => cols.map(c => r[c] ?? "").join(",")).join("\n");
  return header + "\n" + body;
}

function download(filename, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], {type: "text/csv"}));
  a.download = filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1500);
}

// ===== Chart =====
let chart;
function buildChart(rows, selected) {
  const ctx = $("#chartCanvas").getContext("2d");

  // бейджі активних серій
  $("#activeIndicators").innerHTML = selected
    .map(s => `<span class="badge rounded-pill badge-ind">${s}</span>`).join("");

  const palette = (i) => `hsl(${(i*41)%360} 70% 55%)`;

  // будуємо серії у вигляді {x: Date, y: number}
  const datasets = selected.map((ind, i) => {
    const input = document.getElementById(`chk_${ind}`);
    const yAxisID = input?.dataset.axis === "y2" ? "y2" : "y";
    return {
      label: ind,
      data: rows.map(r => ({ x: new Date(r.timestamp), y: r[ind] ?? null })), // ⬅️ ключова зміна
      borderColor: palette(i),
      backgroundColor: "transparent",
      spanGaps: true,
      borderWidth: 1.6,
      pointRadius: 0,
      yAxisID,
    };
  });

  chart?.destroy();
  chart = new Chart(ctx, {
    type: "line",
    data: { datasets },                 // ⬅️ labels не потрібні
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      normalized: true,
      // parsing: false,                 // ⛔ при {x,y} не вимикаємо парсинг
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          type: 'time',
          time: { tooltipFormat: 'yyyy-LL-dd HH:mm' }, // ISO-8601 парситься адаптером
          ticks: { color: '#9aa3b2' },
          grid: { color: '#21263a' }
        },
        y:  { position: 'left',  ticks: { color: '#b7c0d0' }, grid: { color: '#21263a' } },
        y2: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#8ec1ff' } }
      },
      plugins: {
        legend: { labels: { color: "#d5d9e3" } },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`
          }
        }
      }
    }
  });
}

// ===== Data Load =====
async function loadData() {
  const form = $("#filtersForm");
  const selected = $$('input[name="indicators"]:checked').map(x => x.value);
  if (!selected.length) { $("#errorBox").style.display = "block"; $("#errorBox").textContent = "Оберіть хоча б один індикатор."; return; }

  $("#errorBox").style.display = "none";
  $("#spinner").style.display = "block";

  const qs = qsFromForm(form);
  history.replaceState(null, "", `${location.pathname}?${qs.toString()}`);

  const url = `${API_ENDPOINT}?${qs.toString()}`;
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`${resp.status} ${resp.statusText}`);
    const rows = await resp.json();

    buildChart(rows, selected);
    window.__lastRows = rows;
  } catch (e) {
    console.error(e);
    $("#errorBox").style.display = "block";
    $("#errorBox").textContent = e.message || "Помилка запиту";
  } finally {
    $("#spinner").style.display = "none";
  }
}

// ===== Wire-up =====
createCheckboxes();
$$('[data-range]').forEach(btn => btn.addEventListener("click", () => applyQuickRange(btn.dataset.range)));
$("#checkAll").addEventListener("click", () => $$('input[name="indicators"]').forEach(i => i.checked = true));
$("#uncheckAll").addEventListener("click", () => $$('input[name="indicators"]').forEach(i => i.checked = false));
$("#filtersForm").addEventListener("submit", (e) => { e.preventDefault(); loadData(); });
$("#btnReset").addEventListener("click", () => { document.getElementById("filtersForm").reset(); createCheckboxes(); $("#activeIndicators").innerHTML = ""; });
$("#btnExport").addEventListener("click", () => {
  const rows = window.__lastRows || [];
  if (!rows.length) return;
  const pair = new FormData($("#filtersForm")).get("pair") || "pair";
  download(`analysis_data_${pair}.csv`, toCsv(rows));
});

(function bootstrapFromUrl(){
  const url = new URL(location.href);
  const form = $("#filtersForm");
  const map = new Map(url.searchParams.entries());
  for (const [k,v] of map.entries()) { if (form[k]) form[k].value = v; }
  if (map.size) setTimeout(loadData, 50);
})();
