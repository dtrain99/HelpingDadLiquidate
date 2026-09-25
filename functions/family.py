"""The family allowlist, read from the Family tab of the Master Inventory sheet.

Family tab layout: column A = Name, column B = Email, with a header row.
The list is cached briefly, so adding or removing someone takes effect within a minute.
"""
import os
import time

import google.auth
from google.auth.transport.requests import AuthorizedSession

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
_CACHE_SECONDS = 60
_cache = {"at": 0.0, "emails": set()}
_http = None


def _sheets():
    global _http
    if _http is None:
        credentials, _ = google.auth.default(scopes=_SCOPES)
        _http = AuthorizedSession(credentials)
    return _http


def family_emails():
    if time.time() - _cache["at"] < _CACHE_SECONDS:
        return _cache["emails"]
    url = (
        "https://sheets.googleapis.com/v4/spreadsheets/"
        f"{os.environ['SHEET_ID']}/values/Family!A2:B"
    )
    response = _sheets().get(url, timeout=10)
    response.raise_for_status()
    rows = response.json().get("values", [])
    emails = {row[1].strip().lower() for row in rows if len(row) > 1 and row[1].strip()}
    _cache.update(at=time.time(), emails=emails)
    return emails


def is_family(email):
    return bool(email) and email.strip().lower() in family_emails()
