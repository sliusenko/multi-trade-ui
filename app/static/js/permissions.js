function showTab(tabId) {
  const tabs = ["users", "roles", "permissions", "role_permissions"];
  tabs.forEach(id => {
    const tab = document.getElementById(`${id}-tab`);
    if (tab) tab.style.display = (id === tabId) ? "block" : "none";
  });

  if (tabId === 'roles') loadRoles();
  if (tabId === 'permissions') loadPermissions();
  if (tabId === 'role_permissions') loadRolePermissions();
}

async function loadRoles() {
  const res = await fetch('/api/config/roles');
  const data = await res.json();
  const tbody = document.getElementById('rolesTable');
  tbody.innerHTML = '';
  data.forEach(r => {
    tbody.innerHTML += `<tr><td>${r.name}</td><td>${r.description || ''}</td></tr>`;
  });
}

async function loadPermissions() {
  const res = await fetch('/api/config/permissions');
  const data = await res.json();
  const tbody = document.getElementById('permissionsTable');
  tbody.innerHTML = '';
  data.forEach(p => {
    tbody.innerHTML += `<tr><td>${p.name}</td><td>${p.description || ''}</td></tr>`;
  });
}

async function loadRolePermissions() {
  const res = await fetch('/api/config/role_permissions');
  const data = await res.json();
  const tbody = document.getElementById('rolePermissionsTable');
  tbody.innerHTML = '';
  data.forEach(rp => {
    tbody.innerHTML += `<tr><td>${rp.role_name}</td><td>${rp.permission_name}</td></tr>`;
  });
}
