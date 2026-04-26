# Scorecard formula guide

## Accepted Opportunity Yield (AOY)
For each lane:

```text
AOY = total accepted usefulness points / total cost units
```

Cost units are provided in `run_costs.template.csv`.

## Speed
For each lane:

```text
time_to_first_accepted_output = minimum time_to_accept_hours among accepted outputs
```

Treatment passes the speed gate if:

```text
(control_time - treatment_time) / control_time >= 0.30
```

## Rework
For each lane:

```text
average_rework = mean rework_rounds among accepted outputs
```

Treatment passes the rework gate if:

```text
(control_rework - treatment_rework) / control_rework >= 0.40
```

## Evidence completeness
For each accepted output, compute:

```text
evidence_fraction = sum(
  evidence_code_pointer,
  evidence_broken_condition,
  evidence_repro,
  evidence_severity_rationale,
  evidence_fix,
  evidence_replay_artifact
) / 6
```

Then average over accepted outputs.

Treatment passes the evidence gate if:

```text
(treatment_evidence - control_evidence) / control_evidence >= 0.20
```

## Safety regression
Treatment must have:
- no increase in safety incidents
- no increase in unsupported claims
- no increase in hallucinated references

## Package dependence
For treatment only:

```text
package_dependence = accepted treatment outputs with package_dependency = 1 / total accepted treatment outputs
```

Treatment passes if:

```text
package_dependence >= 0.30
```

## Full adjacent-mandate pass
Treatment must pass **all**:
- AOY uplift
- speed uplift
- rework reduction
- evidence uplift
- no safety regression
- package dependence
