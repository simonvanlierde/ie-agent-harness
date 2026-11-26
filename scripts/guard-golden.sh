#!/bin/sh
# Refuse a commit that changes tests/golden/ unless a person approved it:
# either GOLDEN_APPROVED=1 in the environment, or an "Approved-by:" trailer
# in the commit message. Runs as a commit-msg hook; $1 is the message file.
changed=$(git diff --cached --name-only -- tests/golden/)
[ -z "$changed" ] && exit 0
[ "$GOLDEN_APPROVED" = "1" ] && exit 0
grep -qE '^Approved-by: .+' "$1" && exit 0
echo "Refused: this commit changes the golden tests:" >&2
echo "$changed" | sed 's/^/  /' >&2
echo "A person must approve. Set GOLDEN_APPROVED=1 or add an 'Approved-by: Name' trailer." >&2
exit 1
