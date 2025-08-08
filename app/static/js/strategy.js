async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
}

rules.forEach(rule => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>${rule.id}</td>
        <td>${rule.action}</td>
        <td>${rule.condition_type}</td>
        <td>${rule.param_1 ?? ''}</td>
        <td>${rule.param_2 ?? ''}</td>
        <td>${rule.enabled ? '✅' : '❌'}</td>
        <td>${rule.exchange}</td>
        <td>${rule.pair}</td>
        <td>${rule.priority ?? 0}</td>
        <td>
            <button class="btn btn-warning btn-sm" onclick='editRule(${JSON.stringify(rule).replace(/'/g, "\\'")})'>Edit</button>
            <button class="btn btn-danger btn-sm" onclick="deleteRule(${rule.id})">Delete</button>
        </td>
    `;
    tbody.appendChild(tr);
});

async function addRule() {
    const getInputValue = (id) => document.getElementById(id).value.trim();
    const param1Value = getInputValue('param_1');
    const param2Value = getInputValue('param_2');
    const priorityValue = getInputValue('priority');

    const data = {
        action: getInputValue('action'),
        condition_type: getInputValue('condition_type'),
        param_1: param1Value ? parseFloat(param1Value) : null,
        param_2: param2Value ? parseFloat(param2Value) : null,
        enabled: getInputValue('enabled') === 'true',
        exchange: getInputValue('exchange'),
        pair: getInputValue('pair'),
        priority: priorityValue ? parseInt(priorityValue) : 0
    };

    const ruleId = document.getElementById('addBtn').dataset.ruleId;
    const method = ruleId ? 'PUT' : 'POST';
    const url = ruleId ? `/api/strategy_rules/${ruleId}` : '/api/strategy_rules';

    const res = await apiFetch(url, {
        method,
        body: JSON.stringify(data)
    });

    if (res.ok) {
        await loadRules();
        clearForm();
        document.getElementById('addBtn').textContent = 'Add'; // поверни назад
        delete document.getElementById('addBtn').dataset.ruleId;
    } else {
        const errText = await res.text();
        alert(`❌ Error ${method === 'POST' ? 'adding' : 'updating'} rule: ${res.status}\n${errText}`);
    }
}

async function deleteRule(id) {
    const res = await apiFetch(`/api/strategy_rules/${id}`, { method: 'DELETE' });
    if (res.ok) {
        await loadRules();
    } else {
        alert('❌ Error deleting rule: ' + res.status);
    }
}

function clearForm() {
    document.querySelectorAll('.form-control').forEach(input => {
        if (input.tagName === 'SELECT') {
            input.selectedIndex = 0;
        } else {
            input.value = '';
        }
    });
    document.getElementById('addBtn').textContent = 'Add';
    delete document.getElementById('addBtn').dataset.ruleId;
}

function editRule(rule) {
    document.getElementById('action').value = rule.action;
    document.getElementById('condition_type').value = rule.condition_type;
    document.getElementById('param_1').value = rule.param_1 ?? '';
    document.getElementById('param_2').value = rule.param_2 ?? '';
    document.getElementById('enabled').value = rule.enabled ? 'true' : 'false';
    document.getElementById('exchange').value = rule.exchange;
    document.getElementById('pair').value = rule.pair;
    document.getElementById('priority').value = rule.priority ?? '';

    // збережи ID для оновлення
    document.getElementById('addBtn').dataset.ruleId = rule.id;
    document.getElementById('addBtn').textContent = 'Update';
}

document.getElementById('addBtn').addEventListener('click', addRule);
window.addEventListener('DOMContentLoaded', loadRules);
