"""Fixtures shared by every jobboards test module."""
import pytest

from jobboards import http
from helpers import fake_network


@pytest.fixture
def network(monkeypatch):
    """Install a fake network for the test; returns the fake so tests can
    inspect `.calls`. Usage: `fake = network({"url-fragment": "fixture.json"})`."""
    def install(responses: dict):
        fake = fake_network(responses)
        monkeypatch.setattr(http, "request", fake)
        return fake
    return install
