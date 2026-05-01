> [!IMPORTANT]
> Please direct application-level proposals (ERCs) to [`ethereum/ERCs`] and all other proposals (EIPs) to [`ethereum/EIPs`].

# Ethereum Request for Comments (ERCs)

The ERC project standardizes and provides high-quality documentation for the Ethereum application layer. This repository tracks past and ongoing improvements to the Ethereum application ecosystem in the form of Ethereum Request for Comments (ERCs). [EIP-1] governs how ERCs are published.

## Contributing

> [!WARNING]
> Before you write an ERC, ideas MUST be thoroughly discussed on [Ethereum Magicians][ethmag] or [Ethereum Research][ethres]. Once consensus is reached, thoroughly read and review [EIP-1], which describes the EIP process.

To create a new proposal, **copy** the [Proposal Template][template] into the [`contents`] directory and rename it to `99999.md` (or `99999/index.md` if you have additional assets). The template has more detailed instructions.

This repository is for documenting standards and not for help implementing them. These types of inquiries should be directed to the [Ethereum Stack Exchange][ethex]. For specific questions and concerns regarding EIPs, it's best to comment on the relevant discussion thread of the EIP denoted by the `discussions-to` tag in the EIP's preamble.

If you would like to become an EIP Editor, please read [EIP-5069].

### Validation and Auto-merging

All pull requests in this repository must pass checks before they can be automatically merged:

- [eip-review-bot] determines when PRs can be automatically merged [^1]
- EIP-1 rules are enforced using [`eipw`] [^2]
- Markdown best practices are checked using [markdownlint] [^2]

## Local Development

The ERCs repo uses the shared `build-eips` multi-repo workspace for local site builds, live previews, and editorial validation. The setup script bootstraps the surrounding workspace so, with just a few commands, you can:

* build and serve the ERCs site with the local theme repo and sibling proposal repos like EIPs
* include tracked local edits without committing them first
* render only selected proposals to save time when a full site build is unnecessary
* run targeted `eipw` editorial checks for proposals before opening or updating pull requests
* diagnose missing workspace pieces with `build-eips doctor`

Run the commands below from this ERCs repo. From the workspace root, use `-C ERCs` before the command.

### Minimum Requirements

Local workspace commands require these tools on `PATH`:

* Git
* `build-eips`
* Zola 0.22.1

Git must be installed separately. The setup script locates or installs `build-eips` and Zola, adds locally installed tool directories to `PATH` for the current shell session, and prints guidance for making those `PATH` changes permanent.

### Bootstrap The Workspace

Run the setup script once from this repo.

Linux and macOS:

```sh
./scripts/dev-setup
```

Windows PowerShell:

```powershell
.\scripts\dev-setup.ps1
```

The setup script initializes the workspace one directory above this repo, runs `build-eips doctor`, and prints the next local commands.

After setup, the generated workspace guide is available at `../WORKSPACE.md`. Use that file for the full command reference and workspace details.

After setup, the workspace has this layout:

```text
EIPs-project/
├── .build-eips.toml
├── WORKSPACE.md
├── .local-build/
├── EIPs/
├── ERCs/
└── theme/
```

### Build And Serve Locally

Use the main site commands from this repo:

```bash
build-eips serve
build-eips check
build-eips build
build-eips doctor
```

By default, `build`, `serve`, and `check` use the local workspace in dirty mode, which includes tracked working-tree edits from this repo. Use `--clean` when you want to ignore tracked local proposal edits for one command:

```bash
build-eips check --clean
build-eips build --clean
build-eips serve --clean
```

From the workspace root, run the same commands with `-C ERCs`:

```bash
build-eips -C ERCs serve
build-eips -C ERCs check
```

### Target Specific Proposals

Full local `build` and `serve` runs can take time because they process every proposal file. Use targeted rendering when you only need to test a few proposals or theme changes against a small proposal set:

```bash
build-eips serve --only 555
build-eips build --only 555
build-eips build --only 555 678
```

You can also set a default target list in the workspace `.build-eips.toml`:

```toml
[render]
only = [555, 678]
```

CLI `--only` replaces `[render].only` for that run. For edge cases and exact filtering behavior, see `../WORKSPACE.md`.

### Editorial Validation

Use editorial commands when you want targeted `eipw` validation before opening or updating a pull request.

Both `editorial lint` and `editorial check` take the same selector modes:

* proposal numbers or repo-relative proposal paths for explicit targets
* `--working-tree` for tracked dirty proposal files
* `--against-upstream` for proposal files changed versus the upstream merge-base
* `--batch <path>` for a repeatable target list

They also accept `eipw` options such as `--format github`.

`editorial lint` runs targeted editorial validation:

```bash
build-eips editorial lint 1
build-eips editorial lint --working-tree
build-eips editorial lint --against-upstream --format github
```

`editorial check` runs targeted editorial validation first, then reuses the local `check` path:

```bash
build-eips editorial check 1
build-eips editorial check --working-tree
build-eips editorial check --against-upstream --format github
```

Use a batch file when you want to lint or build-check the same proposal set repeatedly. A batch file is a plain text file with one proposal number or repo-relative proposal path per line:

```txt
1
7949
content/07950.md
```

```bash
build-eips editorial lint --batch ../editor-batch.txt
build-eips editorial check --batch ../editor-batch.txt
```

### Full Workspace Reference

For local server settings, `preview`, remote staging/production commands, parity commands, source overrides, side-by-side build roots, and detailed dirty-mode behavior, use the generated workspace guide:

```bash
../WORKSPACE.md
```

## Preferred Citation Format

The canonical URL for an EIP that has achieved draft status at any point is at <https://eips.ethereum.org/>. For example, the canonical URL for EIP-1 is <https://eips.ethereum.org/1/>.

Consider any document not published at <https://eips.ethereum.org/> as a working paper. Additionally, consider published EIPs with a status of "draft", "review", or "last call" to be incomplete drafts, and note that their specification is likely to be subject to change.

[^1]: <https://github.com/ethereum/EIPs/blob/master/.github/workflows/auto-review-bot.yml>
[^2]: <https://github.com/ethereum/EIPs/blob/master/.github/workflows/ci.yml>

[`build-eips`]: https://github.com/ethereum/build-eips
[markdownlint]: https://github.com/DavidAnson/markdownlint
[`eipw`]: https://github.com/ethereum/eipw
[eip-review-bot]: https://github.com/ethereum/eip-review-bot/
[`ethereum/ERCs`]: https://github.com/ethereum/ERCs
[`ethereum/EIPs`]: https://github.com/ethereum/EIPs
[EIP-1]: https://eips.ethereum.org/1/
[ethmag]: https://ethereum-magicians.org/
[ethres]: https://ethresear.ch/t/read-this-before-posting/8
[template]: https://github.com/ethereum/EIPs/blob/master/docs/template.md
[`contents`]: https://github.com/ethereum/EIPs/tree/master/contents
[ethex]: https://ethereum.stackexchange.com
[status]: https://eips.ethereum.org/
[Core EIPs]: https://eips.ethereum.org/category/core/
[Networking EIPs]: https://eips.ethereum.org/category/networking/
[Interface EIPs]: https://eips.ethereum.org/category/interface/
[ERCs]: https://eips.ethereum.org/category/erc/
[Meta EIPs]: https://eips.ethereum.org/type/meta/
[Informational EIPs]: https://eips.ethereum.org/type/informational/
[EIP-5069]: https://eips.ethereum.org/5069/
