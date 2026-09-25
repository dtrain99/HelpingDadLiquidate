"""Sign-in: /api/auth/me, /api/auth/login, /api/auth/logout.

The browser gets a Google ID token from the Sign in with Google button and posts it to /login.
We verify it, check the Family tab, and set the __session cookie.
"""
import os
import traceback

import functions_framework
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

import family
import session

NO_STORE = {"Cache-Control": "private, no-store"}


@functions_framework.http
def auth(request):
    path = request.path.rstrip("/")
    try:
        if path.endswith("/me") and request.method == "GET":
            return _me(request)
        if path.endswith("/login") and request.method == "POST":
            return _login(request)
        if path.endswith("/logout") and request.method == "POST":
            return _logout()
        return {"error": "not found"}, 404, NO_STORE
    except Exception:
        traceback.print_exc()
        return {"error": "server error"}, 500, NO_STORE


def _me(request):
    user = session.current_user(request)
    if user and family.is_family(user["email"]):
        return {"signedIn": True, "user": user}, 200, NO_STORE
    return {"signedIn": False, "clientId": os.environ["GOOGLE_CLIENT_ID"]}, 200, NO_STORE


def _login(request):
    body = request.get_json(silent=True) or {}
    token = body.get("credential")
    if not token:
        return {"error": "missing credential"}, 400, NO_STORE
    try:
        claims = id_token.verify_oauth2_token(
            token, google_requests.Request(), os.environ["GOOGLE_CLIENT_ID"]
        )
    except ValueError:
        return {"error": "invalid sign-in token"}, 401, NO_STORE

    email = (claims.get("email") or "").lower()
    if not claims.get("email_verified") or not family.is_family(email):
        return {"error": "not on family list", "email": email}, 403, NO_STORE

    user = {"email": email, "name": claims.get("name") or email}
    headers = {**NO_STORE, "Set-Cookie": session.make_cookie(user)}
    return {"signedIn": True, "user": user}, 200, headers


def _logout():
    headers = {**NO_STORE, "Set-Cookie": session.clear_cookie()}
    return {"signedIn": False}, 200, headers
