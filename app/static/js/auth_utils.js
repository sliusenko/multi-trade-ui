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

//    if (redirect) {
//      console.warn("↪️ Redirecting to /login...");
//      window.location.href = "/login";
//    }

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
