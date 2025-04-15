# app/api/routes/__init__.py

# Import route modules to make them available when importing the package
from . import business_data

# Create empty modules for compatibility with existing imports in main.py
# These will be implemented later
class DummyRouter:
    def include_router(self, router):
        pass

class DummyModule:
    router = DummyRouter()

auth = DummyModule()
businesses = DummyModule()
calls = DummyModule()
users = DummyModule()
twilio = DummyModule()