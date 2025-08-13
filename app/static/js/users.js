function showTab(tab) {
  document.querySelectorAll(".tab-button").forEach(btn => btn.classList.remove("btn-primary"));
  document.querySelector(`button[onclick="showTab('${tab}')"]`).classList.add("btn-primary");
  document.getElementById('users-tab').style.display = tab === 'users' ? 'block' : 'none';
}

function openAddUserForm() {
  document.getElementById('user_id').value = '';
  document.getElementById('username').value = '';
  document.getElementById('email').value = '';
  document.getElementById('role').value = '';
  document.getElementById('password').value = '';
  document.getElementById('userModal').style.display = 'block';
}

function openEditUser(user) {
  document.getElementById('user_id').value = user.user_id;
  document.getElementById('username').value = user.username;
  document.getElementById('email').value = user.email;
  document.getElementById('role').value = user.role;
  document.getElementById('password').value = '';
  document.getElementById('userModal').style.display = 'block';
}

function closeUserModal() {
  document.getElementById('userModal').style.display = 'none';
}

async function saveUser() {
  const user_id = document.getElementById('user_id').value;
  const method = user_id ? 'PUT' : 'POST';
  const url = user_id ? `/api/config/users/${user_id}` : '/api/config/users';

  const data = {
    username: document.getElementById('username').value.trim(),
    email: document.getElementById('email').value.trim(),
    role: document.getElementById('role').value.trim()
  };

  const password = document.getElementById('password').value.trim();
  if (!user_id && password) data.password = password;
  if (user_id && password) data.password = password;

  const res = await apiFetch(url, {
    method,
    body: JSON.stringify(data)
  });

  if (res.ok) {
    closeUserModal();
    await loadUsers();
  } else {
    alert('❌ Failed to save user: ' + res.status);
  }
}

async function deleteUser(user_id) {
  if (!confirm("Are you sure you want to delete this user?")) return;

  const res = await apiFetch(`/api/config/users/${user_id}`, { method: 'DELETE' });
  if (res.ok) {
    await loadUsers();
  } else {
    alert('❌ Failed to delete user: ' + res.status);
  }
}

async function loadUsers() {
  const res = await apiFetch('/api/config/users');
  if (!res.ok) {
    alert('❌ Failed to load users: ' + res.status);
    return;
  }
  const users = await res.json();
  const tbody = document.getElementById('usersTable');
  tbody.innerHTML = '';

  users.forEach(user => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${user.user_id}</td>
      <td>${user.username}</td>
      <td>${user.email}</td>
      <td>${user.role}</td>
      <td>
        <button class="btn btn-sm btn-warning" onclick='openEditUser(${JSON.stringify(user)})'>Edit</button>
        <button class="btn btn-sm btn-danger" onclick='deleteUser(${user.user_id})'>Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  if (!checkAuth()) return;
  loadUsers();
  showTab('users');
});
