"""Guards on the provider registry itself."""
import pathlib
import re

import jobboards
from jobboards.provider import KIND_AGGREGATOR, KIND_ATS, KIND_PORTFOLIO

TESTS_DIR = pathlib.Path(__file__).resolve().parent


def test_every_provider_has_a_fixture_backed_test():
    """Adding a provider without a test is the failure mode this guards:
    the parser would rot silently the first time the source changed shape."""
    tested = set()
    for test_file in TESTS_DIR.glob("test_*.py"):
        tested |= set(re.findall(r"^def test_fetch_([a-z0-9]+)\(", test_file.read_text(), re.M))
    registered = {provider.key for provider in jobboards.PROVIDERS}
    assert registered <= tested, f"providers without a test_fetch_<key> test: {registered - tested}"


def test_keys_are_unique_and_kinds_are_known():
    keys = [provider.key for provider in jobboards.PROVIDERS]
    assert len(keys) == len(set(keys))
    assert {provider.kind for provider in jobboards.PROVIDERS} <= {KIND_ATS, KIND_AGGREGATOR, KIND_PORTFOLIO}


def test_every_provider_is_recognizable():
    """URL-pattern providers have patterns; portfolio ones have a page signature."""
    for provider in jobboards.PROVIDERS:
        if provider.kind == KIND_PORTFOLIO:
            assert provider.page_signature is not None and not provider.url_patterns, provider.key
        else:
            assert provider.url_patterns and provider.page_signature is None, provider.key


def test_every_alias_resolves():
    for alias in jobboards.SOURCE_ALIASES:
        assert jobboards.detect(alias) is not None, alias
