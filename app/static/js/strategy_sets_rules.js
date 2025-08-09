async function loadSetsIntoSelect() {
  const res = await apiFetch('/api/strategy_sets'); // твій існуючий список сетів
  const sets = await res.json();
  const sel = document.getElementById('setSelect');
  sel.innerHTML = sets.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
  sel.onchange = loadRulesForSelectedSet;
  await loadRulesForSelectedSet();
}

async function loadRulesForSelectedSet() {
  const setId = document.getElementById('setSelect').value;
  if (!setId) return;
  // підтягуємо всі мої rules для селекту додавання
  const allRules = await (await apiFetch('/api/strategy_rules')).json();
  document.getElementById('ruleSelect').innerHTML =
    allRules.map(r => `<option value="${r.id}">[${r.id}] ${r.action} ${r.condition_type} ${r.param_1??''}/${r.param_2??''}</option>`).join('');

  const res = await apiFetch(`/api/strategy_sets/${setId}/rules`);
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
      <td><input type="number" class="form-control form-control-sm" value="${it.priority}" style="width:90px"
            onchange="updatePriority(${setId}, ${it.rule_id}, this.value)"></td>
      <td><input type="checkbox" ${it.enabled ? 'checked':''}
            onchange="toggleEnabled(${setId}, ${it.rule_id}, this.checked)"></td>
      <td>${it.note ?? ''}</td>
      <td>
        <button class="btn btn-sm btn-outline-danger" onclick="detachRule(${setId}, ${it.rule_id})">Remove</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

async function attachRule() {
  const setId = document.getElementById('setSelect').value;
  const ruleId = parseInt(document.getElementById('ruleSelect').value);
  const prio = parseInt(document.getElementById('rulePriority').value || '100');
  const res = await apiFetch(`/api/strategy_sets/${setId}/rules`, {
    method: 'POST',
    body: JSON.stringify({ rule_id: ruleId, priority: prio, enabled: true })
  });
  if (!res.ok) { alert('Attach failed: ' + res.status); return; }
  await loadRulesForSelectedSet();
}

async function toggleEnabled(setId, ruleId, enabled) {
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}`, {
    method: 'PATCH', body: JSON.stringify({ enabled })
  });
}

async function updatePriority(setId, ruleId, priority) {
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}`, {
    method: 'PATCH', body: JSON.stringify({ priority: parseInt(priority) })
  });
}

async function detachRule(setId, ruleId) {
  if (!confirm('Remove rule from set?')) return;
  await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}`, { method: 'DELETE' });
  await loadRulesForSelectedSet();
}

// виклик при завантаженні сторінки
loadSetsIntoSelect();
