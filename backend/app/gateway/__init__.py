"""Gateway module -- FastAPI routers, auth dependencies, the only browser-facing layer.

Future service: `api_gateway`. It owns no domain data. Everything it returns comes from
another module's public functions, which is what lets Phase 9 replace those calls with
network hops without touching a route.
"""

from app.gateway.errors import install_error_handlers
from app.gateway.responses import JsonResponse
from app.gateway.routes import router

__all__ = ["JsonResponse", "install_error_handlers", "router"]
