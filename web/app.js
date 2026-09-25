// Increment 1: confirm the front end can reach the backend through Firebase Hosting.
const statusEl = document.getElementById("status");

fetch("/api/health")
  .then((res) => {
    if (!res.ok) throw new Error(`Server responded ${res.status}`);
    return res.json();
  })
  .then((data) => {
    statusEl.textContent = `Server is running (version ${data.version}).`;
    statusEl.className = "status ok";
  })
  .catch((err) => {
    statusEl.textContent = `Can't reach the server: ${err.message}. Check the latest GitHub Actions run.`;
    statusEl.className = "status bad";
  });
