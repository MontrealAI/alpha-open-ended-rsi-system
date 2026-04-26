const API = 'http://localhost:8000';
let snapshot = {};
const SNAPSHOT_VERSION = 'v2.8.0-rc.7';

async function getJson(path, fallback) {
  try {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn(`Failed ${path}`, error);
    return fallback;
  }
}

function setMetric(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function initTabs() {
  document.querySelectorAll('.tabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tabs button').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(btn.dataset.tab)?.classList.add('active');
    });
  });
}

function bindExports() {
  document.getElementById('exportJson')?.addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nova-seeds-${SNAPSHOT_VERSION}-snapshot-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById('exportPng')?.addEventListener('click', () => {
    const canvas = document.getElementById('snapshotCanvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#0b1020';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#d2f8ff';
    ctx.font = '24px sans-serif';
    ctx.fillText(`Nova-Seeds ${SNAPSHOT_VERSION} Snapshot`, 30, 50);
    ctx.font = '16px monospace';
    const lines = JSON.stringify(snapshot, null, 2).split('\n').slice(0, 30);
    lines.forEach((line, i) => ctx.fillText(line, 30, 90 + i * 20));
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = url;
    a.download = `nova-seeds-${SNAPSHOT_VERSION}-snapshot-${Date.now()}.png`;
    a.click();
  });
}

async function load() {
  initTabs();
  bindExports();

  const summary = await getJson('/dashboard/summary', {});
  const proof = await getJson('/proof/summary', {});
  const reviewer = await getJson('/governance/reviewer-ledger', []);
  const council = await getJson('/governance/council-seats', []);
  const ascensionStatus = await getJson('/ascension/status', {});
  const ascensionScorecard = await getJson('/ascension/scorecard', { layers: [] });
  const ascensionJobs = await getJson('/ascension/jobs', {});
  const ascensionReservoir = await getJson('/ascension/reservoir', {});
  const ascensionArchitect = await getJson('/ascension/architect', {});

  for (const [k, v] of Object.entries(summary)) setMetric(k, v);
  for (const [k, v] of Object.entries(proof)) setMetric(k, v);

  const proofAlerts = (proof.open_challenges || 0) + (proof.chain_event_count === 0 ? 1 : 0);
  setMetric('proof_alerts', proofAlerts);

  setMetric('ascension_available', ascensionStatus.available ? 'yes' : 'no');
  setMetric('ascension_layer_count', ascensionStatus.layer_count || 0);
  setMetric('ascension_event_count', ascensionStatus.event_count || 0);

  document.getElementById('reviewerLedger').textContent = JSON.stringify(reviewer, null, 2);
  document.getElementById('councilSeats').textContent = JSON.stringify(council, null, 2);
  document.getElementById('ascensionScorecard').textContent = JSON.stringify(ascensionScorecard, null, 2);
  document.getElementById('ascensionJobs').textContent = JSON.stringify(ascensionJobs, null, 2);
  document.getElementById('ascensionReservoir').textContent = JSON.stringify(ascensionReservoir, null, 2);
  document.getElementById('ascensionArchitect').textContent = JSON.stringify(ascensionArchitect, null, 2);

  snapshot = {
    version: SNAPSHOT_VERSION,
    proofBoundary: 'Synthetic wedge proof + bounded accelerating-loop mechanism only; broader cybersecurity sovereign and unrestricted autonomy remain unproven in this RC.',
    capturedAt: new Date().toISOString(),
    summary,
    proof,
    reviewer,
    council,
    ascensionStatus,
    ascensionScorecard,
    ascensionJobs,
    ascensionReservoir,
    ascensionArchitect,
  };
}

load().catch(console.error);
