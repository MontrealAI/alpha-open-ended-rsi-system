from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from .assay import run_mandate_1_competition, run_mandate_2
from .business import emit_parent_business_artifact, load_parent_business
from .doctrine import build_doctrine_artifacts
from .fixtures import read_contracts
from .package_builder import build_capability_packages
from .scorecard import build_scorecard
from .seeds import emit_seed_packets, load_seed_packets
from .sovereign import emit_sovereign_or_ruling
from .utils import demo_timestamp, reset_dir, write_json, write_text

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo_output"


def _pct(v: float) -> str:
    return f"{v*100:.1f}%"


def _seed_summary_row(seed: dict) -> str:
    return f"| {seed['id']} | {seed['mutation_thesis']} | {seed['operator_workflow_delta']} |"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _determinism_snapshot() -> dict[str, str]:
    tracked = [
        OUT / "mandate_1" / "assay_summary.json",
        OUT / "capability_package" / "GovernanceValidationPack-v1.json",
        OUT / "capability_package" / "ProtocolCybersecurityPack-v1.json",
        OUT / "scorecard" / "adjacent_mandate_scorecard.json",
        OUT / "proof_docket" / "proof_docket.json",
        OUT / "sovereign" / "ProtocolCybersecuritySovereign-v1.synthetic.json",
        OUT / "doctrine" / "doctrine_stack.json",
    ]
    return {str(path.relative_to(OUT)): _file_sha256(path) for path in tracked}


def run_demo(assert_mode: bool = False):
    reset_dir(OUT)

    parent = load_parent_business(ROOT / "parent_business" / "protocol_cybersecurity_studio.json")
    seeds = load_seed_packets(ROOT / "nova_seeds")
    emit_parent_business_artifact(parent, OUT / "parent_business")
    emit_seed_packets(seeds, OUT / "nova_seeds")

    doctrine = build_doctrine_artifacts(ROOT, OUT / "doctrine")

    mandate_1_contracts = read_contracts(ROOT / "contracts" / "mandate_1")
    mandate_1_summary = run_mandate_1_competition(
        seeds,
        mandate_1_contracts,
        ROOT / "ground_truth" / "mandate_1.json",
        OUT / "mandate_1",
    )
    winner_id = mandate_1_summary["winner"]
    winner_result = next(r for r in mandate_1_summary["results"] if r["seed"] == winner_id)

    governance_pack, protocol_pack = build_capability_packages(winner_result, OUT / "capability_package")

    mandate_2_contracts = read_contracts(ROOT / "contracts" / "mandate_2")
    winner_seed = next(seed for seed in seeds if seed["id"] == winner_id)
    control = run_mandate_2(
        winner_seed,
        mandate_2_contracts,
        ROOT / "ground_truth" / "mandate_2.json",
        False,
        OUT / "mandate_2_control",
    )
    treatment = run_mandate_2(
        winner_seed,
        mandate_2_contracts,
        ROOT / "ground_truth" / "mandate_2.json",
        True,
        OUT / "mandate_2_treatment",
    )

    scorecard = build_scorecard(control["metrics"], treatment["metrics"], OUT / "scorecard")
    sovereign_or_ruling = emit_sovereign_or_ruling(scorecard, protocol_pack, OUT / "sovereign")
    governance_ruling = {
        "id": "governance_ruling.json",
        "status": "pass" if scorecard["passes"]["adjacent_mandate_proof"] else "fail_closed",
        "decision": "emit_protocol_cybersecurity_sovereign"
        if scorecard["passes"]["adjacent_mandate_proof"]
        else "block_protocol_cybersecurity_sovereign",
        "justification": "Threshold scorecard evaluated under deterministic control-vs-treatment adjacent mandate assay.",
        "linked_artifact": sovereign_or_ruling["id"],
        "timestamp": sovereign_or_ruling["timestamp"],
        "disclaimer": "Synthetic governance ruling for local replay; not a real-world governance decision.",
    }
    write_json(OUT / "proof_docket" / governance_ruling["id"], governance_ruling)

    now = demo_timestamp()
    release_gate_packet = {
        "id": "release_gate_packet",
        "timestamp": now,
        "status": "pass" if scorecard["passes"]["adjacent_mandate_proof"] else "fail",
        "requirements": protocol_pack["portable_components"]["release_gate_packet"]["required"],
    }
    write_json(OUT / "scorecard" / "release_gate_packet.json", release_gate_packet)
    write_json(OUT / "proof_docket" / "07_settlement_release_packet.json", release_gate_packet)

    chronicle = {
        "id": "chronicle_protocol_correctness_first_stepping_stone",
        "sector": "protocol_and_smart_contract_correctness",
        "parent_business": parent["title"],
        "winning_seed": winner_id,
        "frozen_sub_pack": governance_pack["id"],
        "sector_stepping_stone": protocol_pack["id"],
        "adjacent_proof_passed": scorecard["passes"]["adjacent_mandate_proof"],
        "timestamp": now,
    }
    write_json(OUT / "proof_docket" / "chronicle_entry.json", chronicle)

    proof_docket = {
        "claim": "Synthetic flagship claim: frozen protocol cybersecurity capability improved adjacent mandate performance under control-vs-treatment assay.",
        "constitutional_frame": {
            "order": ["identity", "proof", "settlement", "governance"],
            "invariant": [
                "no value without evidence",
                "no autonomy without authority",
                "no settlement without validation",
            ],
        },
        "parent_business": parent,
        "doctrine": doctrine,
        "nova_seed_lineup": seeds,
        "mandate_1_summary": mandate_1_summary,
        "mandate_2_control_summary": control,
        "mandate_2_treatment_summary": treatment,
        "scorecard": scorecard,
        "settlement_release_packet": release_gate_packet,
        "chronicle_entry": chronicle,
        "governance_ruling": governance_ruling,
        "sovereign_or_fail_closed_artifact": sovereign_or_ruling,
        "synthetic_disclaimer": "This docket is synthetic, local, replayable, and falsifiable. It is not a real-world proof pack.",
    }
    write_json(OUT / "proof_docket" / "proof_docket.json", proof_docket)

    write_text(
        OUT / "proof_docket" / "00_claim.md",
        "# Claim\n\nSynthetic flagship claim: a frozen protocol cybersecurity capability improved adjacent mandate performance under deterministic control-vs-treatment scoring.\n",
    )
    write_text(
        OUT / "proof_docket" / "01_constitutional_frame.md",
        "# Constitutional Frame\n\n- Order: identity → proof → settlement → governance\n- Invariant: no value without evidence; no autonomy without authority; no settlement without validation\n",
    )
    write_text(
        OUT / "proof_docket" / "02_parent_business.md",
        f"# Parent Business\n\n- Name: {parent['title']}\n- Scope: {parent['scope_type']}\n- Review posture: {parent['review_posture']}\n",
    )
    seed_lines = "\n".join([f"- {seed['title']} (`{seed['id']}`): {seed['mutation_thesis']}" for seed in seeds])
    write_text(OUT / "proof_docket" / "02b_nova_seed_lineup.md", f"# Nova-Seed Lineup\n\n{seed_lines}\n")
    write_text(
        OUT / "proof_docket" / "03_mandate_1_summary.md",
        f"# Mandate 1 Summary\n\n- Mandate: {mandate_1_summary['mandate']}\n- Winner seed: {winner_id}\n- Selection basis: {mandate_1_summary['selection_basis']}\n",
    )
    write_text(
        OUT / "proof_docket" / "04_mandate_2_control_summary.md",
        f"# Mandate 2 Control Summary\n\n- Lane: control\n- AOY: {control['metrics']['aoy']}\n- Time to first accepted: {control['metrics']['time_to_first_accepted_output']}\n- Repair/Rework: {control['metrics']['repair_rework']}\n- Evidence completeness: {control['metrics']['evidence_completeness']}\n",
    )
    write_text(
        OUT / "proof_docket" / "05_mandate_2_treatment_summary.md",
        f"# Mandate 2 Treatment Summary\n\n- Lane: treatment\n- AOY: {treatment['metrics']['aoy']}\n- Time to first accepted: {treatment['metrics']['time_to_first_accepted_output']}\n- Repair/Rework: {treatment['metrics']['repair_rework']}\n- Evidence completeness: {treatment['metrics']['evidence_completeness']}\n- Package dependence rate: {treatment['metrics']['package_dependence_rate']}\n",
    )
    write_text(
        OUT / "proof_docket" / "06_scorecard.md",
        f"# Adjacent-Mandate Scorecard\n\n- AOY uplift: {_pct(scorecard['comparison']['aoy_uplift'])}\n- Speed uplift: {_pct(scorecard['comparison']['speed_uplift'])}\n- Repair/Rework reduction: {_pct(scorecard['comparison']['repair_rework_reduction'])}\n- Evidence completeness uplift: {_pct(scorecard['comparison']['evidence_completeness_uplift'])}\n- Safety regression: {'YES' if scorecard['comparison']['safety_regression'] else 'NO'}\n- Package dependence rate: {_pct(scorecard['comparison']['package_dependence_rate'])}\n- Ruling: {'PASS' if scorecard['passes']['adjacent_mandate_proof'] else 'FAIL'}\n",
    )
    write_text(
        OUT / "proof_docket" / "07_settlement_release_packet.md",
        f"# Settlement / Release Packet\n\n- Release-gate status: {release_gate_packet['status']}\n- Linked packet: scorecard/release_gate_packet.json\n",
    )
    write_text(
        OUT / "proof_docket" / "08_governance_ruling.md",
        f"# Governance Ruling\n\n- Decision: {governance_ruling['decision']}\n- Status: {governance_ruling['status']}\n- Linked artifact: {governance_ruling['linked_artifact']}\n",
    )

    md = f"""# Protocol Smart-Contract Correctness Flagship Demo Report

**Synthetic disclaimer:** This report is synthetic, local, replayable, and falsifiable. It is not a real-world proof.

## Sector and parent business
- Sector: protocol and smart-contract correctness
- Parent business: {parent['title']}
- Why first wedge: objective, replayable, fast to review, reusable primitives, commercially legible.

## Full-stack economic organism framing
- Canonical docs: `docs/DOCTRINE_STACK.md`, `docs/THERMODYNAMIC_MODEL.md`, `docs/NATION_STATE_DOCTRINE.md`
- First narrow organ: 🌱💫 α-AGI Protocol Cybersecurity Sovereign 🔐
- Future-facing seed: 👑 α-AGI Cybersecurity Sovereign 🔱✨
- Honesty boundary: the broader cybersecurity sovereign remains future-facing and not yet proven.

## First mandate and assay setup
- Mandate 1 focus: governance/dispute correctness
- Contract fixtures: `CouncilGovernanceV25Fixture.sol`, `ChallengePolicyModuleV25Fixture.sol`
- Common harsh assay metrics: accepted usefulness points, time-to-first-accepted output, repair/rework, evidence completeness, unsupported claim rate, packageable artifact quality.

## Five sibling Nova-Seeds
| Seed | Mutation thesis | Operator workflow delta |
|---|---|---|
"""
    for seed in seeds:
        md += _seed_summary_row(seed) + "\n"

    md += """
## Nova-Seed assay (Mandate 1)
Winner: **{winner}**

| Seed | AUP | First accepted step | Rework | Evidence | Unsupported claim rate | Package quality |
|---|---:|---:|---:|---:|---:|---:|
""".format(winner=winner_id)
    for result in mandate_1_summary["results"]:
        m = result["metrics"]
        md += f"| {result['seed']} | {m['accepted_usefulness_points']} | {m['time_to_first_accepted_output']} | {m['repair_rework']:.3f} | {m['evidence_completeness']:.3f} | {m['unsupported_claim_rate']:.3f} | {m['packageable_artifact_quality']:.3f} |\n"

    cmp = scorecard["comparison"]
    th = scorecard["thresholds"]
    md_sovereign_interpretation = (
        "- PASS interpretation: this emits the first compounding correctness sovereign in synthetic demo form, i.e., the 🌱💫 α-AGI Protocol Cybersecurity Sovereign 🔐.\n"
        "- PASS interpretation: this is the seed of a future broader 👑 α-AGI Cybersecurity Sovereign 🔱✨.\n"
        "- PASS interpretation: this does **not** claim the broader cybersecurity sovereign already exists."
        if scorecard["passes"]["adjacent_mandate_proof"]
        else "- FAIL-CLOSED interpretation: sovereign emission is blocked; no sovereign seed claim is made for this run."
    )
    html_sovereign_interpretation = (
        "PASS indicates the first narrow production organ and compounding correctness sovereign form in synthetic context; it is not proof that the broader cybersecurity sovereign already exists."
        if scorecard["passes"]["adjacent_mandate_proof"]
        else "FAIL-CLOSED blocks sovereign emission for this run; no sovereign-seed claim is made."
    )
    md += f"""

## Frozen capability packages
- Sub-pack: `GovernanceValidationPack-v1`
- Sector stepping stone: `ProtocolCybersecurityPack-v1` (legacy alias: `ProtocolAssurancePack-v1`)
- Distinction: sub-pack is first frozen reusable governance capability; stepping stone is promoted sector-level portability surface.

## Adjacent mandate (Mandate 2) control vs treatment
- Mandate 2 focus: threshold / attestation correctness
- Contract fixtures: `ThresholdNetworkAdapterV25Fixture.sol`, `SignedAttestationVerifierV25Fixture.sol`
- Control AOY: {control['metrics']['aoy']}
- Treatment AOY: {treatment['metrics']['aoy']}
- AOY uplift: {_pct(cmp['aoy_uplift'])}
- Speed uplift: {_pct(cmp['speed_uplift'])}
- Repair/rework reduction: {_pct(cmp['repair_rework_reduction'])}
- Evidence completeness uplift: {_pct(cmp['evidence_completeness_uplift'])}
- Safety regression: {'YES' if cmp['safety_regression'] else 'NO'}
- Package dependence rate: {_pct(cmp['package_dependence_rate'])}

## Threshold ruling (strict)
- AOY uplift ≥ {_pct(th['aoy_uplift'])}
- Speed uplift ≥ {_pct(th['speed_uplift'])}
- Repair/rework reduction ≥ {_pct(th['repair_rework_reduction'])}
- Evidence completeness uplift ≥ {_pct(th['evidence_completeness_uplift'])}
- No safety regression
- Package dependence rate ≥ {_pct(th['package_dependence_rate'])}
- Adjacent-mandate proof: **{'PASS' if scorecard['passes']['adjacent_mandate_proof'] else 'FAIL'}**

## Sovereign emission
- Artifact: `{sovereign_or_ruling['id']}`
- Status: `{sovereign_or_ruling['status']}`
{md_sovereign_interpretation}
- It does **not** claim cybersecurity is solved once and for all.
"""
    write_text(OUT / "reports" / "report.md", md)

    html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Protocol Correctness Flagship Demo</title>
<style>
body{{font-family:Inter,Arial,sans-serif;background:#091224;color:#dbe4f3;margin:0;padding:28px;line-height:1.55}}
.wrap{{max-width:1180px;margin:0 auto}}
.card{{background:#101a2f;border:1px solid #2f405d;border-radius:14px;padding:18px;margin-bottom:16px;box-shadow:0 2px 16px rgba(2,6,23,.25)}}
h1,h2,h3{{margin:0 0 12px 0}} small{{color:#9fb0cb}}
table{{width:100%;border-collapse:collapse}}th,td{{border-bottom:1px solid #2f405d;padding:8px;text-align:left;vertical-align:top}}
.pass{{color:#34d399;font-weight:700}}.fail{{color:#f87171;font-weight:700}}
.kpi{{font-size:1.1rem;font-weight:700}}
.badge{{display:inline-block;padding:4px 10px;border:1px solid #4d6284;border-radius:999px;background:#182642;margin-right:8px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.tri{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
pre{{white-space:pre-wrap;background:#0a162c;padding:10px;border-radius:10px;border:1px solid #2f405d;overflow:auto}}
ul{{margin:0;padding-left:18px}}
.subtle{{color:#9fb0cb}}
.kv{{display:grid;grid-template-columns:190px 1fr;gap:8px 12px}}
.kv div{{padding:5px 0;border-bottom:1px dashed #2b3b58}}
.kv div:nth-child(odd){{font-weight:600;color:#b8c8e0}}
@media (max-width: 980px){{.grid,.tri{{grid-template-columns:1fr}} .kv{{grid-template-columns:1fr}}}}
</style></head><body><div class='wrap'>
<div class='card'>
<span class='badge'>Flagship synthetic wedge demo</span>
<span class='badge'>v2.8.0-rc.1 candidate surface</span>
<h1>Protocol + Smart-Contract Correctness</h1>
<small>Front-door wedge explanation: sector → parent business → seeds → assay → frozen package → adjacent scorecard → sovereign gate.</small>
<p><strong>Status:</strong> synthetic, local, replayable, falsifiable; not a real-world proof pack and not an audited final deployment.</p>
</div>
<div class='card tri'>
<div>
<h3>Flagship synthetic wedge</h3>
<p class='subtle'>Current page and report bundle.</p>
<code>demos/protocol_smart_contract_correctness_demo/</code>
</div>
<div>
<h3>Compact synthetic adjacent proof</h3>
<p class='subtle'>Minimal replay of adjacent mandate control vs treatment.</p>
<code>demos/adjacent_mandate_reuse_proof_demo/</code>
</div>
<div>
<h3>Real-world experiment pack</h3>
<p class='subtle'>Templates, runbook, and scorecard process for controlled execution.</p>
<code>demos/adjacent_mandate_reuse_proof_real_v1/</code>
</div>
</div>
<div class='card'>
<h2>Doctrine stack in one view</h2>
<p><strong>First narrow organ:</strong> 🌱💫 α-AGI Protocol Cybersecurity Sovereign 🔐.</p>
<p><strong>Future seed:</strong> 👑 α-AGI Cybersecurity Sovereign 🔱✨.</p>
<p><strong>Not claimed:</strong> full cybersecurity sovereign already exists; cybersecurity is solved once and for all; thermodynamic framing is literal physical law.</p>
<p><strong>Organism loop:</strong> Insight → Nova-Seeds → MARK → AGI Jobs (identity/proof/settlement/governance) → Archive (reusable capability and entropy pressure reduction).</p>
<pre>X(t)=\\big(K,C,D,A,Q,R,\\Sigma\\big)\n\\mathcal G[X]=\\mathcal H[X]-T_{{eff}}\\mathcal S_{{org}}[X]\n\\Lambda=\\frac{{\\rho_{{reuse}}\\,\\rho_{{validation}}\\,\\rho_{{selection}}}}{{\\Pi}}</pre>
</div>
<div class='card'>
<h2>Why this sector is first</h2>
<ul>
<li>Objective and replayable failure classes</li>
<li>Fast operator review cycles</li>
<li>Reusable primitives (invariants, query bundles, release gates)</li>
<li>Commercially legible fixed-scope mandate model</li>
</ul>
<p><strong>Parent business:</strong> {parent['title']}</p>
<p><strong>Constitutional order:</strong> identity → proof → settlement → governance</p>
<p><strong>Invariant:</strong> no value without evidence; no autonomy without authority; no settlement without validation.</p>
</div>
<div class='card'>
<h2>Five sibling Nova-Seeds</h2>
<table><tr><th>Seed</th><th>Mutation thesis</th><th>Operator workflow delta</th></tr>
"""
    for seed in seeds:
        html += f"<tr><td>{seed['id']}</td><td>{seed['mutation_thesis']}</td><td>{seed['operator_workflow_delta']}</td></tr>"

    html += f"""
</table>
</div>
<div class='card'>
<h2>Mandate 1 (governance/dispute correctness) assay winner: {winner_id}</h2>
<p>Fixtures: <code>CouncilGovernanceV25Fixture.sol</code>, <code>ChallengePolicyModuleV25Fixture.sol</code></p>
<table><tr><th>Seed</th><th>AUP</th><th>First accepted</th><th>Rework</th><th>Evidence</th><th>Unsupported rate</th><th>Package quality</th></tr>
"""
    for result in mandate_1_summary["results"]:
        m = result["metrics"]
        html += f"<tr><td>{result['seed']}</td><td>{m['accepted_usefulness_points']}</td><td>{m['time_to_first_accepted_output']}</td><td>{m['repair_rework']}</td><td>{m['evidence_completeness']}</td><td>{m['unsupported_claim_rate']}</td><td>{m['packageable_artifact_quality']}</td></tr>"
    html += f"""
</table>
<p>Frozen sub-pack: <code>GovernanceValidationPack-v1</code> → promoted stepping stone: <code>ProtocolCybersecurityPack-v1</code> (legacy alias: <code>ProtocolAssurancePack-v1</code>).</p>
</div>
<div class='card'>
<h2>Winner selection key (deterministic)</h2>
<div class='kv'>
<div>1</div><div>Accepted usefulness points (higher)</div>
<div>2</div><div>Time to first accepted output (lower)</div>
<div>3</div><div>Repair/rework ratio (lower)</div>
<div>4</div><div>Evidence completeness (higher)</div>
<div>5</div><div>Unsupported claim rate (lower)</div>
<div>6</div><div>Severity inflation count (lower)</div>
<div>7</div><div>Packageable artifact quality (higher)</div>
</div>
</div>
<div class='card grid'>
<div>
<h2>Mandate 2 Control</h2>
<p>AOY: <span class='kpi'>{control['metrics']['aoy']}</span></p>
<p>Time to first accepted: {control['metrics']['time_to_first_accepted_output']}</p>
<p>Repair/rework: {control['metrics']['repair_rework']}</p>
<p>Evidence completeness: {control['metrics']['evidence_completeness']}</p>
</div>
<div>
<h2>Mandate 2 Treatment</h2>
<p>AOY: <span class='kpi'>{treatment['metrics']['aoy']}</span></p>
<p>Time to first accepted: {treatment['metrics']['time_to_first_accepted_output']}</p>
<p>Repair/rework: {treatment['metrics']['repair_rework']}</p>
<p>Evidence completeness: {treatment['metrics']['evidence_completeness']}</p>
<p>Package dependence: {treatment['metrics']['package_dependence_rate']}</p>
</div>
</div>
<div class='card'>
<h2>Adjacent-mandate threshold scorecard (strict)</h2>
<ul>
<li>AOY uplift: {_pct(cmp['aoy_uplift'])} (threshold ≥ {_pct(th['aoy_uplift'])})</li>
<li>Speed uplift: {_pct(cmp['speed_uplift'])} (threshold ≥ {_pct(th['speed_uplift'])})</li>
<li>Repair/rework reduction: {_pct(cmp['repair_rework_reduction'])} (threshold ≥ {_pct(th['repair_rework_reduction'])})</li>
<li>Evidence completeness uplift: {_pct(cmp['evidence_completeness_uplift'])} (threshold ≥ {_pct(th['evidence_completeness_uplift'])})</li>
<li>Safety regression: {'YES' if cmp['safety_regression'] else 'NO'} (must be NO)</li>
<li>Package dependence rate: {_pct(cmp['package_dependence_rate'])} (threshold ≥ {_pct(th['package_dependence_rate'])})</li>
</ul>
<p>Ruling: <span class='{'pass' if scorecard['passes']['adjacent_mandate_proof'] else 'fail'}'>{'PASS' if scorecard['passes']['adjacent_mandate_proof'] else 'FAIL'}</span></p>
<p>Sovereign artifact/ruling emitted: <code>{sovereign_or_ruling['id']}</code></p><p><strong>Interpretation:</strong> {html_sovereign_interpretation}</p>
</div>
<div class='card'>
<h2>Operator artifact map + next actions</h2>
<ul>
<li><code>demo_output/scorecard/adjacent_mandate_scorecard.json</code></li>
<li><code>demo_output/scorecard/release_gate_packet.json</code></li>
<li><code>demo_output/proof_docket/proof_docket.json</code></li>
<li><code>demo_output/proof_docket/governance_ruling.json</code></li>
<li><code>demo_output/sovereign/{sovereign_or_ruling['id']}</code></li>
</ul><p><strong>Next:</strong> run real-world controlled experiment pack for external validity evidence.</p>
</div>
</div></body></html>"""
    write_text(OUT / "reports" / "report.html", html)

    if assert_mode:
        assert winner_id == "invariant_library", "Expected deterministic winner invariant_library"
        assert (OUT / "capability_package" / "GovernanceValidationPack-v1.json").exists()
        assert (OUT / "capability_package" / "ProtocolCybersecurityPack-v1.json").exists()
        assert (OUT / "scorecard" / "adjacent_mandate_scorecard.json").exists()
        assert (OUT / "proof_docket" / "governance_ruling.json").exists()
        assert (OUT / "proof_docket" / "07_settlement_release_packet.json").exists()
        assert (OUT / "doctrine" / "doctrine_stack.json").exists()

    return {
        "winner": winner_id,
        "adjacent_mandate_proof": scorecard["passes"]["adjacent_mandate_proof"],
        "sovereign_artifact": sovereign_or_ruling["id"],
    }


def run_demo_cli():
    parser = argparse.ArgumentParser(description="Run protocol correctness flagship demo")
    parser.add_argument("--assert", action="store_true", dest="assert_mode", help="Run with deterministic assertions")
    args = parser.parse_args()
    result = run_demo(assert_mode=args.assert_mode)
    if args.assert_mode:
        snapshot_1 = _determinism_snapshot()
        result_2 = run_demo(assert_mode=False)
        snapshot_2 = _determinism_snapshot()
        assert result == result_2, "Result summary changed between deterministic runs"
        assert snapshot_1 == snapshot_2, "Artifact hashes changed between deterministic runs"
        print("Determinism: PASS (two consecutive runs produced identical tracked artifact hashes)")
    print(f"Winner seed: {result['winner']}")
    print(f"Adjacent proof: {'PASS' if result['adjacent_mandate_proof'] else 'FAIL'}")
    print(f"Sovereign artifact: {result['sovereign_artifact']}")
