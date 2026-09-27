#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${TASK_WORKSPACE:-/workspace}"
git apply --binary "$here/fix.patch"
