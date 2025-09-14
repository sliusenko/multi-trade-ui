async function loadData() {
  const filters = getFilters();
  const url = "/api/bot-activity/data" + qs(filters);
  const data = await jget(url);
  renderTable(data.rows || []);
  renderChart(data.series || [], data.bucket || "minute");
}

function renderChart(series, bucket) {
  const unit = bucket === "day" ? "day" : bucket === "hour" ? "hour" : "minute";

  // перетворюємо у {x, y} — так найнадійніше для time scale
  const points = (series || []).map(p => ({
    x: new Date(p.ts),   // p.ts очікується ISO-рядок з бекенда
    y: Number(p.cnt)     // на всякий — явно у Number
  }));

  const ctx = document.getElementById("activityChart").getContext("2d");
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{
        label: "Events",
        data: points,
        fill: false,
        spanGaps: true,
        tension: 0.25,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      parsing: false, // ми вже дали {x,y}
      scales: {
        x: {
          type: "time",
          time: { unit }
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0 } // цілі значення
        }
      },
      plugins: {
        legend: { display: true },
        tooltip: {
          callbacks: {
            title: (items) => items[0]?.raw?.x ? new Date(items[0].raw.x).toLocaleString() : "",
            label: (item) => `Count: ${item.raw?.y ?? ""}`
          }
        }
      }
    }
  });
}
