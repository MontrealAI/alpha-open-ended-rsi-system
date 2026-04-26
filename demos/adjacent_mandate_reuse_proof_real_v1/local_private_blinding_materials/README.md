# Local private blinding materials

This directory is intentionally git-ignored.

Use it for private-only blinded experiment files, including:
- `answer_key_m1.private.md`
- `answer_key_m2.private.md`
- `answer_key_m3.private.md`
- `blinded_assignment_map.private.csv`
- `reviewer_identity_map.private.csv`
- `private_commitment_hashes.txt`

Generate scaffold files with:

```bash
python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/setup_blinded_adjacent_transfer_v1.py
python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/generate_private_commitment_hashes.py \
  --private-dir demos/adjacent_mandate_reuse_proof_real_v1/local_private_blinding_materials/results_blinded_adjacent_transfer_v1
```

Do not commit filled private files.
