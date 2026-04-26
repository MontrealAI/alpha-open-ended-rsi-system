# Treatment lane instructions

## Allowed materials
Everything available to control, plus:

- `GovernanceValidationPack-v1`
- package ontology
- package extraction schema
- mechanism library
- workflow template
- scoring rubric
- safety routing rules
- query bundle
- OpenClaw skill wrapper

## Lane invariants
- same time budget as control
- same reviewer rubric as control
- same compute budget as control
- all interventions logged

## Package dependence rule
Every accepted treatment output must record whether it depended on at least one package component.
