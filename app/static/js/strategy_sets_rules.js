// ==== селект для "прикріпити правило до сету" ====
async function refreshAttachSelect(setId) {
  const qs = getFiltersQS();
  const all = await (await apiFetch(`/api/strategy_rules${qs}`)).json();
  const inSet = await (await apiFetch(`/api/strategy_sets/${setId}/rules${qs}`)).json();
  const inSetIds = new Set(inSet.map(x => x.rule_id));
  const sel = document.getElementById('ruleSelect');
  sel.innerHTML = all
    .filter(r => !inSetIds.has(r.id))  // ⬅️ виключаємо вже прив'язані
    .map(r => `<option value="${r.id}">[${r.id}] ${r.action} ${r.condition_type} ${r.param_1 ?? ''}/${r.param_2 ?? ''}</option>`)
    .join('');
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

// ==== завантаження правил для вибраного сету ====
async function loadRulesForSelectedSet() {
  const setId = document.getElementById('setSelect').value;
  if (!setId) return;

  const qs = getFiltersQS();

  // оновити селект правил
  await refreshAttachSelect(setId);

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
async function attachRule() {
  const setId = document.getElementById('setSelect').value;
  const ruleId = parseInt(document.getElementById('ruleSelect').value);
  const prio = parseInt(document.getElementById('rulePriority').value || '100');
  const qs = getFiltersQS();

  const res = await apiFetch(`/api/strategy_sets/${setId}/rules${qs}`, {
    method: 'POST',
    body: JSON.stringify({ rule_id: ruleId, priority: prio, enabled: true })
  });

  if (!res.ok) {
    const txt = await safeText(res);
    alert(`Attach failed: ${res.status}\n${txt}`);
    return;
  }

  await loadRulesForSelectedSet();  // ✅ оновити таблицю
}

// ==== вмик/вимк правила ====
async function toggleEnabled(setId, ruleId, enabled) {
  const qs = getFiltersQS();
  const res = await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, {
    method: 'PATCH',
    body: JSON.stringify({ enabled })
  });
  if (!res.ok) {
    const txt = await safeText(res);
    alert(`Enable toggle failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRulesForSelectedSet();  // ✅ обов’язково оновити таблицю
}

// ==== зміна пріоритету ====
async function updatePriority(setId, ruleId, priority) {
  const qs = getFiltersQS();
  const res = await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, {
    method: 'PATCH',
    body: JSON.stringify({ priority: parseInt(priority || '0', 10) })
  });
  if (!res.ok) {
    const txt = await safeText(res);
    alert(`Priority update failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRulesForSelectedSet();  // ✅
}

// ==== відʼєднати правило ====
async function detachRule(setId, ruleId) {
  if (!confirm('Remove rule from set?')) return;
  const qs = getFiltersQS();
  const res = await apiFetch(`/api/strategy_sets/${setId}/rules/${ruleId}${qs}`, { method: 'DELETE' });
  if (!res.ok) {
    const txt = await safeText(res);
    alert(`Detach failed: ${res.status}\n${txt}`);
    return;
  }
  await loadRulesForSelectedSet();  // ✅
}

// ==== старт ====
loadSetsIntoSelect();
window.refreshAttachRuleDropdown = () => {
  const setId = document.getElementById('setSelect')?.value;
  if (setId) refreshAttachSelect(setId);
};
