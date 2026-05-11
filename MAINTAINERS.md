# Maintainers

This document lists the maintainers of the `inundation` project and explains the governance structure.

## Current Maintainers

### Fernando E. Romero Galvan

- **Role:** Primary Maintainer
- **GitHub:** [@ferg-dwr](https://github.com/ferg-dwr)
- **Affiliation:** California Council of Science and Technology Fellow, California Department of Water Resources (DWR)
- **Areas of responsibility:**
  - Overall project direction
  - Code review and PR approval
  - Release management
  - Security response
  - Community engagement

## Becoming a Maintainer

We welcome additional maintainers as the project grows. Maintainers are typically chosen from active contributors who have demonstrated:

- **Consistent high-quality contributions** over time
- **Deep understanding** of the codebase
- **Good judgment** in code review and design decisions
- **Positive community engagement** (helping others, respectful communication)
- **Reliability** and responsiveness to project needs

### Process for Adding Maintainers

1. An existing maintainer proposes a contributor for the maintainer role
2. The proposal is discussed among current maintainers
3. Current maintainers reach consensus on the decision
4. If approved, the new maintainer is granted appropriate repository permissions
5. Their name is added to this file

## Maintainer Responsibilities

Maintainers are expected to:

- **Review PRs** in a timely manner (best effort within 1 week)
- **Triage issues** and respond to bug reports
- **Maintain code quality** through thoughtful review
- **Follow the [Code of Conduct](CODE_OF_CONDUCT.md)** and enforce it fairly
- **Communicate openly** about project decisions
- **Step back gracefully** when unable to fulfill responsibilities

## Emeritus Maintainers

Maintainers who are no longer active but contributed significantly to the project will be listed here.

_(No emeritus maintainers yet)_

## Governance

### Decision Making

This project follows a **benevolent dictator** model for now, with Fernando as the primary decision-maker. As the maintainer team grows, we will transition to a **consensus-seeking** model where major decisions require agreement among active maintainers.

### Types of Decisions

| Decision Type | Approval Needed |
|---------------|-----------------|
| Bug fixes | Maintainer review |
| New features | Maintainer review + design discussion |
| Breaking changes | Discussion + clear migration path |
| Governance changes | Consensus of all maintainers |
| Security fixes | Expedited review, coordinated disclosure |

### Conflict Resolution

If maintainers disagree on a decision:

1. **Discussion first:** Open discussion in the relevant issue or PR
2. **Seek consensus:** Aim for agreement through compromise
3. **Defer to primary maintainer:** If consensus isn't reached, the primary maintainer makes the final call
4. **Document the rationale:** Record the decision and reasoning for future reference

## Roadmap

The project roadmap is maintained through GitHub Issues and Discussions. Major upcoming work is tracked via:

- **Issues** with milestone assignments
- **GitHub Projects** (when applicable)
- **CHANGELOG.md** for completed work

## Communication

### Public Channels

- **Issues:** Bug reports, feature requests, questions
- **Pull Requests:** Code review, technical discussion
- **Discussions:** General questions, ideas, community chat

### Private Channels

- **Security reports:** See [SECURITY.md](SECURITY.md)
- **Code of Conduct violations:** fernando.romerogalvan@gmail.com

## Project Origin and History

`inundation` is a Python translation of the original [R package](https://github.com/goertler/inundation) created by:

- **Jeanette Clark** - Original R package author
- **Pascale A.L. Goertler** - Original R package author and scientific lead

The Python translation was created by Fernando E. Romero Galvan at the California Department of Water Resources, with assistance from AI code generation (Anthropic Claude). See [NOTICE.md](NOTICE.md) for full attribution.

## Acknowledgments

We thank all contributors, past and present, who have helped shape this project. See the [GitHub contributors page](https://github.com/ferg-dwr/inundation/graphs/contributors) for a complete list of contributors.

---

**Last updated:** May 2026
