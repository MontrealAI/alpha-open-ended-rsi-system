⚠️ This is a replicated internal evidence update, not final public proof.

# Adjacent-Mandate Reuse Evidence Update — Internal Rerun Clean v1

This folder is the GitHub-ready counterpart to the stakeholder presentation for the adjacent-mandate reuse rerun.

It records a stricter internal rerun of the real-world proof pack in `../` and should be read as an **evidence update** rather than a repo-wide claim expansion.

## Why this exists

The real-world proof pack defines the experiment, the claim boundary, and the pass thresholds. This rerun asks a harder question than the provisional pilot:

> Can the same frozen capability package pass once on the repo's original adjacent pair and again on a different adjacent pair under the same rubric?

## Experiment identity

- **Experiment ID:** `adjacent-reuse-rerun-clean-v1`
- **Repo:** `MontrealAI/alpha-nova-seeds`
- **Pinned repo SHA:** `97907b70d86f44a5a3f31f71828a9360fd1f6744`
- **Frozen package:** `GovernanceValidationPack-v1`
- **Package hash:** `0f1a9a8a3dfd785cc58c6b96936c891bfb3301bb1ecf8330f95c81c3358a193d`

## Scope

### Mandate 1 — Governance / dispute correctness

Primary scope:

- `contracts/CouncilGovernanceV25.sol`
- `contracts/ChallengePolicyModuleV25.sol`

Goal:

- produce and freeze `GovernanceValidationPack-v1`

### Pass A — Original adjacent pair

Primary scope:

- `contracts/ThresholdNetworkAdapterV25.sol`
- `contracts/SignedAttestationVerifierV25.sol`

Goal:

- rerun the repo's chosen adjacent pair under the frozen package

### Pass B — Second adjacent pair

Primary scope:

- `contracts/NovaSeedRegistryV25.sol`
- `contracts/NovaSeedWorkflowAdapterV25.sol`

Goal:

- test whether the same frozen package transfers to a different adjacent pair in the same wedge

## Frozen package contents

The frozen package is generic rather than pair-specific. It captures four reusable correctness classes:

1. `OBJECT_EXISTENCE_AND_ACTIVE_BINDING`
2. `DISTINCT_ACTOR_AND_WEIGHT_BINDING`
3. `NONCE_BACKED_UNIQUE_IDENTITY`
4. `EVENT_STATE_REPLAY_SURFACE_COMPLETENESS`

The associated treatment query bundle is also generic and explicitly not tailored to a specific adjacent pair.

## Top-line result

- **Pass A:** PASS
- **Pass B:** PASS
- **Combined:** PASS

## Combined scorecard

| Metric | Control | Treatment | Threshold | Result |
|---|---:|---:|---:|---|
| AOY | 0.4167 | 0.7500 | treatment ≥ 35% uplift | PASS |
| Time to first accepted output | 1.60 | 0.90 | treatment ≥ 30% faster | PASS |
| Average rework | 2.00 | 1.00 | treatment ≥ 40% lower | PASS |
| Evidence completeness | 0.6667 | 0.9583 | treatment ≥ 20% higher | PASS |
| Package dependence | 0.0000 | 0.7500 | treatment ≥ 30% | PASS |
| Safety incidents | 0 | 0 | no regression | PASS |

### Combined uplifts

- **AOY uplift:** `+80.00%`
- **Speed uplift:** `+43.75%`
- **Rework reduction:** `50.00%`
- **Evidence completeness uplift:** `+43.75%`
- **Package dependence:** `75.00%`
- **No safety regression:** `PASS`

## Why this matters

This update is materially stronger than the provisional pilot for four reasons:

1. the repo SHA was pinned before execution;
2. answer keys were frozen before each pass;
3. the package was frozen before both adjacent-pair runs;
4. the same package passed on two adjacent pairs rather than one.

That makes the internal evidence for within-wedge adjacent reuse much harder to dismiss.

## What was actually found

### Mandate 1 findings that seeded the package

The package was derived from real governance/dispute findings in the live code, including:

- finalize paths that can proceed without a sufficiently explicit existence / active-binding check,
- quorum or weight paths that are not fully bound to distinct authorized actors,
- timestamp-derived object identity without a nonce-backed collision guard,
- event surfaces that are incomplete for replay or provenance reconstruction.

### Pass A — Threshold / attestation findings

Accepted treatment findings included:

- configured threshold is never enforced at completion;
- trusted signer scope is global rather than profile-bound;
- request identity can collide on same-block duplicate opens;
- completion is not bound to a frozen binding-profile snapshot.

### Pass B — Registry / workflow findings

Accepted treatment findings included:

- review weight is caller-supplied rather than governance-bound;
- review rounds do not freeze a governance-term snapshot;
- reviews are accepted even when no governance term has been opened;
- assay finalization is not bound to a seed/job provenance pair.

## Best-practice alignment

This rerun improved substantially over the provisional pilot:

- exact repo SHA pinned before execution;
- scope, answer keys, cost model, and lane invariants frozen before each pass;
- package frozen before both adjacent-pair runs;
- same scope, rubric, budget, and cost model across lanes;
- blinded output IDs used in adjudication materials;
- intervention log and run register kept.

## Remaining deviations

This is still **not** board-grade or public-grade proof.

Remaining weaknesses:

- no independent blinded reviewers were available in-chat;
- control and treatment were run sequentially rather than in true parallel;
- time-to-accept remains normalized analyst-hours rather than external stopwatch measurements.

These deviations mean the rerun should be treated as **strong replicated internal evidence**, not as the final public proof that the broader compounding claim is fully earned.

## Claim boundary

This evidence update supports the following narrow claim:

> A frozen capability package materially improved adjacent correctness review across two adjacent mandate pairs inside the protocol-and-smart-contract correctness wedge under a fixed internal rubric.

It does **not** support the following stronger claims:

- that AGI Alpha is already publicly proven as a compounding substrate;
- that the broader cybersecurity sovereign is already proven in real-world operation;
- that independent blinded replication has already occurred;
- that this is final security assurance or production-final evidence.

## Is this recursive self-improvement?

**Yes, in a narrow and important sense.**

If a system completes one mandate, freezes the resulting capability into a reusable package, and that package then improves the next mandate, that is a form of **recursive self-improvement through archived capability reuse**.

But it is **not** the strongest or most speculative version of recursive self-improvement.

More precise language here is:

- **bounded recursive self-improvement**
- **recursive capability accumulation**
- **externally-governed recursive improvement**

Why that distinction matters:

- the system is not claiming unconstrained autonomous self-redesign;
- the improvement is mediated by explicit package freeze, review, and scoring gates;
- governance and proof surfaces remain outside the package itself;
- the current evidence is within one wedge, not open-ended across the whole stack.

So the right answer is:

> If this pattern continues under independent controlled reruns, then yes — AGI Alpha is demonstrating a bounded, evidence-bearing form of recursive self-improvement.  
> It is not yet evidence for unconstrained open-ended self-improvement.

## Suggested repo placement

Recommended path:

```text
demos/adjacent_mandate_reuse_proof_real_v1/results_internal_rerun_clean_v1/
```

This keeps the evidence update attached to the real-world proof pack without widening the repo's public claim boundary.

## Related files

- Parent real-world proof pack: `../README.md`
- Parent runbook: `../RUNBOOK.md`
- Demo ladder index: `../../README.md`
- Repo root posture: `../../../README.md`
- Machine-readable summary: `./summary_metrics.json`
- Suggested integration note: `./REPO_INTEGRATION.md`

## Bottom line

This folder should be read as:

> stronger replicated internal evidence that adjacent capability reuse is real inside the first wedge,

not as:

> final public proof that AGI Alpha has already crossed the full compounding-intelligence threshold.
