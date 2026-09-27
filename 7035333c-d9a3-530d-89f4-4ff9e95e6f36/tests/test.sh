#!/usr/bin/env bash
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
logs="${ASSAY_LOG_DIR:-/logs/verifier}"
mkdir -p "$logs"
printf '{"score":null,"reward":0.0,"graded":false,"status":"ungraded"}\n' > "$logs/reward.json"
cp "$logs/reward.json" "$logs/score.json"
printf '0.0\n' > "$logs/reward.txt"
# --- rubric grader (separate scores; it never changes reward or score) -------------------------------
# Keep the judge key out of the environment the tests run in: it goes to a root-only file, and the
# variable is removed before any delivered code executes.
mkdir -p /tmp/rubric-grader && chmod 700 /tmp/rubric-grader
( umask 077; printf '%s' "${RUBRIC_JUDGE_API_KEY:-${OPENAI_API_KEY:-}}" > /tmp/rubric-grader/judge.key )
unset RUBRIC_JUDGE_API_KEY OPENAI_API_KEY
# Snapshot the delivery before the tests run, so the rubric reviews exactly what the agent delivered.
if [ "${RUBRIC_GRADER:-1}" != "0" ] && [ -f /opt/grader/rubric_grader.py ]; then
  RUBRIC_TESTS_DIR="$here" timeout -k 10 900 python3 -I /opt/grader/rubric_grader.py snapshot > "$logs/rubric-grader-stdout.txt" 2>&1 || true
fi
export PYTHONDONTWRITEBYTECODE=1
python3 -I "$here/score_tests.py" > "$logs/verifier-output.txt" 2>&1
# The test reward is final here. Keep it byte for byte, run the rubric, then write reward.json with the
# test reward unchanged plus the rubric scores that were measured (finalize restores this record on any fault).
cp "$logs/reward.json" "$logs/reward.tests.json"
if [ "${RUBRIC_GRADER:-1}" != "0" ] && [ -d /tmp/rubric-grader/delivered ]; then
  RUBRIC_TESTS_DIR="$here" timeout -k 30 3600 python3 -I /opt/grader/rubric_grader.py judge >> "$logs/rubric-grader-stdout.txt" 2>&1 || true
fi
RUBRIC_TESTS_DIR="$here" python3 -I /opt/grader/rubric_grader.py finalize >> "$logs/rubric-grader-stdout.txt" 2>&1 || cp "$logs/reward.tests.json" "$logs/reward.json"
rm -rf /tmp/rubric-grader
exit 0
