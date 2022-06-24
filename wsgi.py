"""This is my docstring."""
import os
from spiffworkflow_backend import create_app
from spiffworkflow_backend.services.acceptance_test_fixtures import load_fixtures

app = create_app()

if os.environ.get("SPIFFWORKFLOW_BACKEND_LOAD_FIXTURE_DATA") == "true":
    with app.app_context():
        load_fixtures()
