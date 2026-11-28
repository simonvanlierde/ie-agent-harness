import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "check-golden-approval.sh"
# Ignore the user's git config (signing, hooks) so the test runs the same everywhere.
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.org",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.org",
}


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, env=ENV, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "tests" / "golden").mkdir(parents=True)
    (tmp_path / "tests" / "golden" / "x").write_text("211.4\n")
    (tmp_path / "notes").write_text("a\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "base")
    return tmp_path


def check(repo):
    return subprocess.run(
        ["sh", str(SCRIPT), "HEAD~1", "HEAD"], cwd=repo, env=ENV, capture_output=True
    ).returncode


def test_no_golden_change_passes(repo):
    (repo / "notes").write_text("b\n")
    git(repo, "commit", "-qam", "edit notes")
    assert check(repo) == 0


def test_golden_change_without_trailer_fails(repo):
    (repo / "tests" / "golden" / "x").write_text("178.64\n")
    git(repo, "commit", "-qam", "change golden")
    assert check(repo) == 1


def test_golden_change_with_trailer_passes(repo):
    (repo / "tests" / "golden" / "x").write_text("178.64\n")
    git(repo, "commit", "-qam", "change golden\n\nApproved-by: Ada")
    assert check(repo) == 0


def test_golden_file_moved_out_without_trailer_fails(repo):
    (repo / "other").mkdir()
    git(repo, "mv", "tests/golden/x", "other/x")
    git(repo, "commit", "-qm", "move golden")
    assert check(repo) == 1


def test_unknown_base_fails(repo):
    result = subprocess.run(
        ["sh", str(SCRIPT), "deadbeef", "HEAD"], cwd=repo, env=ENV, capture_output=True
    )
    assert result.returncode != 0


def test_missing_arguments_fail(repo):
    result = subprocess.run(["sh", str(SCRIPT)], cwd=repo, env=ENV, capture_output=True)
    assert result.returncode != 0


GUARD = Path(__file__).parents[1] / "scripts" / "guard-golden.sh"


def guard(repo, message):
    msg = repo / ".git" / "MSG"
    msg.write_text(message)
    env = {k: v for k, v in ENV.items() if k != "GOLDEN_APPROVED"}
    return subprocess.run(
        ["sh", str(GUARD), str(msg)], cwd=repo, env=env, capture_output=True
    ).returncode


def test_guard_refuses_staged_golden_change(repo):
    (repo / "tests" / "golden" / "x").write_text("178.64\n")
    git(repo, "add", ".")
    assert guard(repo, "change golden\n") == 1
    assert guard(repo, "change golden\n\nApproved-by: Ada\n") == 0


def test_guard_ignores_other_changes(repo):
    (repo / "notes").write_text("b\n")
    git(repo, "add", ".")
    assert guard(repo, "edit notes\n") == 0
