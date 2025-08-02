async function deleteRule(id) {
    if (!confirm("Are you sure?")) return;
    const resp = await fetch(`/api/strategy_rules/${id}`, { method: 'DELETE' });
    if (resp.ok) location.reload();
}

function editRule(id, action, condition, enabled) {
    document.getElementById('ruleId').value = id;
    document.getElementById('ruleAction').value = action;
    document.getElementById('ruleCondition').value = condition;
    document.getElementById('ruleEnabled').value = enabled;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

async function saveRule() {
    const id = document.getElementById('ruleId').value;
    const data = {
        action: document.getElementById('ruleAction').value,
        condition: document.getElementById('ruleCondition').value,
        enabled: document.getElementById('ruleEnabled').value === "1"
    };
    const resp = await fetch(`/api/strategy_rules/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    if (resp.ok) location.reload();
}
