#!/usr/bin/env bash
# One-time Google Cloud setup for the liquidation app.
# Usage: ./scripts/setup-gcp.sh <PROJECT_ID> <GITHUB_OWNER/REPO>
# Run in Cloud Shell or anywhere gcloud is logged in as a project owner.
set -euo pipefail

PROJECT_ID="${1:?Project ID required}"
GITHUB_REPO="${2:?GitHub repo (owner/name) required}"
PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
DEPLOYER="deployer@${PROJECT_ID}.iam.gserviceaccount.com"
RUNTIME="app-runtime@${PROJECT_ID}.iam.gserviceaccount.com"
COMPUTE="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud config set project "$PROJECT_ID"

echo "Enabling APIs..."
gcloud services enable \
  cloudfunctions.googleapis.com run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com iam.googleapis.com iamcredentials.googleapis.com \
  sts.googleapis.com firebasehosting.googleapis.com serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com sheets.googleapis.com

echo "Creating service accounts..."
gcloud iam service-accounts create deployer --display-name="GitHub deployer" || true
gcloud iam service-accounts create app-runtime --display-name="App runtime" || true

echo "Waiting for the new service accounts to be ready..."
for SA in "$DEPLOYER" "$RUNTIME"; do
  until gcloud iam service-accounts describe "$SA" >/dev/null 2>&1; do sleep 5; done
done
sleep 15   # IAM needs a little longer than describe to see new accounts

echo "Granting deployer roles..."
for ROLE in roles/cloudfunctions.developer roles/run.admin roles/iam.serviceAccountUser \
            roles/firebasehosting.admin roles/serviceusage.serviceUsageConsumer; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$DEPLOYER" --role="$ROLE" --condition=None >/dev/null
done

echo "Letting Cloud Build use the default compute account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$COMPUTE" --role=roles/cloudbuild.builds.builder --condition=None >/dev/null

echo "Setting up keyless auth for GitHub Actions..."
gcloud iam workload-identity-pools create github --location=global --display-name="GitHub" || true
gcloud iam workload-identity-pools providers create-oidc github-repo \
  --location=global --workload-identity-pool=github \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='${GITHUB_REPO}'" || true
gcloud iam service-accounts add-iam-policy-binding "$DEPLOYER" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/attribute.repository/${GITHUB_REPO}" >/dev/null

echo
echo "Done. Add these as GitHub repository variables (Settings > Secrets and variables > Actions > Variables):"
echo "  GCP_PROJECT_ID = $PROJECT_ID"
echo "  WIF_PROVIDER   = projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/providers/github-repo"
echo "  DEPLOYER_SA    = $DEPLOYER"
echo "  RUNTIME_SA     = $RUNTIME"
