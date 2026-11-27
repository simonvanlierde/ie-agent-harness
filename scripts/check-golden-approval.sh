#!/bin/sh
# CI copy of guard-golden.sh, which --no-verify or GOLDEN_APPROVED=1 skips locally.
# Fails when the commits in BASE..HEAD change tests/golden/ and none of them carries an
# "Approved-by:" trailer. Usage: check-golden-approval.sh BASE HEAD
base=$1
head=$2
changed=$(git diff --name-only "$base...$head" -- tests/golden/)
[ -z "$changed" ] && exit 0
git log --format=%B "$base..$head" | grep -qE '^Approved-by: .+' && exit 0
echo "Refused: this pull request changes the golden tests:" >&2
echo "$changed" | sed 's/^/  /' >&2
echo "A person must approve. Add an 'Approved-by: Name' trailer to one of its commits." >&2
exit 1
