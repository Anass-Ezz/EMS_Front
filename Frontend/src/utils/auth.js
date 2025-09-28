// src/utils/auth.js
// Lightweight helper for storing and clearing the JWT (or session token)
// so that authentication persistence logic lives in one place only.

const TOKEN_KEY = 'token';

/**
 * Persist the token in either localStorage ("remember me") or sessionStorage.
 * @param {string} token         The auth token returned by the backend.
 * @param {boolean} rememberMe   If true, keep the token across browser restarts.
 */
export function storeToken(token, rememberMe = false) {
  if (!token) return;
  clearToken(); // ensure no duplicates between the two stores
  const storage = rememberMe ? window.localStorage : window.sessionStorage;
  storage.setItem(TOKEN_KEY, token);
}

/**
 * Retrieve the token from whichever Web Storage bucket currently holds it.
 * @returns {string|null}
 */
export function getStoredToken() {
  return (
    window.localStorage.getItem(TOKEN_KEY) ||
    window.sessionStorage.getItem(TOKEN_KEY)
  );
}

/**
 * Remove the token from both sessionStorage and localStorage.
 */
export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
}

/**
 * Common logout helper.
 * Clears the token and then either reloads the page or routes to the login view.
 * @param {import('vue-router').Router} [router] Optional router instance.
 */
export function logout(router) {
  clearToken();
  if (router) {
    router.push({ path: '/auth/login' });
  } else {
    // Fallback: hard reload to reset in-memory state if router isn't available
    window.location.reload();
  }
}

// Convenience default export so consumers can choose the style they like.
export default {
  storeToken,
  getStoredToken,
  clearToken,
  logout,
};
