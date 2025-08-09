<script>
/* ===== Strategy Weights ===== */
async function loadWeights() {
  const res = await apiFetch('/api/strategy_weights');
  const items = res.ok ? await res.json() : [];
  const tbody = document.getElementById('weightsTable');
  tbody.innerHTML = '';
  items.forEach(w => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${w.exchange}</td>
      <td>${w.pair}</td>
      <td>${(+w.rsi_weight).toFixed(2)}</td>
      <td>${(+w.forecast_weight).toFixed(2)}</td>
      <td>${(+w.acceleration_weight).toFixed(2)}</td>
      <td>${w.trade_logic}</td>
      <td>${w.updated_at ? new Date(w.updated_at).toLocaleString() : ''}</td>
      <td>
        <button class="btn btn-sm btn-outline-primary"
            onclick="prefillWeights('${w.exchange}','${w.pair}',${w.rsi_weight},${w.forecast_weight},${w.acceleration_weight},'${w.trade_logic}')">Edit</button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteWeights('${w.exchange}','${w.pair}')">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

function prefillWeights(exchange, pair, r, f, a, logic) {
  document.getElementById('w_exchange').value = exchange;
  document.getElementById('w_pair').value = pair;
  document.getElementById('w_rsi').value = r;
  document.getElementById('w_forecast').value = f;
  document.getElementById('w_accel').value = a;
  document.getElementById('w_logic').value = logic;
}

async function upsertWeights() {
  const payload = {
    exchange: document.getElementById('w_exchange').value.trim(),
    pair: document.getElementById('w_pair').value.trim(),
    rsi_weight: parseFloat(document.getElementById('w_rsi').value),
    forecast_weight: parseFloat(document.getElementById('w_forecast').value),
    acceleration_weight: parseFloat(document.getElementById('w_accel').value),
    trade_logic: document.getElementById('w_logic').value
  };
  if (!payload.exchange || !payload.pair) return alert('Exchange and pair are required');

  const res = await apiFetch('/api/strategy_weights', { method:'POST', body: JSON.stringify(payload) });
  if (!res.ok) return alert('Error saving weights');
  await loadWeights();
}

async function deleteWeights(exchange, pair) {
  if (!confirm(`Delete weights for ${exchange}:${pair}?`)) return;
  const res = await apiFetch(`/api/strategy_weights/${exchange}/${pair}`, { method:'DELETE' });
  if (!res.ok) return alert('Error deleting weights');
  await loadWeights();
}

/* ===== Initial load ===== */
document.addEventListener('DOMContentLoaded', () => {
  // твоя існуюча loadRules() вже є
  loadSets();
  loadWeights();
});
</script>
