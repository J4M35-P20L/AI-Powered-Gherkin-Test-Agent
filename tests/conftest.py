import pytest
import os
import sys
import logging
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from autotester.utils.env_loader import load_api_key, load_base_url
from autotester.utils.logger import get_logger

# --- Pytest Command-Line Option ---
def pytest_addoption(parser):
    """Adds a custom command-line option to pytest for specifying a URL."""
    default_url = load_base_url()
    parser.addoption(
        "--url",
        action="store",
        default=default_url,
        help="The starting URL for the application to be tested"
    )

# --- Pytest Fixtures ---

@pytest.fixture(scope="session")
def client():
    """Initializes the Gemini AI client once per test session."""
    api_key = load_api_key('gemini')
    genai.configure(api_key=api_key)

    # --- SPEED FIX 1 ---
    # Using 'gemini-flash-latest', which is optimized for speed.
    return genai.GenerativeModel('gemini-flash-latest')

@pytest.fixture(scope="session")
def logger():
    """Initializes the logger once per test session."""
    return get_logger()

@pytest.fixture
def page(request):
    """
    Provides a Playwright page object for each test.
    """
    start_url = request.config.getoption("--url")

    with sync_playwright() as p:
        # --- SPEED FIX 2 ---
        # Changed headless=True and slow_mo=0 for maximum speed.
        # Set headless=False if you still want to watch it.
        browser = p.chromium.launch(headless=False, slow_mo=0)
        # --- END OF FIX ---

        context = browser.new_context()
        page = context.new_page()

        if start_url:
            page.goto(start_url)
            page.wait_for_load_state('networkidle')

        yield page

        # Clean up
        context.close()
        browser.close()