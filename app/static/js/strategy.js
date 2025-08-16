// ===== strategy.js =====
console.log('[strategy.js] loaded');

function val(id) { return document.getElementById(id)?.value?.trim() ?? ""; }

function bool(id) { return !!document.getElementById(id)?.checked; }

function parsePriority(raw) {
  if (raw === "" || raw === null || raw === undefined) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? Math.trunc(n) : null;
}

function payloadFromForm() {
  return {
    rule_id: parseInt(val("rule_id")),
    action: val("action"),
    condition_type: val("condition_type"),
    param_1: val("param_1") || null,
    param_2: val("param_2") || null,
    enabled: bool("enabled"),
    exchange: val("exchange").toLowerCase() || null,
    pair: val("pair").toUpperCase() || null,
    priority: parsePriority(val("priority")),
  };
}

async function loadRules() {
  const tbody = document.getElementById('rulesTable');
  tbody.innerHTML = `<tr><td colspan="10">Loading…</td></tr>`;
  try {
    const res = await apiFetch('/api/strategy_rules', { method: 'GET' });
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="10">Error ${res.status}</td></tr>`;
      return;
    }
    const rules = await res.json();
    tbody.innerHTML = '';
    rules.forEach(rule => tbody.appendChild(renderRuleRow(rule)));
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="10">Network error</td></tr>`;
  }
}

function renderRuleRow(rule) {
  const tr = document.createElement('tr');

  const cells = [
    rule.id,
    rule.action,
    rule.condition_type,
    rule.param_1 ?? '',
    rule.param_2 ?? '',
    rule.enabled ? '✅' : '❌',
    rule.exchange ?? '',
    rule.pair ?? '',
    rule.priority ?? '',
  ].map(text => {
    const td = document.createElement('td');
    td.textContent = text;
    return td;
  });

  const actionsTd = document.createElement('td');
  actionsTd.innerHTML = `
    <div class="btn-group btn-group-sm" role="group">
      <button class="btn btn-primary">Edit</button>
      <button class="btn btn-warning">${rule.enabled ? 'Disable' : 'Enable'}</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  `;

  // Прив'язуємо події
  const [editBtn, toggleBtn, delBtn] = actionsTd.querySelectorAll('button');

  editBtn.addEventListener('click', () => openEditRule(rule));
  toggleBtn.addEventListener('click', () => toggleEnabledSets_Rules(rule));
  delBtn.addEventListener('click', () => deleteRule(rule.id));

  cells.forEach(td => tr.appendChild(td));
  tr.appendChild(actionsTd);
  return tr;
}

// ====== Create ======
async function addRule() {
  console.log('[addRule] called');
  const body = payloadFromForm();
  console.log('[addRule] payload =', body);

  if (!body.action || !body.condition_type) {
    alert('action і condition_type — обовʼязкові');
    return;
  }

  let res = await apiFetch('/api/strategy_rules', {
    method: 'POST',
    body: JSON.stringify(body),
  });
  console.log('[addRule] POST status=', res.status, res.url);

  if (!res.ok && res.status !== 201) {
    // fallback із трейлінг-слешем
    if (res.status === 405 || res.status === 307 || res.status === 308) {
      res = await apiFetch('/api/strategy_rules/', {
        method: 'POST',
        body: JSON.stringify(body),
      });
      console.log('[addRule] POST / with slash status=', res.status);
    }
  }

  if (!res.ok && res.status !== 201) {
    const txt = await safeText(res);
    console.error('[addRule] failed', res.status, txt);
    alert(`Add failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRules();
}

// ====== Edit Modal ======
function openEditRule(rule) {
  window.__editRuleId__ = rule.id;

  document.getElementById('er_id').value = rule.id;
  document.getElementById('er_action').value = rule.action ?? 'BUY';
  document.getElementById('er_condition').value = rule.condition_type ?? '';
  document.getElementById('er_p1').value = rule.param_1 ?? '';
  document.getElementById('er_p2').value = rule.param_2 ?? '';
  document.getElementById('er_exchange').value = rule.exchange ?? '';
  document.getElementById('er_pair').value = rule.pair ?? '';
  document.getElementById('er_priority').value = rule.priority ?? '';
  document.getElementById('er_enabled').checked = !!rule.enabled;

  window.__gatherEditPayload__ = function() {
    // відправляємо лише змінені (але можна й усі)
    const payload = {};
    const action = document.getElementById('er_action').value.trim();
    const cond = document.getElementById('er_condition').value.trim();
    const p1 = document.getElementById('er_p1').value.trim();
    const p2 = document.getElementById('er_p2').value.trim();
    const ex = document.getElementById('er_exchange').value.trim().toLowerCase();
    const pair = document.getElementById('er_pair').value.trim().toUpperCase();
    const prStr = document.getElementById('er_priority').value.trim();
    const en = document.getElementById('er_enabled').checked;

    if (action) payload.action = action;
    if (cond) payload.condition_type = cond;
    payload.param_1 = p1 || null;
    payload.param_2 = p2 || null;
    payload.exchange = ex || null;
    payload.pair = pair || null;
    payload.priority = prStr === '' ? null : parsePriority(prStr);
    payload.enabled = !!en;

    return payload;
  };

  const modalEl = document.getElementById('editRuleModal');
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

// ====== Update ======
async function updateRule(id, body) {
  console.log('[updateRule] called', id, body);

  const qs = getFiltersQS();  // ← ключовий момент
  const res = await apiFetch(`/api/strategy_rules/${id}${qs}`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const txt = await safeText(res);
    console.error('[updateRule] failed', res.status, txt);
    alert(`Update failed: ${res.status}\n${txt}`);
    return;
  }

  await loadRules();  // перезавантажує таблицю
}

// ====== Toggle ======
async function toggleEnabledSets_Rules(rule) {
  const body = {
    action: (rule.action || '').trim(),
    condition_type: (rule.condition_type || '').trim(),
    param_1: isFinite(rule.param_1) ? parseFloat(rule.param_1) : null,
    param_2: isFinite(rule.param_2) ? parseFloat(rule.param_2) : null,
    exchange: (rule.exchange || '').toLowerCase() || null,
    pair: (rule.pair || '').toUpperCase() || null,
    priority: rule.priority ?? null,
    enabled: !rule.enabled,
  };

  try {
    const res = await apiFetch(`/api/strategy_rules/${rule.id}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const txt = await safeText(res);
      alert(`Toggle failed: ${res.status}\n${txt}`);
      return;
    }

    await loadRules();
  } catch (e) {
    console.error(e);
    alert('Network error on toggle');
  }
}

// ====== Delete ======
async function deleteRule(id) {
  if (!confirm(`Delete rule #${id}?`)) return;
  try {
    const res = await apiFetch(`/api/strategy_rules/${id}`, { method: 'DELETE' });
    if (res.ok || res.status === 204) {
      await loadRules();
      return;
    }
    const txt = await safeText(res);
    alert(`Delete failed: ${res.status}\n${txt}`);
  } catch (e) {
    console.error(e);
    alert('Network error on delete');
  }
}

async function safeText(res) {
  try { return await res.text(); } catch { return ''; }
}

// ====================== filters ==================
function getActiveFilters() {
  return {
    user_id: document.getElementById('filter_user')?.value || '',
    exchange: document.getElementById('filter_exchange')?.value || '',
    pair: document.getElementById('filter_pair')?.value || ''
  };
}

function buildQuery(params) {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v && usp.append(k, v));
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
}

async function loadRules() {
  const tbody = document.getElementById('rulesTable');
  tbody.innerHTML = `<tr><td colspan="10">Loading…</td></tr>`;
  const url = `/api/strategy_rules${buildQuery(getActiveFilters())}`;

  try {
    const res = await apiFetch(url, { method: 'GET' });
    if (!res.ok) {
      tbody.innerHTML = `<tr><td colspan="10">Error ${res.status}</td></tr>`;
      return;
    }
    const rules = await res.json();
    tbody.innerHTML = '';
    rules.forEach(rule => tbody.appendChild(renderRuleRow(rule)));
  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="10">Network error</td></tr>`;
  }
}

window.apiFetch ??= async function(url, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = options.headers || {};
  headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(url, { ...options, headers });
};
window.addEventListener('DOMContentLoaded', async () => {
  console.log('[init] DOM ready');

  // ... ваші кнопки/слухачі вище без змін ...

  // 1) завантажити списки фільтрів
  await loadFilters();

  // 2) підтягнути таблиці з поточними фільтрами
  try { if (typeof loadRules === 'function') await loadRules(); } catch(e){ console.error('loadRules err', e); }
  try { if (typeof loadSets === 'function')  await loadSets();  } catch(e){ console.error('loadSets err', e); }
  try { if (typeof loadWeights === 'function') await loadWeights(); } catch(e){ console.error('loadWeights err', e); }
});
window.loadRules = loadRules;
window.addRule = addRule;
window.updateRule = updateRule;
window.toggleEnabledSets_Rules = toggleEnabledSets_Rules;
window.deleteRule = deleteRule;
window.openEditRule = openEditRule;
window.getActiveFilters = function () {
  return {
    user_id: document.getElementById('filter_user')?.value || '',
    exchange: document.getElementById('filter_exchange')?.value || '',
    pair: document.getElementById('filter_pair')?.value || ''
  };
};
window.buildQuery = function (params) {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v && usp.append(k, v));
  const qs = usp.toString();
  return qs ? `?${qs}` : '';
};