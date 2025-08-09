<script>
/* ===== Strategy Sets CRUD ===== */
async function loadSets() {
  const res = await apiFetch('/api/strategy_sets');
  const sets = res.ok ? await res.json() : [];
  const tbody = document.getElementById('setsTable');
  tbody.innerHTML = '';
  sets.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${s.id}</td>
      <td>${escapeHtml(s.name)}</td>
      <td>${s.active ? '✅' : '❌'}</td>
      <td>${s.exchange ?? ''}</td>
      <td>${s.pair ?? ''}</td>
      <td class="d-flex gap-2">
        <button class="btn btn-sm btn-primary" onclick="openManageSetRules(${s.id})">Manage rules</button>
        <button class="btn btn-sm btn-warning" onclick="toggleSetActive(${s.id}, ${!s.active})">${s.active ? 'Deactivate' : 'Activate'}</button>
        <button class="btn btn-sm btn-danger" onclick="deleteSet(${s.id})">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

async function addSet() {
  const payload = {
    name: document.getElementById('set_name').value.trim(),
    description: document.getElementById('set_desc').value.trim() || null,
    exchange: document.getElementById('set_exchange').value.trim() || null,
    pair: document.getElementById('set_pair').value.trim() || null,
    active: document.getElementById('set_active').checked
  };
  const res = await apiFetch('/api/strategy_sets', { method:'POST', body: JSON.stringify(payload) });
  if (!res.ok) return alert('Error creating set: ' + res.status);
  await loadSets();
}

async function toggleSetActive(id, active) {
  const res = await apiFetch('/api/strategy_sets/' + id, { method:'PUT', body: JSON.stringify({ active }) });
  if (!res.ok) return alert('Error updating set');
  await loadSets();
}

async function deleteSet(id) {
  if (!confirm('Delete this set?')) return;
  const res = await apiFetch('/api/strategy_sets/' + id, { method:'DELETE' });
  if (!res.ok) return alert('Error deleting set');
  await loadSets();
}

/* ===== Manage set rules (dual list) ===== */
let currentSetId = null;
const manageSetRulesModal = () => new bootstrap.Modal(document.getElementById('manageSetRulesModal'));

async function openManageSetRules(setId) {
  currentSetId = setId;
  // 1) load all rules (reuse your existing GET /api/strategy_rules)
  const rulesRes = await apiFetch('/api/strategy_rules');
  const rules = rulesRes.ok ? await rulesRes.json() : [];

  // 2) load rules inside set
  const inRes = await apiFetch(`/api/strategy_set_rules/${setId}`);
  const inSet = inRes.ok ? await inRes.json() : [];
  const inSetMap = new Map(inSet.map(r => [r.rule_id, r]));

  // render lists
  const allBox = document.getElementById('allRulesList');
  const setBox = document.getElementById('setRulesList');
  allBox.innerHTML = '';
  setBox.innerHTML = '';

  rules.forEach(r => {
    if (!inSetMap.has(r.id)) {
      const btn = document.createElement('button');
      btn.className = 'list-group-item list-group-item-action';
      btn.textContent = `#${r.id} ${r.action} / ${r.condition_type} [${r.exchange}:${r.pair}]`;
      btn.onclick = () => addRuleToSet(setId, r.id);
      allBox.appendChild(btn);
    }
  });

  inSet.forEach(r => {
    setBox.appendChild(renderSetRuleRow(r));
  });

  manageSetRulesModal().show();
}

function renderSetRuleRow(r) {
  const div = document.createElement('div');
  div.className = 'list-group-item';
  div.innerHTML = `
    <div class="d-flex align-items-center justify-content-between gap-2">
      <div>#${r.rule_id}</div>
      <div class="form-check">
        <input class="form-check-input" type="checkbox" ${r.enabled ? 'checked':''}
               onchange="updateSetRule(${r.set_id}, ${r.rule_id}, {enabled:this.checked})">
        <label class="form-check-label">enabled</label>
      </div>
      <div class="input-group" style="width:150px">
        <span class="input-group-text">prio</span>
        <input type="number" class="form-control" value="${r.override_priority ?? ''}"
               onblur="updateSetRule(${r.set_id}, ${r.rule_id}, {override_priority: this.value ? parseInt(this.value) : null})">
      </div>
      <button class="btn btn-sm btn-outline-danger"
              onclick="removeRuleFromSet(${r.set_id}, ${r.rule_id})">Remove</button>
    </div>`;
  return div;
}

async function addRuleToSet(setId, ruleId) {
  const payload = { set_id: setId, rule_id: ruleId, enabled: true, override_priority: null };
  const res = await apiFetch('/api/strategy_set_rules', { method:'POST', body: JSON.stringify(payload) });
  if (!res.ok) return alert('Error adding rule');
  openManageSetRules(setId);
}

async function updateSetRule(setId, ruleId, patch) {
  const res = await apiFetch(`/api/strategy_set_rules/${setId}/${ruleId}`, { method:'PUT', body: JSON.stringify(patch) });
  if (!res.ok) alert('Error updating rule in set');
}

async function removeRuleFromSet(setId, ruleId) {
  const res = await apiFetch(`/api/strategy_set_rules/${setId}/${ruleId}`, { method:'DELETE' });
  if (!res.ok) return alert('Error removing rule');
  openManageSetRules(setId);
}

/* small util */
function escapeHtml(s){return (s??'').replace(/[&<>"']/g,m=>({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[m]))}
</script>
