FLAKE_ITER := https://flakehub.com/f/DeterminateSystems/flake-iter/*
SYSTEM     := $(shell nix eval --raw --impure --expr builtins.currentSystem)

# Regenerate the git-diff example in README.md from the test snapshot.
# Run this before committing whenever test fixtures change.
.PHONY: docs
docs:
	python -m pytest tests/test_knxray.py::test_git_diff_textconv_snapshot --snapshot-update -q
	python scripts/update_readme.py

# Fast evaluation-only check (does not build most derivations)
.PHONY: check
check:
	nix flake check

# Exact equivalent of the DeterminateSystems CI build step for the current system
.PHONY: ci-build
ci-build:
	FLAKE_ITER_NIX_SYSTEM=$(SYSTEM) nix run "$(FLAKE_ITER)" -- --verbose build
