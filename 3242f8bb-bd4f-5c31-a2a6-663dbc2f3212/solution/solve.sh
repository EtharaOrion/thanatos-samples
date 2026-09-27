#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "${THANATOS_WORKSPACE:-/workspace}"
git apply --check "$HERE/fix.patch"
git apply "$HERE/fix.patch"
