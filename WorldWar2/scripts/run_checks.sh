#!/bin/bash
# Full verification set for the WWII unit-locations dataset. Read-only (writes only /tmp).
# Usage: scripts/run_checks.sh [WORKING_COPY_DIR]   (default: the WorldWar2 directory holding this script)
# Exit status: 0 only if every step passes; otherwise 1, with the failing steps listed at the end.
set -u -o pipefail
D=${1:-$(cd "$(dirname "$0")/.." && pwd)}
cd "$D" || exit 1
FAILED=()
step() {  # step NAME FILTER CMD...: run CMD, show its output through FILTER, record a non-zero exit of CMD
    local name=$1 filter=$2; shift 2
    local out; out=$(mktemp)
    "$@" > "$out" 2>&1; local rc=$?
    eval "$filter" < "$out"
    rm -f "$out"
    if [ $rc -ne 0 ]; then FAILED+=("$name (exit $rc)"); echo "FAILED: $name (exit $rc)"; fi
}
step validate 'grep -E "^OK|ERROR|warning\(s\)" || true' python3 scripts/validate.py
step check_json_fields 'tail -1' python3 scripts/check_json_fields.py
step semantic_tests 'tail -1' python3 scripts/semantic_tests.py
step test_renumber_new_ids 'tail -1' python3 scripts/test_renumber_new_ids.py
step test_renumber_new_ids_stress 'tail -1' python3 scripts/test_renumber_new_ids_stress.py
step build_check 'tail -1' python3 scripts/build.py --check   # includes build/oob/ flagship snapshots and other generated files
step build_references_check 'tail -1' python3 scripts/build_references.py --check
step review_sample_check 'cat' python3 scripts/review_sample.py --check
step check_coordinates 'tail -1' python3 scripts/check_coordinates.py
step audit_command_location 'tail -1' python3 scripts/audit_command_location.py
step audit_temporal_relationships 'tail -1' python3 scripts/audit_temporal_relationships.py
if git rev-parse --verify -q origin/main >/dev/null; then
    step check_claim_ids 'tail -2' python3 scripts/check_claim_ids.py
    step check_mission_ids 'tail -2' python3 scripts/check_mission_ids.py
    step check_commander_ids 'tail -3' python3 scripts/check_commander_ids.py
    step check_other_ids 'cat' python3 scripts/check_other_ids.py
else
    echo "(check_claim_ids, check_mission_ids, check_commander_ids and check_other_ids skipped: origin/main not available)"
fi
if [ ${#FAILED[@]} -ne 0 ]; then
    echo "CHECKS FAILED: ${FAILED[*]}"; exit 1
fi
echo "ALL CHECKS PASSED"
