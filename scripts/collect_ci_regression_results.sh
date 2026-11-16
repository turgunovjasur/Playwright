#!/usr/bin/env bash
# A hosted runner has a clean checkout and one Order run per workflow attempt.
set -euo pipefail
shopt -s nullglob
api=(test-results/api/allure-results/*-result.json)
runs=(test-results/runs/*/run.json)
if (( ${#runs[@]} > 1 )); then
  echo "Multiple Order runs in the same CI checkout" >&2
  exit 1
fi
# The parent pytest hooks may have written to the default results path.
# Build the published report exclusively from the two selected suites.
dest=test-results/api-regression-allure-results
mkdir -p "$dest"
if (( ${#api[@]} )); then
  cp -a test-results/api/allure-results/. "$dest/"
fi
if (( ${#runs[@]} )); then
  directory=${runs[0]%/run.json}
  source="$directory/allure-presentation-results"
  presented=("$source"/*-result.json)
  if (( ! ${#presented[@]} )); then source="$directory/allure-results"; fi
  if [[ -d "$source" ]]; then cp -a "$source/." "$dest/"; fi
fi
results=("$dest"/*-result.json)
(( ${#results[@]} )) || { echo "API/Order Allure results not found" >&2; exit 1; }
