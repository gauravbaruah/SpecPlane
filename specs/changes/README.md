# Change folders

In-flight write path for the kernel (`kind: learn | fix | evolve`). Not 5C specs. `honest_kernel/` is this slice.

v9.1.0 `validate.py` loads every `*.yaml` under `specs/` and will flag these files (no `meta.id`). That is expected until schema unfreeze teaches the toolkit to skip or understand this folder. Do not invent a 5C type for them.
