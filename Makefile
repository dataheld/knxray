FLAKE_ITER := https://flakehub.com/f/DeterminateSystems/flake-iter/*
SYSTEM     := $(shell nix eval --raw --impure --expr builtins.currentSystem)

# Fast evaluation-only check (does not build most derivations)
.PHONY: check
check:
	nix flake check

# Exact equivalent of the DeterminateSystems CI build step for the current system
.PHONY: ci-build
ci-build:
	FLAKE_ITER_NIX_SYSTEM=$(SYSTEM) nix run "$(FLAKE_ITER)" -- --verbose build
