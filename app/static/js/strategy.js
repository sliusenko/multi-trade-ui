// /static/js/strategy.js

async function apiFetch(url, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = options.headers || {};
  headers['Content-Type'] = 'application/json';
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return fetch(url, { ...options, headers });
}

function val(id) { return document.getElementById(id)?.value?.trim() ?? ""; }
function bool(id) { return !!document.getElementById(id)?.checked; }

function parsePriority(raw) {
  if (raw === "" || raw === null || raw === undefined) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? Math.trunc(n) : null;
}

function payloadFromForm() {
  return {
    action: val("action"),                          // "BUY" | "SELL"
    condition_type: val("condition_type"),          // e.g. "RSI_ABOVE"
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
    if (res.status === 401) {
      tbody.innerHTML = `<tr><td colspan="10">401 Unauthorized — перевір токен</td></tr>`;
      return;
    }
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
      <button class="btn btn-primary" onclick="openEditRule(${rule.id})">Edit</button>
      <button class="btn btn-warning" onclick="toggleEnabled(${rule.id}, ${!rule.enabled})">
        ${rule.enabled ? 'Disable' : 'Enable'}
      </button>
      <button class="btn btn-danger" onclick="deleteRule(${rule.id})">Delete</button>
    </div>
  `;

  cells.forEach(td => tr.appendChild(td));
  tr.appendChild(actionsTd);
  return tr;
}

async function addRule() {
  const body = payloadFromForm();
  console.log('[addRule] body=', body);

  let res = await apiFetch('/api/strategy_rules', {
    method: 'POST',
    body: JSON.stringify(body),
  });
  console.log('[addRule] POST /api/strategy_rules status=', res.status, res.url);

  // fallback, якщо бекенд очікує слеш
  if (res.status === 405 || res.status === 307 || res.status === 308) {
    res = await apiFetch('/api/strategy_rules/', {
      method: 'POST',
      body: JSON.stringify(body),
    });
    console.log('[addRule] POST /api/strategy_rules/ status=', res.status, res.url);
  }

  if (!res.ok && res.status !== 201) {
    const txt = await safeText(res);
    alert(`Add failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRules();
}

async function openEditRule(id) {
  try {
    const res = await apiFetch('/api/strategy_rules', { method: 'GET' });
    if (!res.ok) { alert('Cannot load rules for edit'); return; }
    const rules = await res.json();
    const r = rules.find(x => x.id === id);
    if (!r) { alert('Rule not found'); return; }

    // Простий prompt-редактор. Якщо хочеш — зроблю модалку.
    const action = prompt('Action (BUY/SELL):', r.action ?? '') ?? r.action;
    const condition_type = prompt('Condition type:', r.condition_type ?? '') ?? r.condition_type;
    const param_1 = prompt('Param1:', r.param_1 ?? '') ?? r.param_1;
    const param_2 = prompt('Param2:', r.param_2 ?? '') ?? r.param_2;
    const exchange = prompt('Exchange:', r.exchange ?? '') ?? r.exchange;
    const pair = prompt('Pair:', r.pair ?? '') ?? r.pair;
    const priorityStr = prompt('Priority (int or empty):', r.priority ?? '') ?? (r.priority ?? '');
    const enabledStr = prompt('Enabled (true/false):', String(r.enabled)) ?? String(r.enabled);

    const body = {
      action: (action || '').trim(),
      condition_type: (condition_type || '').trim(),
      param_1: (param_1 || '').trim() || null,
      param_2: (param_2 || '').trim() || null,
      exchange: (exchange || '').trim().toLowerCase() || null,
      pair: (pair || '').trim().toUpperCase() || null,
      priority: priorityStr === '' ? null : parsePriority(priorityStr),
      enabled: /^true$/i.test(enabledStr.trim()),
    };

    await updateRule(id, body);
  } catch (e) {
    console.error(e);
    alert('Edit failed');
  }
}

async function updateRule(id, body) {
  console.log('[updateRule] id=', id, 'body=', body);
  let res = await apiFetch(`/api/strategy_rules/${id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  console.log('[updateRule] PUT no-slash status=', res.status, res.url);

  if (res.status === 405 || res.status === 307 || res.status === 308) {
    res = await apiFetch(`/api/strategy_rules/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
    console.log('[updateRule] PUT with-slash status=', res.status, res.url);
  }

  if (!res.ok) {
    const txt = await safeText(res);
    alert(`Update failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRules();
}

async function toggleEnabled(id, newVal) {
  try {
    const res = await apiFetch(`/api/strategy_rules/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ enabled: !!newVal }),
    });
    if (res.ok) {
      await loadRules();
      return;
    }
    const txt = await safeText(res);
    alert(`Toggle failed: ${res.status}\n${txt}`);
  } catch (e) {
    console.error(e);
    alert('Network error on toggle');
  }
}

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

// Експортуємо в глобал
window.loadRules = loadRules;
window.addRule = addRule;
window.openEditRule = openEditRule;
window.updateRule = updateRule;
window.toggleEnabled = toggleEnabled;
window.deleteRule = deleteRule;




