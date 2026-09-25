# Helping Dad Liquidate

A phone-friendly web app for photographing, pricing, and tracking the items we're selling.

## Architecture

- **Web app** (`web/`): plain HTML, CSS, and JavaScript, no build step. Hosted on Firebase Hosting.
- **Functions** (`functions/`): Python Cloud Run functions, one per entry point in `main.py` (`health`, `auth`), reached at `/api/<name>` through Firebase Hosting rewrites, so everything shares one domain. Shared modules: `session.py` (cookie), `family.py` (allowlist).
- **State**: a first-party session cookie named `__session` (the only cookie Firebase Hosting forwards).
- **Data**: photos in Cloud Storage, items in the "Master Inventory" Google Sheet, family allowlist in its "Family" tab.
- **CI/CD**: GitHub Actions deploys on every push to `main`, using Workload Identity Federation (no stored keys).

Requirements and decisions are tracked in [REQUIREMENTS.md](REQUIREMENTS.md).

## Increment status

1. [x] Skeleton and pipeline (health check)
2. [x] Google sign-in, allowlist, session cookie
3. [ ] Photo capture and upload
4. [ ] Save item to Master Inventory

## One-time setup

1. **Create a Google Cloud project** at console.cloud.google.com and link a billing account.
2. **Add Firebase to it**: at console.firebase.google.com, choose "Add project" and pick the existing Google Cloud project. Then open Hosting and click "Get started" (you can skip the CLI steps it shows).
3. **Create the GitHub repo** and push this code to it.
4. **Run the setup script** in Cloud Shell (the terminal icon in the Cloud console), after uploading or cloning this repo there:
   ```
   ./scripts/setup-gcp.sh YOUR_PROJECT_ID dtrain99/HelpingDadLiquidate
   ```
5. **Add the four repository variables** the script prints to GitHub under Settings > Secrets and variables > Actions > Variables.
6. **Trigger a deploy**: push to `main`, or run the Deploy workflow manually from the Actions tab.
7. **Check it**: open `https://YOUR_PROJECT_ID.web.app`. You should see "Server is running (version abc1234)" matching your latest commit.
8. **Set the image cleanup policy** (once, after the first successful deploy):
   ```
   ./scripts/set-cleanup-policy.sh YOUR_PROJECT_ID
   ```

## Increment 2 setup (sign-in)

1. **Master Inventory sheet**: create a Google Sheet named "Master Inventory" with a tab named `Family` (column A Name, column B Email, header in row 1). Share it with `app-runtime@helping-dad-liquidate.iam.gserviceaccount.com` as Editor. The sheet ID is the part of its URL between `/d/` and `/edit`.
2. **Sheets API**: `gcloud services enable sheets.googleapis.com --project=helping-dad-liquidate`
3. **OAuth client**: in Google Auth Platform (console.cloud.google.com/auth), set up branding (External audience), add homepage `https://helping-dad-liquidate.web.app`, privacy policy `https://helping-dad-liquidate.web.app/privacy.html`, and authorized domain `helping-dad-liquidate.web.app`, then publish the app under Audience, and create a Web application client with authorized JavaScript origins `https://helping-dad-liquidate.web.app` and `https://helping-dad-liquidate.firebaseapp.com`. No redirect URIs or client secret are needed.
4. **GitHub**: add repository variables `GOOGLE_CLIENT_ID` and `SHEET_ID`, and a repository **secret** `SESSION_SECRET` (generate with `openssl rand -hex 32`).

## Troubleshooting

- *Sign-in says the server failed*: check the `auth` function's logs in Cloud Run. The usual causes are the sheet not being shared with the runtime service account, the Sheets API not enabled, or the tab not named exactly `Family`.

- *"allUsers" or public access errors when deploying the function*: your organization may have a policy blocking public services. Personal Gmail-based projects usually don't.
- *Page loads but says it can't reach the server*: the function deploy step probably failed; check the Actions log.
