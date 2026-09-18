# tiny-saas

Synthetic example — not a real product. Spec overlay plus a few Python files so you can try SpecPlane without touching this repo’s kernel `specs/`.

Live auth promise: **password reset links expire in 60 minutes** (`src/auth.py`).

## Try

```bash
git clone https://github.com/gauravbaruah/SpecPlane.git
cd SpecPlane
```

Open **`examples/tiny-saas`** as the workspace (File → Open Folder). Then ask Cursor:

> Reset links should expire in 15 minutes instead of 60.

You should not type `retrieve` or `blast`. The agent should classify this as an **evolve**, open a change folder, blast, implement `src/auth.py`, then `check_sync`.

There is already an open billing change (`add_dunning`). Leave it; 60 → 15 is a new auth change.

## Kernel commands (optional)

From this folder, after `pip install -e ../..` from the SpecPlane checkout:

```bash
specplane retrieve capability.authentication
specplane blast component.password_reset
specplane check_sync --changed-ids capability.billing
```
