---
title: Home
extra:
  homepage_badges:
    - href: https://discord.gg/Nz6rtfJ8Cu
      image: https://dcbadge.limes.pink/api/server/Nz6rtfJ8Cu?style=flat
      alt: Badge for EIP Editor Discord channel
    - href: https://discord.gg/EVTQ9crVgQ
      image: https://dcbadge.limes.pink/api/server/EVTQ9crVgQ?style=flat
      alt: Badge for Ethereum R&D Discord channel
    - href: https://discord.gg/mRzPXmmYEA
      image: https://dcbadge.limes.pink/api/server/mRzPXmmYEA?style=flat
      alt: Badge for Ethereum Wallets Discord channel
    - href: https://discord.gg/9FxN6CfaQR
      image: https://dcbadge.limes.pink/api/server/9FxN6CfaQR?style=flat
      alt: Badge for ERCRef Discord channel
    - href: ./atom.xml
      image: https://img.shields.io/badge/rss-Everything-red.svg
      alt: RSS feed for everything
    - href: ./status/last-call/atom.xml
      image: https://img.shields.io/badge/rss-Last%20Calls-red.svg
      alt: RSS feed for last calls
---

# EIPs & ERCs

<!-- TODO: Recreate email alerts -->

Ethereum Improvement Proposals (EIPs) describe standards for the Ethereum
platform, including core protocol specifications, client APIs, and contract
standards. Network upgrades are discussed separately in the
[Ethereum Project Management][ethpm] repository.

## Contributing

First review [EIP-1](./00001.md), then clone the repository and add your
proposal to it. There is a [template here][template]. Finally, submit a pull
request to the [`ethereum/EIPs`] or [`ethereum/ERCs`] repository, as
appropriate.

## Proposal Statuses

- **_Idea_**: An idea that is pre-draft. This is not tracked within a
  repository.
- **Draft**: The first formally tracked stage of a proposal in development. A
  proposal is merged as a Draft by an EIP Editor into either the EIP or ERC
  repository when properly formatted.
- **Review**: An EIP Author marks their proposal as ready for and requesting
  peer review. Proposals at this stage are fully specified, but still subject
  to significant change.
- **Last Call**: An EIP Author marks their proposal as complete and begins the
  last review window (`last-call-deadline`, typically 14 days) before moving to
  Final. If the review window passes without significant changes, the proposal
  can advance to Final, otherwise it should return to Review or Draft.
- **Final**: This proposal represents the completed standard. A Final proposal
  is, with few exceptions, immutable. It should only be updated to correct
  errata and add non-normative clarifications.
- **Withdrawn**: An EIP Author has withdrawn the proposal. This state is
  immutable, and the proposal can no longer be resurrected using its same
  number. If the idea is pursued at later date it will be considered a new
  proposal, with a new number.
- **Living**: A special status for EIPs that are designed to be continually
  updated and not reach a state of finality. This includes, most notably,
  EIP-1.

## Proposal Types

Proposals are separated into a number of types, and each has its own list.

### [Standards Track](./type/standards-track/)

Describes any change that affects most or all Ethereum implementations, such as
a change to the network protocol, a change in block or transaction validity
rules, proposed application standards/conventions, or any change or addition
that affects the interoperability of applications using Ethereum. Furthermore
Standards Track proposals can be broken down into the following categories.

#### [Core](./category/core/)

Improvements requiring a consensus fork (e.g. [EIP-5](./00005.md) or
[EIP-211](./00211.md)), as well as changes that are not necessarily consensus
critical but may be relevant to “core dev” discussions (for example, the PoA
algorithm for testnets described in [EIP-225](./00225.md)).

#### [Networking](./category/networking/)

Includes improvements around devp2p ([EIP-8](./00008.md)) and Light Ethereum
Subprotocol, as well as proposed improvements to network protocol
specifications of whisper and swarm.

#### [Interface](./category/interface/)

Includes improvements around client API/RPC specifications and standards, and
also certain language-level standards like method names ([EIP-6](./00006.md))
and contract ABIs.

#### [ERC](./category/erc/)

Application-level standards and conventions, including contract standards such
as token standards ([ERC-20](./00020.md)), name registries
([ERC-137](./00137.md)), URI schemes ([ERC-681](./00681.md)), library/package
formats ([ERC-190](./00190.md)), and account abstraction
([ERC-4337](./04337.md)).

### [Meta](./type/meta/)

Describes a process surrounding Ethereum or proposes a change to (or an event
in) a process. Process EIPs are like Standards Track EIPs but apply to areas
other than the Ethereum protocol itself. They may propose an implementation,
but not to Ethereum's codebase; they often require community consensus; unlike
Informational EIPs, they are more than recommendations, and users are typically
not free to ignore them. Examples include procedures, guidelines, changes to
the decision-making process, and changes to the tools or environment used in
Ethereum development.

### [Informational](./type/informational)

Describes a Ethereum design issue, or provides general guidelines or
information to the Ethereum community, but does not propose a new feature.
Informational EIPs do not necessarily represent Ethereum community consensus or
a recommendation, so users and implementers are free to ignore Informational
EIPs or follow their advice.

[ethpm]: https://github.com/ethereum/pm/

[template]: https://github.com/ethereum/EIPs/blob/master/docs/template.md?plain=1

[`ethereum/EIPs`]: https://github.com/ethereum/EIPs
[`ethereum/ERCs`]: https://github.com/ethereum/ERCs
