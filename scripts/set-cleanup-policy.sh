#!/usr/bin/env bash
# Run once, after the first successful deploy (the image repository is created by that deploy).
# Deletes old function images so storage stays within the free allowance.
# Usage: ./scripts/set-cleanup-policy.sh <PROJECT_ID>
set -euo pipefail
PROJECT_ID="${1:?Project ID required}"

cat > /tmp/cleanup-policy.json <<'JSON'
[
  {"name": "keep-latest", "action": {"type": "Keep"}, "mostRecentVersions": {"keepCount": 2}},
  {"name": "delete-old", "action": {"type": "Delete"}, "condition": {"olderThan": "7d"}}
]
JSON

gcloud artifacts repositories set-cleanup-policies gcf-artifacts \
  --project="$PROJECT_ID" --location=us-central1 \
  --policy=/tmp/cleanup-policy.json --no-dry-run
echo "Cleanup policy set."
