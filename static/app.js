const $ = (selector) => document.querySelector(selector);

async function api(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[ch]));
}

function showError(message) {
  $("#toast").textContent = message;
  $("#toast").classList.add("show");
  setTimeout(() => $("#toast").classList.remove("show"), 5000);
}

async function loadHealth() {
  try {
    await api("/api/health");
    $("#status").textContent = "● CognoDB connected";
    $("#status").classList.add("online");
  } catch (error) {
    $("#status").textContent = "● Database unavailable";
    $("#status").classList.add("offline");
    showError("Could not connect to CognoDB. Check your environment variables.");
  }
}

async function loadStats() {
  try {
    const s = await api("/api/stats");
    $("#stats").innerHTML = [
      ["Candidates", s.candidates],
      ["Jobs", s.jobs],
      ["Skills", s.skills],
      ["Companies", s.companies]
    ].map(([label, value]) =>
      `<div class="stat"><strong>${value}</strong><span>${label}</span></div>`
    ).join("");
  } catch (error) {
    $("#stats").innerHTML = "";
  }
}

async function loadCandidates() {
  const candidates = await api("/api/candidates");
  $("#candidateSelect").innerHTML = candidates.map(c =>
    `<option value="${escapeHtml(c.id)}">${escapeHtml(c.name)} — ${escapeHtml(c.title)}</option>`
  ).join("");
  $("#candidateSelect").addEventListener("change", () => loadRecommendations());
  await loadRecommendations();
}

async function loadRecommendations() {
  const candidateId = $("#candidateSelect").value;
  const box = $("#recommendations");
  box.classList.add("loading");
  box.innerHTML = "Finding connected jobs…";

  try {
    const jobs = await api(`/api/recommendations/${encodeURIComponent(candidateId)}`);
    if (!jobs.length) {
      box.innerHTML = `<div class="empty">No connected jobs found for this candidate.</div>`;
      return;
    }

    box.innerHTML = jobs.map(job => `
      <article class="recommendation">
        <div class="match">${job.matchPercent}% match</div>
        <div>
          <h3>${escapeHtml(job.title)}</h3>
          <p>${escapeHtml(job.company)} · ${escapeHtml(job.domain)} · ${escapeHtml(job.location)}</p>
          <div class="chips">
            ${(job.matchedSkills || []).map(s => `<span>${escapeHtml(s)}</span>`).join("")}
          </div>
        </div>
      </article>
    `).join("");
  } catch (error) {
    box.innerHTML = `<div class="empty">Unable to load recommendations.</div>`;
    showError(error.message);
  } finally {
    box.classList.remove("loading");
  }
}

async function loadJobs() {
  const q = $("#search").value.trim();
  const box = $("#jobs");
  box.classList.add("loading");
  box.innerHTML = "Loading jobs…";

  try {
    const jobs = await api(`/api/jobs?q=${encodeURIComponent(q)}`);
    if (!jobs.length) {
      box.innerHTML = `<div class="empty">No jobs matched your search.</div>`;
      return;
    }

    box.innerHTML = jobs.map(job => `
      <article class="job-card">
        <div class="job-top">
          <span class="domain">${escapeHtml(job.domain)}</span>
          <span>${escapeHtml(job.location)}</span>
        </div>
        <h3>${escapeHtml(job.title)}</h3>
        <p class="company">${escapeHtml(job.company)}</p>
        <p>${escapeHtml(job.description)}</p>
      </article>
    `).join("");
  } catch (error) {
    box.innerHTML = `<div class="empty">Unable to load jobs.</div>`;
    showError(error.message);
  } finally {
    box.classList.remove("loading");
  }
}

let searchTimer;
$("#search").addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadJobs, 250);
});

(async function init() {
  await Promise.all([loadHealth(), loadStats()]);
  try {
    await loadCandidates();
    await loadJobs();
  } catch (error) {
    showError(error.message);
  }
})();
