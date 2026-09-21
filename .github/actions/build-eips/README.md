# V2 CI workspace adapter — F05 candidate

This action no longer downloads `releases/latest` and invokes it in an uninitialized checkout. It builds an explicitly selected immutable tool commit and constructs a new V2 workspace for each invocation.

## Candidate revision and rollout decision

The candidate defaults to `ritovision/eip-preprocessor` at `a9e5b976bb64699b61ce45143d4cca6357eeeda2`: the exact publicly available V2 commit audited before these corrections. This is a **pre-release test pin, not an assertion that the final corrected release is already published or approved**. Before canonical rollout, promote `preprocessor-repository` and `preprocessor-ref` together to the reviewed upstream/integrated commit. EIPs and ERCs should use the same reviewed tool revision. The complete 40-hex SHA is required; branches, tags, and `latest` are rejected. There is no fallback to an old released binary.

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
