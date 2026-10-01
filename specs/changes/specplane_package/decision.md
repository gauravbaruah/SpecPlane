# Published package

Class: **evolve.** Retrieved `capability.specplane_init` first. Its live ux constraint still says a published PyPI / npx package is not this command. That sentence moves only on accept. This folder does not edit that live file.

## What is drafted

- `capability.specplane_package` is a Phase 1 capability. It has no `realized_by`, so its own blast is empty.
- The change blast is the one to review. It reaches init because this change promises `capability.specplane_init`.
- Four flows, one flowchart each: publish, install from the index, init from the installed package, install from a checkout.

## Left open

- Which PyPI account owns the name.
- Whether the first publish is `0.1.0` or a pre-release.
- Whether uninstall is only the package manager.

## Not in this change

The local command log stays on unless a human disables it. Upload stays never. Splitting execution success from SpecPlane outcome is a later evolve.
