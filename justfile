# Run every check CI runs.
check:
    uv run ruff check
    uv run ruff format --check
    uv run pytest
    uv run pytest --noconftest -o addopts= tests/golden
