# V2 CI workspace adapter — F05 candidate

This action no longer downloads `releases/latest` and invokes it in an uninitialized checkout. It builds an explicitly selected immutable tool commit and constructs a new V2 workspace for each invocation.

## Candidate revision and rollout decision

The candidate now selects **`ritovision/eip-preprocessor` at `ce162f863f30e5c4ff5b68ddeac4040ee1ff1298`**, containing the bounded R01–R06 corrections, instead of the pre-correction audited tool. The committed `Build.toml` selects **`ritovision/eips-wg-theme` at `b4b3b96af9a8068ef39b65653ef9e05c9eac35e4`**, the already reviewed combination of both F06 optimizations. EIPs and ERCs use the same pair.

These are exact candidate selectors, **not a claim that the commits have already been pushed, independently approved, or exercised in hosted Actions**. Before merging this consumer rollout, publish/approve the selected tool and theme commits in the indicated repositories (or promote repository/ref pairs together to their reviewed canonical counterparts), then run hosted Actions/Pages acceptance. Do not merge a selector whose object is unavailable. A missing selected object fails closed; branches, tags, `latest`, and old-version fallbacks are not used.

The local selected-stack test reads these actual action/manifest selectors, fetches the exact tool commit, compiles its locked source, initializes the exact pinned theme and source/sibling heads, and runs both real full builds. Test-only URL rewrites point the declared remotes at local repositories; they do not edit project/global Git configuration and do not prove remote distribution or hosted permissions.

Source-building is deliberate pre-release integration policy. Once an approved release exists, an independently reviewed checksum-verified immutable release installation path can replace it without changing the workspace contract.

## Execution contract

* Source: a fresh clone of the input repository's exact HEAD, detached and verified. Uncommitted or untracked local edits are not CI input. The original checkout and its index are unchanged.
* Workspace: private per-invocation directory under `RUNNER_TEMP`; the tool's own `init` constructs sisters and the theme. Committed active `.build-eips.toml` overrides are rejected. Setup logs go to stderr; only the requested command contributes to `stdout` outputs.
* Theme: a freshly initialized checkout at the active committed manifest pin. Markdown lint uses that same checkout, not an unrelated floating theme branch.
* Siblings: committed checkouts cloned from active `Build.toml` locations by init. This retains the current product's floating sibling-head policy, not cross-repository reproducibility at independently pinned sibling SHAs. Exact selected sibling HEADs are recorded in `workspace-evidence.json`.
* Publication: remove init's development-only localhost override and target filter. The committed active manifest supplies the publication base URL. The explicit build root is `<CI workspace>/build`. The action returns its actual output directory only after a successful nonempty build; publication uploads that output rather than guessing a relative legacy path.
* Cleanliness: `build` and `check` use `--clean`; editorial has no such flag and runs on the same newly cloned, verified-clean snapshot. `changed` retains upstream-comparison semantics and produces only changed paths.
* Lifetime: workspace, tool, and output directories remain available for subsequent job steps. They are job-scoped temporary runner state, not persistent project files. The adapter never deploys by itself.

GitHub-hosted Ubuntu must provide Git, Python 3.11+, Cargo/Rust capable of building the selected locked tool source, wget, tar, and SHA-256 verification. Zola remains pinned at 0.22.1 with the existing checked-in archive digest. No new credential-bearing checkout or privileged PR trigger is introduced.

## Local contract test

```sh
python3 .github/actions/build-eips/test_contract.py \
  --build-eips /absolute/path/to/the/current/build-eips \
  --evidence /absolute/path/to/a/new/evidence-directory
```

The test uses local Git fixture repositories and real Zola to cover build, check, no-change editorial check, nonempty changed-file stdout, real editorial-error annotations/exit propagation, failed-command exit/output behavior, exact source/pin selection, publication URLs, dirty-source exclusion, source/index preservation, immutable revision validation, and multiline output boundaries. Hosted Actions, release distribution, permissions, and actual Pages deployment are separate rollout acceptance—not consequences of a local pass.

## Exact selected-stack acceptance (POSIX)

```sh
python3 .github/actions/build-eips/test_selected_stack.py \
  --workspace /absolute/coordinated-workspace \
  --evidence /absolute/new-evidence-directory \
  --cargo-target /absolute/shared-cargo-target
```

This additional test requires PyYAML and uses a process-local home/Git configuration. It builds the selected source in the debug profile for local acceptance; the hosted release-profile build, GitHub triggers/permissions, artifact upload and Pages deployment remain separate rollout checks. Public URLs, source content and current pins are not rewritten inside the consuming manifests.
