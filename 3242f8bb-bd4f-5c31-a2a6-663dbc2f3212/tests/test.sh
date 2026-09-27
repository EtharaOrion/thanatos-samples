#!/usr/bin/env bash
set -uo pipefail
LOGS="${ASSAY_LOG_DIR:-/logs/verifier}"
TESTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$LOGS"
printf '{"score":null,"reward":0.0,"graded":false,"status":"ungraded"}\n' > "$LOGS/reward.json"
cp "$LOGS/reward.json" "$LOGS/score.json"
# --- rubric grader (separate scores; it never changes reward or score) -------------------------------
# Keep the judge key out of the environment the tests run in: it goes to a root-only file, and the
# variable is removed before any delivered code executes.
mkdir -p /tmp/rubric-grader && chmod 700 /tmp/rubric-grader
( umask 077; printf '%s' "${RUBRIC_JUDGE_API_KEY:-${OPENAI_API_KEY:-}}" > /tmp/rubric-grader/judge.key )
unset RUBRIC_JUDGE_API_KEY OPENAI_API_KEY
# Snapshot the delivery before the tests run, so the rubric reviews exactly what the agent delivered.
if [ "${RUBRIC_GRADER:-1}" != "0" ] && [ -f /opt/grader/rubric_grader.py ]; then
  RUBRIC_TESTS_DIR="$TESTS" timeout -k 10 900 python3 -I /opt/grader/rubric_grader.py snapshot > "$LOGS/rubric-grader-stdout.txt" 2>&1 || true
fi
export PYTHONPATH="$TESTS"
export PYTHONSAFEPATH=1
export PYTHONDONTWRITEBYTECODE=1
python3 -P "$TESTS/score_tests.py" > "$LOGS/test-stdout.txt" 2>&1
# The test reward is final here. Keep it byte for byte, run the rubric, then write reward.json with the
# test reward unchanged plus the rubric scores that were measured (finalize restores this record on any fault).
cp "$LOGS/reward.json" "$LOGS/reward.tests.json"
if [ "${RUBRIC_GRADER:-1}" != "0" ] && [ -d /tmp/rubric-grader/delivered ]; then
  RUBRIC_TESTS_DIR="$TESTS" timeout -k 30 3600 python3 -I /opt/grader/rubric_grader.py judge >> "$LOGS/rubric-grader-stdout.txt" 2>&1 || true
fi
RUBRIC_TESTS_DIR="$TESTS" python3 -I /opt/grader/rubric_grader.py finalize >> "$LOGS/rubric-grader-stdout.txt" 2>&1 || cp "$LOGS/reward.tests.json" "$LOGS/reward.json"
rm -rf /tmp/rubric-grader
exit 0
