// 📁 app/static/js/auth_utils.js

function checkAuth(redirect = true) {
  const token = localStorage.getItem("access_token");
  const expiresAt = localStorage.getItem("token_expires_at");

  console.log("🔍 checkAuth");
  console.log("access_token:", token);
  console.log("expiresAt:", expiresAt);
  console.log("now:", Date.now());

  if (!token || !expiresAt || Date.now() > parseInt(expiresAt)) {
    console.warn("❌ Token missing or expired");
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_expires_at");

    if (redirect) {
      console.warn("↪️ Redirecting to /login...");
      window.location.href = "/login";
    }

    return false;
  }

  console.log("✅ Token is valid");
  return true;
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("token_expires_at");
  window.location.href = "/login";
}

function isTokenValid() {
  const token = localStorage.getItem("access_token");
  const expiresAt = parseInt(localStorage.getItem("token_expires_at") || "0", 10);
  return token && Date.now() < expiresAt;
}

function checkAuth(redirect = true) {
  const valid = isTokenValid();
  if (!valid && redirect) {
    window.location.href = "/login";
  }
  return valid;
}