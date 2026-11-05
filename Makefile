# Regenerate the git-diff example in README.md from the test snapshot.
# Run this before committing whenever test fixtures change.
.PHONY: docs
docs:
	python -m pytest tests/test_knxray.py::test_git_diff_textconv_snapshot --snapshot-update -q
	python scripts/update_readme.py
