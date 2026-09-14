# screenshots/

Screenshot-only pytest-playwright modules that render pages across viewports so you can look at them. This is **developer tooling, not a gate**: nothing here runs in CI, nothing here blocks a PR.

## Why a separate directory?

`pyproject.toml` sets `testpaths = ["tests"]`, so a plain `pytest` invocation never discovers this directory. These tests spin up a live server and a headless browser, so keeping them out of the default run keeps normal test runs fast.

## Running screenshot tests

```bash
poetry run pytest screenshots/
```

To regenerate screenshots for a specific module:

```bash
poetry run pytest screenshots/test_signup_screenshots.py
```

## Output

Generated screenshots are saved under `docs/_static/`, partitioned by viewport tier:

```
docs/_static/
├── desktop/    # 1440×900
└── mobile/     # 390×844
```

Output is gitignored and deliberately not committed. There is no automatic image comparison — you run these when you want to see how something looks, and you read the result yourself.

The guard against markup regressions is the rendered-HTML contract tests under `tests/`, which assert the semantic structure and DaisyUI classes each element emits. Those run in CI and do block a PR. See Article XII of `CONSTITUTION.md` for why pixel-diffing was weighed and declined.

## Contents

| File | Page | Permutations |
|------|------|-------------|
| `test_signup_screenshots.py` | Signup page (`/account-center/signup/`) and passkey signup page (`/account-center/signup/passkey/`) | 6 settings permutations × 2 viewports = 12 files |
