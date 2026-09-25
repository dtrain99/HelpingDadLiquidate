"""Health check: confirms the backend is running and which commit is deployed."""
import os

import functions_framework


@functions_framework.http
def health(request):
    return {"status": "ok", "version": os.environ.get("APP_VERSION", "dev")}, 200
