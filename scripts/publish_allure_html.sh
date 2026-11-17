#!/usr/bin/env bash
# Publish the packed HTML under the original test run and attempt.
set -euo pipefail
: "${REPORT_BASE:?Allure host is missing}" "${UPLOAD_PASSWORD:?Allure upload password is missing}"
[[ "$REPORT_RUN_ID" =~ ^[1-9][0-9]*$ && "$REPORT_ATTEMPT" =~ ^[1-9][0-9]*$ ]]
[[ -s "$1" ]]
file="${REPORT_RUN_ID}-${REPORT_ATTEMPT}.html"
base="${REPORT_BASE%/}"
status=$(curl --proto '=https' --silent --show-error --fail --retry 2 \
  --output /dev/null --write-out '%{http_code}' --user "ci:${UPLOAD_PASSWORD}" \
  --upload-file "$1" "${base}/upload/${file}")
case "$status" in
  201|204) ;;
  *) echo "Unexpected Allure upload status: $status" >&2; exit 1 ;;
esac
echo "url=${base}/${file}" >> "$GITHUB_OUTPUT"
echo "[Allure hisobotini ochish](${base}/${file})" >> "$GITHUB_STEP_SUMMARY"
