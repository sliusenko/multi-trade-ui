async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
}

async function loadRules() {
    const res = await apiFetch('/api/strategy_rules');
    if (!res.ok) {
        alert('❌ Error loading rules: ' + res.status);
        return;
    }

    const rules = await res.json();
    const tbody = document.getElementById('rulesTable');
    tbody.innerHTML = '';

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
            <td><button class="btn btn-danger btn-sm" onclick="deleteRule(${rule.id})">Delete</button></td>
        `;
        tbody.appendChild(tr);
    });
}

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

    const res = await apiFetch('/api/strategy_rules', {
        method: 'POST',
        body: JSON.stringify(data)
    });

    if (res.ok) {
        await loadRules();
        clearForm();
    } else {
        const errText = await res.text();
        alert(`❌ Error adding rule: ${res.status}\n${errText}`);
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
}

document.getElementById('addBtn').addEventListener('click', addRule);
window.addEventListener('DOMContentLoaded', loadRules);
