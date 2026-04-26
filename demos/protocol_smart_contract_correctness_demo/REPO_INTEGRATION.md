# REPO INTEGRATION NOTES

This demo is additive and isolated under:

- `demos/protocol_smart_contract_correctness_demo/`

It does not modify existing demos and does not alter contract/backend/sdk/dashboard architecture.

## Relation to existing demos

- `adjacent_mandate_reuse_proof_demo`: compact proof-of-method
- `adjacent_mandate_reuse_proof_real_v1`: operator templates for real execution
- `protocol_smart_contract_correctness_demo` (this demo): public/operator front-door narrative + deterministic simulation loop

## Doctrine stack surfaces

The doctrine stack is intentionally explicit and split into three markdown files:

- `docs/DOCTRINE_STACK.md`
- `docs/THERMODYNAMIC_MODEL.md`
- `docs/NATION_STATE_DOCTRINE.md`

These files are the canonical doctrinal surface for GitHub-rendered math and policy framing, including the explicit statement that the thermodynamic/statistical-physics model is a formal governance analogy (not literal physical law).

Generated doctrine artifacts are emitted under:

- `demo_output/doctrine/doctrine_stack.json`
- `demo_output/doctrine/thermodynamic_model_summary.json`

## Naming migration policy

User-facing language now prefers **Protocol Cybersecurity** over **Protocol Assurance**.
Compatibility aliases are retained in output artifacts to avoid breaking legacy references.

## How to call from docs

Use this path as the first explanatory entry point for the protocol-correctness wedge, then route deep operators to the real-v1 pack.
