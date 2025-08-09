// ===== strategy_weights.js =====
console.log('[strategy_weights.js] loaded');

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = options.headers || {};
  headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(url, { ...options, headers });
}

function wVal(id){ return document.getElementById(id)?.value?.trim() ?? ""; }
function num(s){
  if (s === null || s === undefined) return null;
  const n = String(s).replace(',', '.').trim();
  if (n === '') return null;
  const f = Number(n);
  return Number.isFinite(f) ? f : null;
}

function weightPayloadFromForm(){
  return {
    exchange: wVal('w_exchange').toLowerCase(),
    pair: wVal('w_pair').toUpperCase(),
    rsi_weight: num(wVal('w_rsi')) ?? 1.0,
    forecast_weight: num(wVal('w_forecast')) ?? 1.0,
    acceleration_weight: num(wVal('w_accel')) ?? 1.0,
    trade_logic: wVal('w_logic') || 'COMBINER'
  };
}

async function loadWeights() {
  const tbody = document.getElementById('weightsTable');
  tbody.innerHTML = `<tr><td colspan="8">Loading…</td></tr>`;
  try {
    const res = await apiFetch('/api/strategy_weights', { method: 'GET' });
    if (!res.ok) { tbody.innerHTML = `<tr><td colspan="8">Error ${res.status}</td></tr>`; return; }
    const items = await res.json();
    tbody.innerHTML = '';
    items.forEach(w => tbody.appendChild(renderWeightRow(w)));
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="8">Network error</td></tr>`;
  }
}

function renderWeightRow(w) {
  const tr = document.createElement('tr');
  const cells = [
    w.exchange ?? '',
    w.pair ?? '',
    w.rsi_weight ?? '',
    w.forecast_weight ?? '',
    w.acceleration_weight ?? '',
    w.trade_logic ?? '',
    w.updated_at ? new Date(w.updated_at).toLocaleString() : ''
  ].map(t => { const td = document.createElement('td'); td.textContent = t; return td; });

  const actionsTd = document.createElement('td');
  actionsTd.innerHTML = `
    <div class="btn-group btn-group-sm" role="group">
      <button class="btn btn-primary">Edit</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  `;
  const [editBtn, delBtn] = actionsTd.querySelectorAll('button');

  editBtn.addEventListener('click', () => {
    // Заповнюємо форму зверху для редагування
    document.getElementById('w_exchange').value = (w.exchange ?? '').toLowerCase();
    document.getElementById('w_pair').value = (w.pair ?? '').toUpperCase();
    document.getElementById('w_rsi').value = w.rsi_weight ?? 1.0;
    document.getElementById('w_forecast').value = w.forecast_weight ?? 1.0;
    document.getElementById('w_accel').value = w.acceleration_weight ?? 1.0;
    document.getElementById('w_logic').value = w.trade_logic ?? 'COMBINER';
  });

  delBtn.addEventListener('click', () => deleteWeights(w.exchange, w.pair));

  cells.forEach(td => tr.appendChild(td));
  tr.appendChild(actionsTd);
  return tr;
}

async function upsertWeights() {
  console.log('[weights] upsert called');
  const body = weightPayloadFromForm();

  if (!body.exchange || !body.pair) {
    alert('Exchange і Pair — обовʼязкові');
    return;
  }

  let res = await apiFetch('/api/strategy_weights', {
    method: 'PUT', // upsert
    body: JSON.stringify(body),
  });
  if (!res.ok && [405,307,308].includes(res.status)) {
    res = await apiFetch('/api/strategy_weights/', { method:'PUT', body: JSON.stringify(body) });
  }
  if (!res.ok) {
    const txt = await res.text();
    alert(`Save failed: ${res.status}\n${txt}`);
    return;
  }

  await loadWeights();
}

async function deleteWeights(exchange, pair) {
  if (!confirm(`Delete weights ${exchange}/${pair}?`)) return;
  let res = await apiFetch(`/api/strategy_weights/${encodeURIComponent(exchange)}/${encodeURIComponent(pair)}`, {
    method: 'DELETE'
  });
  if (!res.ok && res.status !== 204) {
    const txt = await res.text();
    alert(`Delete failed: ${res.status}\n${txt}`);
    return;
  }
  await loadWeights();
}

// глобал
window.loadWeights = loadWeights;
window.upsertWeights = upsertWeights;
window.deleteWeights = deleteWeights;
