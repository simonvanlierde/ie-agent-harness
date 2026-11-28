#!/bin/sh
# CI copy of guard-golden.sh, which --no-verify or GOLDEN_APPROVED=1 skips locally.
# Fails when the commits in BASE..HEAD change tests/golden/ and none of them carries an
# "Approved-by:" trailer. Usage: check-golden-approval.sh BASE HEAD
if [ $# -ne 2 ]; then
	echo "usage: check-golden-approval.sh BASE HEAD" >&2
	exit 2
fi
base=$1
head=$2
# Fail closed: a shallow clone or a bad commit id must not look like "no change".
changed=$(git diff --name-only "$base...$head" -- tests/golden/) || {
	echo "Could not compare $base and $head. Check out the full history (fetch-depth: 0)." >&2
	exit 2
}
[ -z "$changed" ] && exit 0
git log --format=%B "$base..$head" | grep -qE '^Approved-by: .+' && exit 0
echo "Refused: this pull request changes the reference answer in tests/golden/:" >&2
echo "$changed" | sed 's/^/  /' >&2
echo "Stop and ask a person. Only they may approve it, with an 'Approved-by: <their name>' line in one of its commits." >&2
exit 1
