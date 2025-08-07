// 📁 app/static/js/auth_utils.js

function checkAuth(redirect = true) {
  const token = localStorage.getItem("access_token");
  const expiresAt = localStorage.getItem("token_expires_at");

  if (!token || !expiresAt || Date.now() > parseInt(expiresAt)) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_expires_at");

    if (redirect) {
      window.location.href = "/login";
    }

    return false;
  }

  return true;
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_expires_at");
  window.location.href = "/login";
}
