"""Health check function: proves the deploy pipeline works end to end."""
import os

import functions_framework


@functions_framework.http
def health(request):
    return {
        "status": "ok",
        "version": os.environ.get("APP_VERSION", "dev"),
    }, 200
