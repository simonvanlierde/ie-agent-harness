#!/bin/sh
# Refuse a commit that changes tests/golden/ unless a person approved it:
# either GOLDEN_APPROVED=1 in the environment, or an "Approved-by:" trailer
# in the commit message. Runs as a commit-msg hook; $1 is the message file.
changed=$(git diff --cached --name-only -- tests/golden/) || exit 1
[ -z "$changed" ] && exit 0
[ "$GOLDEN_APPROVED" = "1" ] && exit 0
grep -qE '^Approved-by: .+' "$1" && exit 0
echo "Refused: this commit changes the reference answer in tests/golden/:" >&2
echo "$changed" | sed 's/^/  /' >&2
echo "Stop and ask a person. Only they may approve it, with an 'Approved-by: <their name>' line in the commit message." >&2
exit 1
