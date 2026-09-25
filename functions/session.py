"""Signed session cookie.

Firebase Hosting forwards only one cookie to backend functions, and it must be named __session.
"""
import os

from itsdangerous import BadSignature, URLSafeTimedSerializer

COOKIE_NAME = "__session"
MAX_AGE_SECONDS = 30 * 24 * 60 * 60  # 30 days
_ATTRIBUTES = "Path=/; HttpOnly; Secure; SameSite=Lax"


def _serializer():
    return URLSafeTimedSerializer(os.environ["SESSION_SECRET"], salt="session-v1")


def make_cookie(user):
    value = _serializer().dumps(user)
    return f"{COOKIE_NAME}={value}; Max-Age={MAX_AGE_SECONDS}; {_ATTRIBUTES}"


def clear_cookie():
    return f"{COOKIE_NAME}=; Max-Age=0; {_ATTRIBUTES}"


def current_user(request):
    """Returns {"email", "name"} from a valid, unexpired cookie, or None."""
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return None
    try:
        return _serializer().loads(raw, max_age=MAX_AGE_SECONDS)
    except BadSignature:  # also covers expired cookies
        return None
