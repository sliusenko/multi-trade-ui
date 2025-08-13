// ==== helpers ====
function getFiltersQS() {
  const { user_id, exchange, pair } = getActiveFilters(); // твоя існуюча функція
  return buildQuery({ user_id, exchange, pair });         // твій існуючий хелпер
}

// ==== селект для "прикріпити правило до сету" ====
async function refreshAttachSelect(setId) {
  const qs = getFiltersQS();
  const all = await (await apiFetch(`/api/strategy_rules${qs}`)).json();
  const inSet = await (await apiFetch(`/api/strategy_sets/${setId}/rules${qs}`)).json();
  const inSetIds = new Set(inSet.map(x => x.rule_id));
  const sel = document.getElementById('ruleSelect');
  sel.innerHTML = all
    .filter(r => !inSetIds.has(r.id))
    .map(r => `<option value="${r.id}">[${r.id}] ${r.action} ${r.condition_type} ${r.param_1 ?? ''}/${r.param_2 ?? ''}</option>`)
    .join('');
}

// ==== оновлення дропдауну правил з урахуванням фільтрів ====
async function refreshAttachRuleDropdown() {
  const qs = getFiltersQS();
  const res = await apiFetch(`/api/strategy_rules${qs}`);
  if (!res.ok) return;
  const rules = await res.json();

  const ruleSelect = document.getElementById('ruleSelect');
  if (ruleSelect) {
    const keep = ruleSelect.value;
    ruleSelect.innerHTML = '';
    rules.forEach(r => {
      const o = document.createElement('option');
      const suffix = [r.exchange, r.pair].filter(Boolean).join(' ');
      o.value = r.id;
      o.textContent = suffix ? `${r.action} ${r.condition_type} (${suffix})` : `${r.action} ${r.condition_type}`;
      ruleSelect.appendChild(o);
    });
    if (keep && [...ruleSelect.options].some(o => o.value === keep)) {
      ruleSelect.value = keep;
    }
  }
}

// ==== завантаження списку сетів у селект (з фільтрами) ====
async function loadSetsIntoSelect() {
  const qs = getFiltersQS();
  const res = await apiFetch(`/api/strategy_sets${qs}`);
  if (!res.ok) { console.error('Failed to load sets'); return; }
  const sets = await res.json();

  const sel = document.getElementById('setSelect');
  const keep = sel.value;
  sel.innerHTML = sets.map(s => `<option value="${s.id}">${s.name}</option>`).join('');

  // зберегти вибір, якщо ще існує
  if (keep && [...sel.options].some(o => o.value === keep)) {
    sel.value = keep;
  }
  sel.onchange = loadRulesForSelectedSet;

  await loadRulesForSelectedSet();
}

// ==== завантаження правил для вибраного сету (з фільтрами) ====
async function loadRulesForSelectedSet() {
  const setId = document.getElementById('setSelect').value;
  if (!setId) return;

  const qs = getFiltersQS();

  // підтягнути всі правила (для дропдауну додавання)
  const allRules = await (await apiFetch(`/api/strategy_rules${qs}`)).json();
  document.getElementById('ruleSelect').innerHTML =
    allRules.map(r => `<option value="${r.id}">[${r.id}] ${r.action} ${r.condition_type} ${r.param_1 ?? ''}/${r.param_2 ?? ''}</option>`).join('');

  // підтягнути правила в сеті
  const res = await apiFetch(`/api/strategy_sets/${setId}/rules${qs}`);
  const items = await res.json();

  const tbody = document.getElementById('setRulesTbody');
  tbody.innerHTML = '';
  items.forEach(it => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${it.rule_id}</td>
      <td>${it.action}</td>
      <td>${it.condition_type}</td>
      <td>${it.param_1 ?? ''}</td>
      <td>${it.param_2 ?? ''}</td>
      <td>
        <input type="number" class="form-control form-control-sm" value="${it.priority}" style="width:90px"
               onchange="updatePriority(${setId}, ${it.rule_id}, this.value)">
      </td>
      <td>
        <input type="checkbox" ${it.enabled ? 'checked' : ''}
               onchange="toggleEnabled(${setId}, ${it.rule_id}, this.checked)">
      </td>
      <td>
        <button class="btn btn-sm btn-outline-danger" onclick="detachRule(${setId}, ${it.rule_id})">Remove</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

// ==== додати правило в сет ====
await apiFetch(`/api/strategy_sets/${setId}/rules`, {
  method: 'POST',
  body: JSON.stringify({
    rule_id: createdRuleId,
    enabled: true,
    priority: 100
  })
});

async function attachRule() {
  const setId = document.getElementById('setSelect').value;
  const ruleId = parseInt(document.getElementById('ruleSelect').value);
  const prio = parseInt(document.getElementById('rulePriority').value || '100');
  const qs = getFiltersQS();

  const res = await apiFetch(`/api/strategy_sets/${setId}/rules${qs}`, {
    method: 'POST',
    body: JSON.stringify({ rule_id: ruleId, priority: prio, enabled: true })
  });
  if (!res.ok) { alert('Attach failed: ' + res.status); return; }
  await loadRulesForSelectedSet();
}

// ==== вмик/вимк правилo у сеті ====
async function toggleEnabled(setId, ruleId, enabled) {
  const qs = getFiltersQS();
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, {
    method: 'PATCH',
    body: JSON.stringify({ enabled })
  });
}

// ==== зміна пріоритету правила у сеті (debounce можна залишити зовнішнім) ====
async function updatePriority(setId, ruleId, priority) {
  const qs = getFiltersQS();
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, {
    method: 'PATCH',
    body: JSON.stringify({ priority: parseInt(priority || '0', 10) })
  });
}

// ==== відкріпити правило від сету ====
async function detachRule(setId, ruleId) {
  if (!confirm('Remove rule from set?')) return;
  const qs = getFiltersQS();
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, { method: 'DELETE' });
  await loadRulesForSelectedSet();
}

// ==== виклик при завантаженні сторінки ====
loadSetsIntoSelect();
window.refreshAttachRuleDropdown = refreshAttachRuleDropdown;
