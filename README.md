> [!IMPORTANT]
> Please direct application-level proposals (ERCs) to [`ethereum/ERCs`] and all
> other proposals (EIPs) to [`ethereum/EIPs`].

# Ethereum Request for Comments (ERCs)

The ERC project standardizes and provides high-quality documentation for
the Ethereum application layer. This repository tracks past and ongoing
improvements to the Ethereum application ecosystem in the form of Ethereum
Request for Comments (ERCs). [EIP-1] governs how ERCs are published.

## Contributing

> [!WARNING]
> Before you write an ERC, ideas MUST be thoroughly discussed on
> [Ethereum Magicians][ethmag] or [Ethereum Research][ethres]. Once consensus
> is reached, thoroughly read and review [EIP-1], which describes the EIP
> process.

To create a new proposal, **copy** the [Proposal Template][template] into the
[`contents`] directory and rename it to `99999.md` (or `99999/index.md` if you
have additional assets). The template has more detailed instructions.

This repository is for documenting standards and not for help implementing
them. These types of inquiries should be directed to the
[Ethereum Stack Exchange][ethex]. For specific questions and concerns regarding
EIPs, it's best to comment on the relevant discussion thread of the EIP denoted
by the `discussions-to` tag in the EIP's preamble.

If you would like to become an EIP Editor, please read [EIP-5069].

### Validation and Auto-merging

All pull requests in this repository must pass checks before they can be
automatically merged:

- [eip-review-bot] determines when PRs can be automatically merged [^1]
- EIP-1 rules are enforced using [`eipw`] [^2]
- Markdown best practices are checked using [markdownlint] [^2]

### Building Locally

The retained local bootstrap path in this repo is:

```bash
./scripts/dev-setup
build-eips serve
```

`./scripts/dev-setup` locates or installs `build-eips`, runs
`build-eips -C <repo> workspace init <workspace-root>`, runs
`build-eips -C <repo> workspace doctor`, and prints the next direct
`build-eips` commands for this repo.

For the current multi-repo bootstrap and direct command surface, see
[`Workspace Bootstrap`](https://github.com/eips-wg/preprocessor#workspace-bootstrap),
[`Profiles And Overrides`](https://github.com/eips-wg/preprocessor#profiles-and-overrides),
and [`Dirty Mode`](https://github.com/eips-wg/preprocessor#dirty-mode) in
[`eips-wg/preprocessor`](https://github.com/eips-wg/preprocessor).

## Preferred Citation Format

The canonical URL for an EIP that has achieved draft status at any point is at
<https://eips.ethereum.org/>. For example, the canonical URL for EIP-1 is
<https://eips.ethereum.org/1/>.

Consider any document not published at <https://eips.ethereum.org/> as a
working paper. Additionally, consider published EIPs with a status of "draft",
"review", or "last call" to be incomplete drafts, and note that their
specification is likely to be subject to change.

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
