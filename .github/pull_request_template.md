<!--
Thanks for contributing! Fill in every section. Keep it short and specific:
reviewers read the "Why" and "Testing" sections first.
-->

## What

<!-- What changed? Bullet points, one per logical change. Reference the module(s). -->

-

## Why

<!--
Why is this change needed? Link the issue, describe the user/engineering problem,
and note any alternative you rejected.
-->

Closes #

## How

<!--
How was it implemented? Call out design decisions, config/schema changes, and
anything a reviewer should look at closely. Note the risk of the change.
-->

-

## Testing

<!--
How did you verify it? Paste the commands and their result. Include new/updated
tests and any manual checks (video, endpoint, container).
-->

| Command / check | Result |
| --------------- | ------ |
| `make lint` |  |
| `make typecheck` |  |
| `make test` |  |

## Checklist

- [ ] Branch is named `type/<issue>-short-desc` and targets `main`
- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] `Closes #<issue>` is linked above
- [ ] Tests added or updated for the change (regression test for bug fixes)
- [ ] `make lint`, `make typecheck` and `make test` pass locally
- [ ] No data, model weights, runs or `.env` files committed (see `.gitignore`)
- [ ] DVC pointer changes are backed up and verified, if applicable
- [ ] No secrets, credentials or personal data in code, logs, tests or docs
- [ ] Configs in `configs/` and docs updated if behaviour or defaults changed
- [ ] `CHANGELOG`/model card/dataset registry updated when relevant
- [ ] Breaking changes are marked with `BREAKING CHANGE:` in the commit footer
