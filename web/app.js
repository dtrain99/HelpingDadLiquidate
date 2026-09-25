// Increment 2: Google sign-in with a family allowlist and a session cookie.
const $ = (id) => document.getElementById(id);

function show(view) {
  for (const v of ["loading", "signed-out", "signed-in"]) $(v).hidden = v !== view;
}

function setMessage(text) {
  $("message").textContent = text;
}

async function api(path, options = {}) {
  const res = await fetch(path, { credentials: "same-origin", ...options });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

function showSignedIn(user) {
  $("user-name").textContent = user.name;
  $("user-email").textContent = user.email;
  show("signed-in");
}

function loadGoogleScript() {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error("Google sign-in didn't load"));
    document.head.appendChild(script);
  });
}

async function showSignedOut(clientId) {
  show("signed-out");
  await loadGoogleScript();
  google.accounts.id.initialize({ client_id: clientId, callback: onCredential });
  google.accounts.id.renderButton($("google-button"), {
    theme: "outline", size: "large", text: "signin_with", shape: "pill",
  });
}

async function onCredential(response) {
  setMessage("");
  const { ok, status, data } = await api("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential: response.credential }),
  });
  if (ok) return showSignedIn(data.user);
  if (status === 403) {
    setMessage(`${data.email} isn't on the family list. Ask whoever manages the Master Inventory to add it to the Family tab.`);
  } else if (status === 401) {
    setMessage("Google sign-in didn't go through. Try again.");
  } else {
    setMessage("Sign-in failed on the server. Try again in a minute.");
  }
}

async function signOut() {
  await api("/api/auth/logout", { method: "POST" });
  if (window.google) google.accounts.id.disableAutoSelect();
  location.reload();
}

async function start() {
  $("sign-out").addEventListener("click", signOut);
  try {
    const { ok, data } = await api("/api/auth/me");
    if (!ok) throw new Error("server error");
    if (data.signedIn) showSignedIn(data.user);
    else await showSignedOut(data.clientId);
  } catch {
    show("signed-out");
    setMessage("Can't reach the server right now. Try again in a minute.");
  }
  api("/api/health").then(({ ok, data }) => {
    if (ok) $("version").textContent = `Version ${data.version}`;
  });
}

start();
