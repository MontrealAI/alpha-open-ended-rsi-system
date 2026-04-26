# RUNBOOK — protocol_smart_contract_correctness_demo

## 1) Execute

```bash
python3 run_demo.py --assert
```

## 2) Inspect outputs

Open:

- `demo_output/reports/report.html`
- `demo_output/reports/report.md`
- `demo_output/doctrine/doctrine_stack.json`
- `demo_output/doctrine/thermodynamic_model_summary.json`
- `demo_output/scorecard/adjacent_mandate_scorecard.json`
- `demo_output/proof_docket/proof_docket.json`

## 3) Determinism check

Automatic mode:

```bash
python3 run_demo.py --assert
```

The command performs two back-to-back runs and verifies tracked artifact hashes are identical.

## 4) Doctrine math rendering check (GitHub markdown)

Canonical equations are in:

- `docs/THERMODYNAMIC_MODEL.md`

Validation is enforced during demo execution:

- all doctrine files must exist
- no legacy `\[ ... \]` delimiters are allowed
- no legacy bare `[ ... ]` pseudo-equation delimiters are allowed
- required equations must be present with corrected notation

## 5) Naming compatibility check

This demo now prefers **Protocol Cybersecurity** labels while retaining legacy aliases for replayability:

- `ProtocolCybersecurityPack-v1` + alias file `ProtocolAssurancePack-v1`
- `ProtocolCybersecuritySovereign-v1.synthetic.json` + alias file `ProtocolAssuranceSovereign-v1.synthetic.json`
- `protocol_cybersecurity_studio.json` + compatibility artifact `protocol_assurance_studio.json`

## 6) Interpretation guardrails

This is a synthetic replayable assay. It is suitable for:

- process legibility
- operator training
- proof-surface review

It is not a replacement for a real mandate proof pack.
