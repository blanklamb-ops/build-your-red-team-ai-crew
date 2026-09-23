#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_dir"

python3 -m unittest discover -s tests -v

test "$(sed -n 's/^ics_enabled:[[:space:]]*//p' config/default.yaml)" = "false"
grep -q "Architecture" README.md
grep -q "Authorized use only" README.md
grep -q "Detection Recommendations" OPSEC_CARD.md
test "$(grep -c '^- ' OPSEC_CARD.md)" -ge 3
grep -q "Semgrep" scans/semgrep.txt
grep -q "ast-grep" scans/ast-grep.txt

acceptance_tmp=$(mktemp -d "${TMPDIR:-/tmp}/gophish-ics-acceptance.XXXXXX")
trap 'rm -rf -- "$acceptance_tmp"' EXIT HUP INT TERM
before_hash=$(python3 -c 'import hashlib, pathlib; print(hashlib.sha256(pathlib.Path("config/default.yaml").read_bytes()).hexdigest())')
printf 'ics_enabled: true\n' > "$acceptance_tmp/enabled.yaml"
python3 -m gophish_ics.cli generate \
  --campaign fixtures/campaign.json \
  --recipient-id recipient-001 \
  --output "$acceptance_tmp/invite.ics" \
  --config "$acceptance_tmp/enabled.yaml"
python3 -m gophish_ics.cli validate "$acceptance_tmp/invite.ics"
python3 -m gophish_ics.cli seed --db "$acceptance_tmp/rsvps.sqlite3" --fixture fixtures/rsvps.json
report=$(python3 -m gophish_ics.cli report --db "$acceptance_tmp/rsvps.sqlite3" --campaign-id lab-campaign-001 --json)
printf '%s\n' "$report" | grep -q '"accept": 1'
printf '%s\n' "$report" | grep -q '"decline": 1'
after_hash=$(python3 -c 'import hashlib, pathlib; print(hashlib.sha256(pathlib.Path("config/default.yaml").read_bytes()).hexdigest())')
test "$before_hash" = "$after_hash"

printf '%s\n' "All A1-A10 and M1-M3 acceptance checks passed."
