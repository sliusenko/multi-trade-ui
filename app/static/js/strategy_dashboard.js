async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = options.headers || {};
    headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return fetch(url, { ...options, headers });
}

async function loadRules() {
    const res = await apiFetch('/api/strategy_rules');
    if (!res.ok) {
        alert('Error loading rules: ' + res.status);
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
            <td>${rule.priority}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteRule(${rule.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function addRule() {
    const data = {
        action: document.getElementById('action').value,
        condition_type: document.getElementById('condition_type').value,
        param_1: parseFloat(document.getElementById('param_1').value) || null,
        param_2: parseFloat(document.getElementById('param_2').value) || null,
        enabled: document.getElementById('enabled').value === 'true',
        exchange: document.getElementById('exchange').value,
        pair: document.getElementById('pair').value,
        priority: parseInt(document.getElementById('priority').value) || null
    };

    const res = await apiFetch('/api/strategy_rules', {
        method: 'POST',
        body: JSON.stringify(data)
    });

    if (res.ok) {
        await loadRules();
        clearForm();
    } else {
        alert('Error adding rule: ' + res.status);
    }
}

async function deleteRule(id) {
    const res = await apiFetch(`/api/strategy_rules/${id}`, { method: 'DELETE' });
    if (res.ok) {
        await loadRules();
    } else {
        alert('Error deleting rule: ' + res.status);
    }
}

function clearForm() {
    document.querySelectorAll('.form-control').forEach(input => input.value = '');
}

document.getElementById('addBtn').addEventListener('click', addRule);
window.addEventListener('DOMContentLoaded', loadRules);
