# Published package

Class: **evolve.** Retrieved `capability.specplane_init` first. Its live ux constraint still says a published PyPI / npx package is not this command. That sentence moves only on accept. This folder does not edit that live file.

## What is drafted

- `capability.specplane_package` is a Phase 1 capability. It has no `realized_by`, so its own blast is empty.
- The change blast is the one to review. It reaches init because this change promises `capability.specplane_init`.
- Four flows, one flowchart each: publish, install from the index, init from the installed package, install from a checkout.

The live sentences were applied on 2026-10-02. Promoted and archived on 2026-10-02.

## Decided

- The public GitHub repository and the PyPI project `specplane` stay on the personal account. Paid sections are sold by Nimble Notions. That does not transfer this repository. Paid code stays out of this public tree until a later change.
- The first publish is the pre-release `0.1.0a1`, not `0.1.0`.
- `specplane uninstall` removes the kit init copied into a destination and leaves `specs/` in place. It does not remove the `specplane` command. That stays a package-manager uninstall.

## Not in this change

The local command log stays on unless a human disables it. Upload stays never. Splitting execution success from SpecPlane outcome is a later evolve.
