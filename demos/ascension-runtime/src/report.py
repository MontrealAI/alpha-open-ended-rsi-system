from __future__ import annotations

from pathlib import Path

from .utils import write_text


def run(out: Path, claim_boundary: str) -> None:
    scorecard_path = out / "ascension_runtime_scorecard.json"
    layers = []
    if scorecard_path.exists():
        import json

        layers = json.loads(scorecard_path.read_text(encoding="utf-8")).get("layers", [])

    layer_lines = "\n".join(
        [
            f"- **{row['layer']}** — {row['implementation_status']} / {row['runtime_mode']} / {row['result']} | "
            f"artifact: `{row['evidence_artifact']}` | next proof: {row['next_required_proof']}"
            for row in layers
        ]
    )
    md = f"""# Ascension Runtime Report (bounded local/devnet)

## Claim boundary
{claim_boundary}

## Organism map
Insight → Nova-Seeds → MARK → Sovereign → AGI Business → Marketplace → AGI Jobs → Agents → Validators/Council → Value Reservoir → Architect → Nodes → Archive/next loop.

## Layer status
{layer_lines}

## Key artifacts
- `out/insight_packet.json`
- `out/nova_seed_packet.json`
- `out/mark_selection_report.json`
- `out/sovereign_manifest.json`
- `out/agi_job_receipt.json`
- `out/validation_round.json`
- `out/council_ruling.json`
- `out/reservoir_ledger.json`
- `out/archive_lineage.json`
- `out/architect_recommendation.json`

## Not yet proven
- live mainnet settlement
- external-market validation
- audited final deployment safety
- unrestricted autonomy
"""
    html = f"""<html><body>
<h1>Ascension Runtime Report</h1>
<p>{claim_boundary}</p>
<p><strong>Mode:</strong> bounded local/devnet replay.</p>
<p><strong>Layer map:</strong> Insight → Nova-Seeds → MARK → Sovereign → AGI Business → Marketplace → AGI Jobs → Agents → Validators/Council → Value Reservoir → Architect → Nodes → Archive.</p>
<ul>
<li>Deterministic Insight-to-Archive loop completed.</li>
<li>Marketplace and reservoir remain local simulation layers.</li>
<li>No live external-market or mainnet claims.</li>
</ul>
</body></html>
"""
    write_text(out / "reports" / "ascension_runtime_report.md", md)
    write_text(out / "reports" / "ascension_runtime_report.html", html)
