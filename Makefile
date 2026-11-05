# Regenerate the git-diff example in README.md from the test snapshot.
# Run this before committing whenever test fixtures change.
.PHONY: docs
docs:
	nk python-test tests/test_knxray.py::test_git_diff_textconv_snapshot --snapshot-update -q
	python scripts/update_readme.py

# Run working-tree checks.
.PHONY: check
check:
	nk all

# Run sandboxed flake checks.
.PHONY: ci-build
ci-build:
	nk flake-check
