# Blinding protocol

## Goal
Reviewers should not know whether an output came from the control or treatment lane.

## Procedure
1. Assign blinded output IDs
2. Strip lane labels from reviewer packets
3. Remove timestamps and operator names where practical
4. Use a private lane map kept outside the public repo
5. Reveal lane assignments only after adjudication is complete

## Private files
Use `05_private_local_only/blinded_assignment_map.template.csv` and keep the filled file private.
