# Security Policy

## Supported versions

SafeSite Vision is pre-1.0. Security fixes land on the latest release only.

| Version | Supported |
| ------- | --------- |
| `0.1.x` (latest) | ✅ |
| older | ❌ |

## Reporting a vulnerability

**Do not open a public issue, discussion or pull request for a security problem.**

Use GitHub's private vulnerability reporting:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability** (GitHub Security Advisories).
3. Describe the issue with reproduction steps, affected version/commit, and impact.

If private reporting is unavailable to you, contact a maintainer privately through GitHub
(the maintainers are listed in [`README.md`](README.md#contributors) and
[`CODEOWNERS`](.github/CODEOWNERS)) and ask for a private channel before sharing details.

Please include:

- The affected component (`src/safesite/**`, `app/**`, a workflow, or the container image)
- Version, commit SHA, OS and Python version
- Reproduction steps or a proof of concept
- The impact you believe it has (data exposure, RCE, DoS, supply chain, ...)
- Whether the issue is already public anywhere

## What to expect

| Stage | Target |
| ----- | ------ |
| Acknowledgement of the report | within 3 business days |
| Initial triage and severity assessment | within 7 days |
| Fix or mitigation plan communicated | within 14 days |
| Public disclosure (coordinated with you) | after a fix is released, typically within 90 days |

We will credit you in the advisory unless you ask us not to.

## Scope

In scope:

- The Python package in `src/safesite/`
- The FastAPI service and Streamlit demo in `app/`
- CI/CD workflows and container image published to `ghcr.io`
- Dependency and supply-chain issues that this project can mitigate

Out of scope:

- Vulnerabilities in upstream dependencies without a project-level mitigation (report them
  upstream — e.g. [Ultralytics](https://github.com/ultralytics/ultralytics))
- Issues that require a compromised developer machine, or that only affect unsupported
  versions
- Findings from automated scanners with no demonstrated impact
- Social engineering and physical access

## Handling data and model artefacts

Video frames can contain identifiable people. When reporting an issue:

- Never attach real site footage, personal data, or production credentials.
- Reproduce with synthetic frames or blurred, consented samples.
- Model weights and datasets are distributed as release assets, not in the repository; see
  [`docs/datasets.md`](docs/datasets.md) for licences and provenance.

## Safe harbour

We will not pursue legal action against researchers who act in good faith, stay within
this policy, avoid privacy violations and service disruption, and give us reasonable time
to fix the issue before disclosure.
