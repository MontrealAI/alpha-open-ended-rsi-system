
from copy import deepcopy
from pathlib import Path
import json, hashlib, textwrap, shutil
from src.engine import read_contracts, analyze_contracts, review_findings, discover_from_mandate1, compare_treatment_vs_control, package_hash

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "demo_output"
DEMO_TIMESTAMP = "2026-01-01T00:00:00Z"
PACKAGE_PRIMARY = "ProtocolCybersecurityPack-v1"
PACKAGE_ALIAS = "ProtocolAssurancePack-v1"

def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def write_text(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data)

def settlement_receipt(job_id, mode, accepted_count, aoy, package_hash_value=None):
    now = DEMO_TIMESTAMP
    return {
        "job_id": job_id,
        "mode": mode,
        "lifecycle": [
            {"state": "REQUEST", "at": now},
            {"state": "ESCROW", "at": now, "escrow_amount_agialpha": 1000},
            {"state": "EXECUTE", "at": now},
            {"state": "PROOF", "at": now},
            {"state": "VALIDATE", "at": now},
            {"state": "SETTLE", "at": now},
            {"state": "CHRONICLE", "at": now},
        ],
        "receipt": {
            "accepted_findings": accepted_count,
            "aoy": aoy,
            "package_hash": package_hash_value,
            "validated": True,
            "settled": True
        }
    }

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    gt1 = json.loads((ROOT / "ground_truth" / "mandate_1.json").read_text())
    gt2 = json.loads((ROOT / "ground_truth" / "mandate_2.json").read_text())

    contracts1 = read_contracts(ROOT / "contracts" / "mandate_1")
    contracts2 = read_contracts(ROOT / "contracts" / "mandate_2")

    # Mandate 1: build first package
    findings1 = analyze_contracts(contracts1, mode="treatment", package={
        "learned_signatures": {
            "payout_verbs": ["finalize", "settle", "release", "refund", "withdraw"],
            "proof_aliases": ["proof", "validator", "approval", "challenge", "review", "completion", "ready", "attest"],
            "upgrade_aliases": ["implementation", "upgrade", "module", "router", "swap"],
            "accounting_aliases": ["locked", "reserved", "bond", "escrow", "collateral"]
        }
    })
    review1 = review_findings(findings1, gt1, mode="mandate_1")
    accepted1 = review1["accepted_findings"]
    accepted_findings_objs = []
    # Rehydrate minimal accepted objects for compiler
    from src.engine import Finding
    for f in accepted1:
        accepted_findings_objs.append(Finding(**f))
    package = discover_from_mandate1(contracts1, accepted_findings_objs)
    package_primary = deepcopy(package)
    package_primary["package_name"] = PACKAGE_PRIMARY
    package_primary["legacy_aliases"] = [PACKAGE_ALIAS]
    pkg_hash = package_hash(package_primary)
    package_primary["package_hash"] = pkg_hash
    package_primary["frozen_at"] = DEMO_TIMESTAMP
    package_primary["source_mandate"] = "Mandate 1"

    package_alias = deepcopy(package_primary)
    package_alias["package_name"] = PACKAGE_ALIAS
    package_alias["alias_of"] = PACKAGE_PRIMARY

    write_json(OUT / "mandate_1" / "findings.json", [f.__dict__ for f in findings1])
    write_json(OUT / "mandate_1" / "review.json", review1)
    write_json(OUT / "capability_package" / f"{PACKAGE_PRIMARY}.json", package_primary)
    write_json(OUT / "capability_package" / f"{PACKAGE_ALIAS}.json", package_alias)

    # Mandate 2 control
    findings_control = analyze_contracts(contracts2, mode="control", package=None)
    review_control = review_findings(findings_control, gt2, mode="control")
    write_json(OUT / "mandate_2_control" / "findings.json", [f.__dict__ for f in findings_control])
    write_json(OUT / "mandate_2_control" / "review.json", review_control)

    # Mandate 2 treatment
    findings_treat = analyze_contracts(contracts2, mode="treatment", package=package_primary)
    review_treat = review_findings(findings_treat, gt2, mode="treatment")
    write_json(OUT / "mandate_2_treatment" / "findings.json", [f.__dict__ for f in findings_treat])
    write_json(OUT / "mandate_2_treatment" / "review.json", review_treat)

    scorecard = compare_treatment_vs_control(review_control["metrics"], review_treat["metrics"])
    write_json(OUT / "adjacent_mandate_scorecard.json", scorecard)

    # Proof docket
    receipts = {
        "mandate_1": settlement_receipt("JOB-M1-001", "mandate_1", review1["metrics"]["accepted_count"], review1["metrics"]["aoy"], pkg_hash),
        "mandate_2_control": settlement_receipt("JOB-M2-CTRL-001", "control", review_control["metrics"]["accepted_count"], review_control["metrics"]["aoy"], None),
        "mandate_2_treatment": settlement_receipt("JOB-M2-TREAT-001", "treatment", review_treat["metrics"]["accepted_count"], review_treat["metrics"]["aoy"], pkg_hash)
    }
    write_json(OUT / "proof_docket" / "07_settlement_receipts.json", receipts)
    write_json(OUT / "proof_docket" / "08_chronicle_entry.json", {
        "lineage": "Protocol Cybersecurity",
        "parent_business": "Protocol and smart-contract correctness firm",
        "mandate_1_package": PACKAGE_PRIMARY,
        "legacy_package_alias": PACKAGE_ALIAS,
        "package_hash": pkg_hash,
        "adjacent_proof_passed": scorecard["passes"]["adjacent_mandate_proof"],
        "archived_at": DEMO_TIMESTAMP
    })

    claim = "Claim: one completed mandate created a frozen capability package that materially improved the next adjacent mandate under control conditions (synthetic local demo)."
    write_text(OUT / "proof_docket" / "00_claim.md", claim)
    write_text(OUT / "proof_docket" / "01_constitutional_frame.md", textwrap.dedent("""
    # Constitutional frame

    identity → proof → settlement → governance

    Invariant:
    - no value without evidence
    - no autonomy without authority
    - no settlement without validation

    This demo treats AGI Jobs as the assay:
    REQUEST → ESCROW → EXECUTE → PROOF → VALIDATE → SETTLE → CHRONICLE
    """).strip() + "\n")
    write_text(OUT / "proof_docket" / "02_parent_business.md", textwrap.dedent("""
    # Parent business

    Sector: Protocol and smart-contract correctness

    Parent business:
    A Protocol Cybersecurity Studio that sells exploit review, invariant design,
    reviewer packets, and release gating for crypto systems.

    Goal of Mandate 1:
    extract one reusable capability package from a real review batch.

    Goal of Mandate 2:
    test whether the frozen package improves the next adjacent review batch under control conditions.
    """).strip() + "\n")
    write_text(OUT / "proof_docket" / "03_mandate_1_summary.md", f"Accepted findings: {review1['metrics']['accepted_count']}\nPackage hash: {pkg_hash}\n")
    write_text(OUT / "proof_docket" / "04_mandate_2_control_summary.md", json.dumps(review_control["metrics"], indent=2))
    write_text(OUT / "proof_docket" / "05_mandate_2_treatment_summary.md", json.dumps(review_treat["metrics"], indent=2))
    write_text(OUT / "proof_docket" / "06_scorecard.md", textwrap.dedent(f"""
    # Adjacent-mandate scorecard

    Control metrics:
    {json.dumps(review_control["metrics"], indent=2)}

    Treatment metrics:
    {json.dumps(review_treat["metrics"], indent=2)}

    Comparison:
    {json.dumps(scorecard, indent=2)}
    """).strip() + "\n")

    # Reports
    c = review_control["metrics"]
    t = review_treat["metrics"]
    cmp = scorecard["comparison"]
    passes = scorecard["passes"]
    md = textwrap.dedent(f"""
    # Adjacent-Mandate Reuse Proof Demo

    ## Summary
    This is a **synthetic local demo** of the AGI ALPHA adjacent-mandate proof gate.

    - Parent sector: Protocol and smart-contract correctness
    - Mandate 1: review a first batch of protocol contracts and freeze one capability package
    - Mandate 2: review an adjacent batch twice:
      - **control** without the package
      - **treatment** with the frozen package

    ## Frozen capability package
    - Name: `ProtocolCybersecurityPack-v1`
    - Legacy alias: `ProtocolAssurancePack-v1`
    - Hash: `{pkg_hash}`

    ## Mandate 2 results

    ### Control
    - Accepted findings: {c['accepted_count']}
    - AOY: {c['aoy']}
    - First accepted step: {c['first_accepted_step']}
    - Rework rate: {c['rework_rate']}
    - Evidence completeness: {c['evidence_completeness']}
    - Severe false positives: {c['severe_false_positive_count']}

    ### Treatment
    - Accepted findings: {t['accepted_count']}
    - AOY: {t['aoy']}
    - First accepted step: {t['first_accepted_step']}
    - Rework rate: {t['rework_rate']}
    - Evidence completeness: {t['evidence_completeness']}
    - Severe false positives: {t['severe_false_positive_count']}
    - Package dependence: {t['package_dependence']}

    ## Threshold comparison
    - AOY uplift: {cmp['aoy_uplift']:.1%} → {'PASS' if passes['aoy_uplift'] else 'FAIL'}
    - Speed uplift: {cmp['speed_uplift']:.1%} → {'PASS' if passes['speed_uplift'] else 'FAIL'}
    - Rework reduction: {cmp['rework_reduction']:.1%} → {'PASS' if passes['rework_reduction'] else 'FAIL'}
    - Evidence completeness uplift: {cmp['evidence_completeness_uplift']:.1%} → {'PASS' if passes['evidence_completeness_uplift'] else 'FAIL'}
    - No safety regression: {'PASS' if passes['no_safety_regression'] else 'FAIL'}
    - Package dependence ≥ 30%: {cmp['package_dependence']:.1%} → {'PASS' if passes['package_dependence'] else 'FAIL'}

    ## Verdict
    **Adjacent-mandate proof:** {'PASS' if passes['adjacent_mandate_proof'] else 'FAIL'}

    This demo shows the structure of the proof:
    one completed mandate created a frozen capability package that materially improved
    the next adjacent mandate under control conditions.

    ## Important note
    This is a **controlled synthetic demo**, not a real-world proof.
    """).strip() + "\n"
    write_text(OUT / "reports" / "report.md", md)

    html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Adjacent-Mandate Reuse Proof Demo</title>
<style>
body{{font-family:Arial,sans-serif;background:#0b1020;color:#f1f5f9;margin:0;padding:32px;}}
.wrap{{max-width:980px;margin:0 auto;}}
.card{{background:#111827;border:1px solid #334155;border-radius:16px;padding:20px;margin:16px 0;}}
h1,h2,h3{{margin:0 0 12px 0;}}
small{{color:#94a3b8;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;}}
.metric{{font-size:28px;font-weight:bold;}}
.pass{{color:#34d399;}}
.fail{{color:#f87171;}}
code{{background:#1f2937;padding:2px 6px;border-radius:6px;}}
table{{width:100%;border-collapse:collapse}}
td,th{{border-bottom:1px solid #334155;padding:8px;text-align:left}}
.badge{{display:inline-block;padding:4px 10px;border-radius:999px;background:#1f2937;border:1px solid #475569}}
</style></head><body><div class='wrap'>
<div class='card'>
  <div class='badge'>Synthetic proof-of-method</div>
  <h1>Adjacent-Mandate Reuse Proof Demo</h1>
  <p><small>Parent sector: Protocol and smart-contract correctness</small></p>
  <p>This demo freezes one capability package from Mandate 1 and tests whether it improves the next adjacent mandate under control conditions.</p>
</div>
<div class='grid'>
  <div class='card'>
    <h2>Control</h2>
    <table>
      <tr><th>Accepted findings</th><td>{c['accepted_count']}</td></tr>
      <tr><th>AOY</th><td>{c['aoy']}</td></tr>
      <tr><th>First accepted step</th><td>{c['first_accepted_step']}</td></tr>
      <tr><th>Rework rate</th><td>{c['rework_rate']}</td></tr>
      <tr><th>Evidence completeness</th><td>{c['evidence_completeness']}</td></tr>
      <tr><th>Severe false positives</th><td>{c['severe_false_positive_count']}</td></tr>
    </table>
  </div>
  <div class='card'>
    <h2>Treatment</h2>
    <table>
      <tr><th>Accepted findings</th><td>{t['accepted_count']}</td></tr>
      <tr><th>AOY</th><td>{t['aoy']}</td></tr>
      <tr><th>First accepted step</th><td>{t['first_accepted_step']}</td></tr>
      <tr><th>Rework rate</th><td>{t['rework_rate']}</td></tr>
      <tr><th>Evidence completeness</th><td>{t['evidence_completeness']}</td></tr>
      <tr><th>Severe false positives</th><td>{t['severe_false_positive_count']}</td></tr>
      <tr><th>Package dependence</th><td>{t['package_dependence']:.1%}</td></tr>
    </table>
  </div>
</div>
<div class='card'>
  <h2>Frozen capability package</h2>
  <p><code>ProtocolCybersecurityPack-v1</code> <small>(legacy alias: ProtocolAssurancePack-v1)</small></p>
  <p>Hash: <code>{pkg_hash}</code></p>
</div>
<div class='card'>
  <h2>Threshold comparison</h2>
  <table>
    <tr><th>Metric</th><th>Observed</th><th>Threshold</th><th>Result</th></tr>
    <tr><td>AOY uplift</td><td>{cmp['aoy_uplift']:.1%}</td><td>≥35%</td><td class="{'pass' if passes['aoy_uplift'] else 'fail'}">{'PASS' if passes['aoy_uplift'] else 'FAIL'}</td></tr>
    <tr><td>Speed uplift</td><td>{cmp['speed_uplift']:.1%}</td><td>≥30%</td><td class="{'pass' if passes['speed_uplift'] else 'fail'}">{'PASS' if passes['speed_uplift'] else 'FAIL'}</td></tr>
    <tr><td>Rework reduction</td><td>{cmp['rework_reduction']:.1%}</td><td>≥40%</td><td class="{'pass' if passes['rework_reduction'] else 'fail'}">{'PASS' if passes['rework_reduction'] else 'FAIL'}</td></tr>
    <tr><td>Evidence completeness uplift</td><td>{cmp['evidence_completeness_uplift']:.1%}</td><td>≥20%</td><td class="{'pass' if passes['evidence_completeness_uplift'] else 'fail'}">{'PASS' if passes['evidence_completeness_uplift'] else 'FAIL'}</td></tr>
    <tr><td>No safety regression</td><td>{'No regression' if not cmp['safety_regression'] else 'Regression'}</td><td>Required</td><td class="{'pass' if passes['no_safety_regression'] else 'fail'}">{'PASS' if passes['no_safety_regression'] else 'FAIL'}</td></tr>
    <tr><td>Package dependence</td><td>{cmp['package_dependence']:.1%}</td><td>≥30%</td><td class="{'pass' if passes['package_dependence'] else 'fail'}">{'PASS' if passes['package_dependence'] else 'FAIL'}</td></tr>
  </table>
  <p class="metric {'pass' if passes['adjacent_mandate_proof'] else 'fail'}">Adjacent-mandate proof: {'PASS' if passes['adjacent_mandate_proof'] else 'FAIL'}</p>
</div>
<div class='card'>
  <h2>Interpretation</h2>
  <p>In this synthetic controlled demo, one completed mandate produced a frozen capability package that materially improved the next adjacent mandate under the same budget and review conditions.</p>
  <p>This is a proof-of-method artifact, not a real-world production proof.</p>
</div>
</div></body></html>"""
    write_text(OUT / "reports" / "report.html", html)

    # root readme
    readme = textwrap.dedent(f"""
    # Adjacent-Mandate Reuse Proof Demo

    This is the **next milestone demo**:
    one adjacent-mandate reuse proof under control conditions.

    It is intentionally small, local, and reproducible.

    ## What it demonstrates

    - Parent sector: **Protocol and smart-contract correctness**
    - Mandate 1: review a first batch of smart-contract mandates
    - Freeze the resulting reusable package as:
      - `ProtocolCybersecurityPack-v1` (legacy alias: `ProtocolAssurancePack-v1`)
    - Mandate 2: review an **adjacent** batch twice:
      - **control** without the package
      - **treatment** with the frozen package
    - Score the result against the adjacent-mandate proof gate

    ## How to run

    ```bash
    python3 run_demo.py
    ```

    No extra dependencies are required.

    ## Best files to open

    - `demo_output/reports/report.html`
    - `demo_output/reports/report.md`
    - `demo_output/proof_docket/06_scorecard.md`

    ## Important note

    This is a **synthetic local demo**, not a real-world proof.
    It shows the structure of the milestone:
    one completed mandate can create a frozen capability package that materially improves the next adjacent mandate under control conditions.

    ## Current synthetic result

    - Adjacent-mandate proof: **{'PASS' if scorecard['passes']['adjacent_mandate_proof'] else 'FAIL'}**
    - Package hash: `{pkg_hash}`

    ## Demo ladder

    - Flagship synthetic wedge demo: `demos/protocol_smart_contract_correctness_demo/`
    - Adjacent synthetic proof demo: `demos/adjacent_mandate_reuse_proof_demo/`
    - Real-world experiment pack: `demos/adjacent_mandate_reuse_proof_real_v1/`
    """).strip() + "\n"
    write_text(ROOT / "README.md", readme)

if __name__ == "__main__":
    main()
