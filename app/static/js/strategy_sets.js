// ===== strategy_sets.js =====
console.log('[strategy_sets.js] loaded');

// Завжди перетворити у JSON (якщо це Response) або пропустити (якщо вже JSON)
async function asJson(x) {
  if (x && typeof x === "object" && "ok" in x && typeof x.json === "function") {
    if (!x.ok) {
      const text = await x.text().catch(() => "");
      throw new Error(`HTTP ${x.status} ${text}`);
    }
    return await x.json();
  }
  return x;
}

// Побудова ?query тільки коли треба; пропускає '', 'all', 'всі'
function buildQuerySafe(params) {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params || {})) {
    if (v == null) continue;
    const s = String(v).trim();
    if (!s || ["all","всі","усі"].includes(s.toLowerCase())) continue;
    q.append(k, s);
  }
  const qs = q.toString();
  return qs ? `?${qs}` : "";
}

// Нормалізація ENUM
function normSetType(v) {
  const t = (v ?? "").toLowerCase();
  return ["default","scalping","aggressive","combiner"].includes(t) ? t : "default";
}

function openEditSet(st) {
  window.__editSetId__ = st.id;
  document.getElementById('es_id').value = st.id;
  document.getElementById('es_name').value = st.name ?? '';
  document.getElementById('es_desc').value = st.description ?? '';
  document.getElementById('es_exchange').value = st.exchange ?? '';
  document.getElementById('es_pair').value = st.pair ?? '';
  const stSel = document.getElementById('es_set_type');
  if (stSel) stSel.value = normSetType(st.set_type);
  document.getElementById('es_active').checked = !!st.active;

  window.__gatherSetEditPayload__ = function() {
    return {
      name: document.getElementById('es_name').value.trim(),
      description: document.getElementById('es_desc').value.trim() || null,
      exchange: document.getElementById('es_exchange').value.trim().toLowerCase() || null,
      pair: document.getElementById('es_pair').value.trim().toUpperCase() || null,
      set_type: document.getElementById('es_set_type')?.value || null,
      active: document.getElementById('es_active').checked,
    };
  };

  const modal = new bootstrap.Modal(document.getElementById('editSetModal'));
  modal.show();
}

function sVal(id){ return document.getElementById(id)?.value?.trim() ?? ""; }

function sBool(id){ return !!document.getElementById(id)?.checked; }

function setPayloadFromForm() {
  return {
    name: sVal("set_name"),
    description: sVal("set_desc") || null,
    exchange: sVal("set_exchange").toLowerCase() || null,
    pair: sVal("set_pair").toUpperCase() || null,
    set_type: sVal("set_type") || null,
    active: sBool("set_active"),
  };
}

function renderSetRow(st) {
  const tr = document.createElement('tr');

  // 🔘 Чекбокс для активності
  const activeCheckbox = document.createElement('input');
  activeCheckbox.type = 'checkbox';
  activeCheckbox.checked = !!st.active;
  activeCheckbox.classList.add('form-check-input');
  activeCheckbox.addEventListener('change', async () => {
    await updateSet(st.id, {
      name: st.name ?? '',
      description: st.description ?? null,
      exchange: (st.exchange || '').toLowerCase() || null,
      pair: (st.pair || '').toUpperCase() || null,
      set_type: st.set_type ?? null,
      active: activeCheckbox.checked,
    });
  });

  // 📄 Інші клітинки
  const cells = [
    st.id,
    st.name ?? '',
    activeCheckbox,
    st.exchange ?? '',
    st.pair ?? '',
    st.set_type ?? ''
  ].map(c => {
    const td = document.createElement('td');
    if (c instanceof HTMLElement) td.appendChild(c);
    else td.textContent = c;
    return td;
  });

  // 🛠️ Дії
  const actionsTd = document.createElement('td');
  actionsTd.innerHTML = `
    <div class="btn-group btn-group-sm" role="group">
      <button class="btn btn-primary">Edit</button>
      <button class="btn btn-warning">${st.active ? 'Deactivate' : 'Activate'}</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  `;
  const [editBtn, toggleBtn, delBtn] = actionsTd.querySelectorAll('button');
  editBtn.addEventListener('click', () => openEditSet(st));
  toggleBtn.addEventListener('click', () => toggleSetActive(st));
  delBtn.addEventListener('click', () => deleteSet(st.id));

  // 🧱 Збірка
  cells.forEach(td => tr.appendChild(td));
  tr.appendChild(actionsTd);
  return tr;
}

async function addSet() {
  console.log('[addSet] called');
  const body = setPayloadFromForm();

  if (!body.name) { alert('Name — обовʼязкове поле'); return; }

  let res = await apiFetch('/api/strategy_sets', {
    method: 'POST',
    body: JSON.stringify(body),
  });
  console.log('[addSet] POST status=', res.status);

  if (!res.ok && res.status !== 201) {
    // fallback зі слешем на всяк випадок
    if ([405,307,308].includes(res.status)) {
      res = await apiFetch('/api/strategy_sets/', { method:'POST', body: JSON.stringify(body) });
      console.log('[addSet] POST / with slash status=', res.status);
    }
  }

  if (!res.ok && res.status !== 201) {
    alert(`Add Set failed: ${res.status}\n${await res.text()}`);
    return;
  }

  // очистити форму
  ["set_name","set_desc","set_exchange","set_pair","set_type"].forEach(id=>{ const el=document.getElementById(id); if(el) el.value=''; });
  const ac = document.getElementById('set_active'); if (ac) ac.checked = false;

  await loadSets();
}

// async function loadSets() {
//   console.log('[loadSets] url=', url);
//   const tbody = document.getElementById('setsTable');
//   if (tbody) tbody.innerHTML = `<tr><td colspan="7">Loading…</td></tr>`;

//   // беремо ТІЛЬКИ exchange/pair (user_id все одно приходить з токена на бекенді)
//   const { exchange, pair, user_id } = getActiveFilters();
//   const url = `/api/strategy_sets${buildQuerySafe({ exchange, pair, user_id })}`;

// //  const res = await apiFetch(url, { cache: "no-store" });
// //  if (!res.ok) {
// //    if (tbody) tbody.innerHTML = `<tr><td colspan="8">Error ${res.status}</td></tr>`;
// //    return;
// //  }
// //  const sets = await res.json();

//   let sets;
//   try {
//     const res = await apiFetch(url);
//     sets = await asJson(res);
//   } catch (e) {
//     console.error('[loadSets] failed:', e);
//     if (tbody) tbody.innerHTML = `<tr><td colspan="8">${String(e)}</td></tr>`;
//     return;
//   }
//   if (!Array.isArray(sets)) {
//     console.error('Unexpected payload for strategy_sets:', sets);
//     if (tbody) tbody.innerHTML = `<tr><td colspan="8">Bad payload</td></tr>`;
//     return;
//   }

//   console.log('[loadSets] got items=', sets.length, sets.slice(0,3));


//     if (!Array.isArray(sets)) {
//       console.error('Unexpected payload for strategy_sets:', sets);
//       return;
//     }
//   // 1) таблиця
//   if (tbody) {
//     tbody.innerHTML = '';
//     sets.forEach(s => tbody.appendChild(renderSetRow(s)));
//   }

//   // 2) селект зверху "Rules in Set"
//   const setSelect = document.getElementById('setSelect');
//   if (setSelect) {
//     const keep = setSelect.value;
//     setSelect.innerHTML = '';
//     sets.forEach(s => {
//       const o = document.createElement('option');
//       o.value = s.id;
//       // покажемо назву + (ex/pair), якщо є
//       const extra = [s.exchange, s.pair].filter(Boolean).join(' ');
//       o.textContent = extra ? `${s.name} (${extra})` : s.name;
//       setSelect.appendChild(o);
//     });
//     if (keep && [...setSelect.options].some(o => o.value === keep)) {
//       setSelect.value = keep;
//     }
//     // перевантажити правила для вибраного сету
//     if (typeof loadSetRules === 'function' && setSelect.value) {
//       loadSetRules(setSelect.value);
//     }
//   }
// }

async function updateSet(id, body) {
  console.log('[updateSet] called', id, body);
  let res = await apiFetch('/api/strategy_sets', {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  if (!res.ok && [405,307,308].includes(res.status)) {
    res = await apiFetch(`/api/strategy_sets/${id}/`, { method:'PUT', body: JSON.stringify(body) });
  }
  if (!res.ok) {
    alert(`Update Set failed: ${res.status}\n${await res.text()}`);
    return;
  }
  await loadSets();
}

async function toggleSetActive(st) {
  const body = {
    name: st.name ?? '',
    description: st.description ?? null,
    exchange: (st.exchange || '').toLowerCase() || null,
    pair: (st.pair || '').toUpperCase() || null,
    set_type: normSetType(st.set_type),
    active: !st.active,
  };
  let res = await apiFetch(`/api/strategy_sets/${st.id}`, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  if (!res.ok) alert(`Toggle failed: ${res.status}\n${await res.text()}`);
  else await loadSets();
}

async function deleteSet(id) {
  if (!confirm(`Delete set #${id}?`)) return;
  const res = await apiFetch(`/api/strategy_sets/${id}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 204) {
    alert(`Delete failed: ${res.status}\n${await res.text()}`);
    return;
  }
  await loadSets();
}


// ========= FIX loadSets(): спочатку формуємо url, потім логуємо =========
async function loadSets() {
  const tbody = document.getElementById('setsTable');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7">Loading…</td></tr>`;

  // беремо ТІЛЬКИ exchange/pair/user_id (якщо треба)
  const { exchange, pair, user_id } = getActiveFilters();
  const url = `/api/strategy_sets${buildQuerySafe({ exchange, pair, user_id })}`;
  console.log('[loadSets] url=', url);

  let sets;
  try {
    const res = await apiFetch(url, { cache: 'no-store' });
    sets = await asJson(res);
  } catch (e) {
    console.error('[loadSets] failed:', e);
    if (tbody) tbody.innerHTML = `<tr><td colspan="8">${String(e)}</td></tr>`;
    return;
  }
  if (!Array.isArray(sets)) {
    console.error('Unexpected payload for strategy_sets:', sets);
    if (tbody) tbody.innerHTML = `<tr><td colspan="8">Bad payload</td></tr>`;
    return;
  }

  console.log('[loadSets] got items=', sets.length, sets.slice(0,3));

  // 1) таблиця
  if (tbody) {
    tbody.innerHTML = '';
    sets.forEach(s => tbody.appendChild(renderSetRow(s)));
  }

  // 2) селект зверху "Rules in Set"
  const setSelect = document.getElementById('setSelect');
  if (setSelect) {
    const keep = setSelect.value;
    setSelect.innerHTML = '';
    sets.forEach(s => {
      const o = document.createElement('option');
      o.value = s.id;
      const extra = [s.exchange, s.pair].filter(Boolean).join(' ');
      o.textContent = extra ? `${s.name} (${extra})` : s.name;
      setSelect.appendChild(o);
    });
    if (keep && [...setSelect.options].some(o => o.value === keep)) {
      setSelect.value = keep;
    }
    if (typeof loadSetRules === 'function' && setSelect.value) {
      loadSetRules(setSelect.value);
    }
  }
}


// ========= Додаємо підписки на фільтри з дебаунсом =========

// Fallback, якщо десь не визначена
function getActiveFilters() {
  if (typeof window.getActiveFilters === 'function') return window.getActiveFilters();
  const userSel = document.getElementById('userSelect');
  const exSel   = document.getElementById('exchangeSelect');
  const pairSel = document.getElementById('pairSelect');
  return {
    user_id:  userSel?.value?.trim() || '',
    exchange: exSel?.value?.trim().toLowerCase() || '',
    pair:     pairSel?.value?.trim().toUpperCase() || '',
  };
}

function debounce(fn, ms=200) {
  let t; 
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

function attachFilterHandlersOnce() {
  if (window.__setsFiltersBound__) return;
  window.__setsFiltersBound__ = true;

  const onChange = debounce(async () => {
    // якщо інший код перезавантажує список пар — все одно просто перезавантажимо сети
    await loadSets();
  }, 200);

  document.getElementById('userSelect')   ?.addEventListener('change', onChange);
  document.getElementById('exchangeSelect')?.addEventListener('change', onChange);
  document.getElementById('pairSelect')    ?.addEventListener('change', onChange);
  console.log('[strategy_sets] filter handlers attached');
}

// Після завантаження DOM підвʼязуємося і робимо перше завантаження
function bootSetsModule() {
  attachFilterHandlersOnce();
  loadSets();
}

// if (document.readyState !== 'loading') bootSetsModule();
// else window.addEventListener('DOMContentLoaded', bootSetsModule);


// експорт у глобал (на випадок ручного виклику з консолі)
window.addSet = addSet;
window.updateSet = updateSet;
window.deleteSet = deleteSet;
window.loadSets = loadSets;

// автоматично підвантажити сети при завантаженні, якщо є фільтри
if (document.readyState !== 'loading') loadSets();
else window.addEventListener('DOMContentLoaded', loadSets);

