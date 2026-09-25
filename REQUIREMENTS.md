# Requirements

The requirements we build and validate against. Each has an ID so commits, tests, and
conversations can refer to it. Status: Done, In progress, Planned, or Later.

## Guiding principles

| ID | Principle |
|---|---|
| P-1 | Simple is better. Prefer the fewest moving parts that meet the need. |
| P-2 | Modular architecture: each backend capability is its own function; each front-end page is its own file. |
| P-3 | Serverless: no servers to manage; everything scales to zero when unused. |
| P-4 | CI/CD from GitHub: every push to `main` deploys automatically. |
| P-5 | The front end manages session state with a cookie. |
| P-6 | Iterative and incremental: small, deployable, testable increments. |
| P-7 | Keep running costs at or near zero by staying within free allowances. |

## Functional requirements

### Phase 1: capture and catalog

| ID | Requirement | How we validate | Status |
|---|---|---|---|
| F-1.0 | Every push to `main` deploys the app automatically, and the page shows the deployed version. | Page footer shows the latest commit code. | Done |
| F-1.1 | The app runs in a phone browser and can be added to the home screen. | Open on iPhone and Android; add to home screen; it launches. | Planned |
| F-1.2 | Family members sign in with their Google account, stay signed in for 30 days, and can sign out. | Sign in on a phone and a laptop; reload and remain signed in; sign out. | In progress |
| F-1.3 | Only people listed in the Master Inventory "Family" tab can use the app. Removing someone takes effect within a minute, even if they're signed in. | A listed email gets in; an unlisted one sees an access message; removing a signed-in person signs them out on reload. | In progress |
| F-1.7 | The app has a privacy page, linked from the main page, describing what's collected and how it's used. Required to publish the Google sign-in app. | `/privacy.html` loads and is linked from the footer. | In progress |
| F-1.4 | A user can take a photo of an item with the phone camera and upload it. | Photo appears in the Cloud Storage bucket. | Planned |
| F-1.5 | Saving an item adds a row to the Items tab of the Master Inventory with a visible photo thumbnail. | Row appears with thumbnail, name, notes, who added it, and date. | Planned |
| F-1.6 | Each item has a status: Available, Pending, or Sold. | Status column present; defaults to Available. | Planned |

### Phase 2: research and listings

| ID | Requirement | How we validate | Status |
|---|---|---|---|
| F-2.1 | The app identifies the item from its photo. | Suggested name and category are reasonable for a sample of items. | Planned |
| F-2.2 | The app researches market value and records an estimated value and research summary. | Items tab shows estimate and summary. | Planned |
| F-2.3 | The app writes a title and description optimized for each of Craigslist, Facebook Marketplace, and eBay, stored in the "Listings" tab (one row per item per platform). | Three Listings rows per item; eBay titles are 80 characters or fewer. | Planned |
| F-2.4 | Each item has a page in the web app showing its photo, value, and each platform's listing text with a Copy button. | Copy button places text on the clipboard on phone and laptop. | Planned |
| F-2.5 | Each Items row links to that item's page. | Link opens the item page. | Planned |
| F-2.6 | The web app has an inventory list page that works on phones and laptops. | Browse items on both. | Planned |
| F-2.7 | The app captures eBay-ready fields: category, condition, and item specifics. | Fields present in Items tab. | Planned |
| F-2.8 | Each item has a "Can ship" choice, defaulting to local pickup; shippable items record approximate weight and box size (AI may suggest them). | Toggle and fields present; suggestions appear. | Planned |

### Phase 3: comparables and review

| ID | Requirement | How we validate | Status |
|---|---|---|---|
| F-3.1 | Research includes comparable items found online, recorded in the Items tab. | Comparables column populated with links. | Planned |
| F-3.2 | A user can review and edit the AI's results before saving. | Edited values are what land in the sheet. | Planned |

### Phase 4 and later

| ID | Requirement | Status |
|---|---|---|
| F-4.1 | Automatically create eBay listings through eBay's official API, with the user connecting their eBay account via OAuth. | Later |
| F-5.1 | Specialized selling channels for items such as jewelry. | Later |

## Technical requirements and decisions

| ID | Decision |
|---|---|
| T-1 | Front end: plain HTML, CSS, and JavaScript with no build step, hosted on Firebase Hosting. |
| T-2 | Backend: Python Cloud Run functions in `us-central1`, one per module, reached at `/api/<name>` via Firebase Hosting rewrites (same domain as the web app). All functions share one source folder (`functions/`) with a separate entry point each, so shared modules are written once. |
| T-3 | Session cookie is named `__session` (the only cookie Firebase Hosting forwards), HttpOnly, Secure, SameSite=Lax, signed, and valid for 30 days. |
| T-4 | Sign-in: the Sign in with Google button (Google Identity Services) returns an ID token, which the browser posts to `/api/auth/login`; the backend verifies it (signature, audience, expiry, verified email) and checks the Family tab. |
| T-5 | The backend accesses the sheet and storage as a dedicated runtime service account; users never grant Drive access. |
| T-6 | Photos are stored in a Cloud Storage bucket, publicly readable under random, unguessable file names, so `=IMAGE()` thumbnails work in the sheet. |
| T-7 | The Master Inventory Google Sheet is the source of truth. Tabs: Items, Listings, Family. |
| T-8 | GitHub Actions deploys using Workload Identity Federation; no service account keys are stored anywhere. |
| T-9 | Cost guards: function max instances capped, old build images cleaned up, and a billing budget alert set. Endpoints that call paid APIs require a signed-in family member. |
| T-10 | All code and documentation live in https://github.com/dtrain99/HelpingDadLiquidate. |
| T-11 | The cookie-signing key is a GitHub Actions secret (`SESSION_SECRET`) passed to the functions as an environment variable. Changing it signs everyone out. (Alternative considered: Google Secret Manager.) |
| T-13 | The Google sign-in app is published (External, production) with homepage `https://helping-dad-liquidate.web.app` and privacy policy `https://helping-dad-liquidate.web.app/privacy.html`, so anyone on the Family tab can sign in without also being a test user. |
| T-12 | Configuration lives in GitHub repository variables: `GCP_PROJECT_ID`, `WIF_PROVIDER`, `DEPLOYER_SA`, `RUNTIME_SA`, `GOOGLE_CLIENT_ID`, `SHEET_ID`. |

## Constraints and known limitations

| ID | Note |
|---|---|
| C-1 | Only eBay offers an official API for listing data. Craigslist and Facebook Marketplace have no public API and prohibit scraping, so their prices inform estimates only through general web research. |
| C-2 | Google Sheets cannot host buttons inside cells, which is why Copy buttons live on the item page (F-2.4). |
