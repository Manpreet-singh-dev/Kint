"""Test utilities and helper functions."""

from typing import Dict


def get_sample_generated_files() -> Dict[str, str]:
    """Return sample generated files dictionary."""
    return {
        "index.html": "<!DOCTYPE html><html><head><title>Test App</title></head><body><h1>Hello</h1></body></html>",
        "style.css": "body { font-family: sans-serif; }",
        "script.js": "document.addEventListener('DOMContentLoaded', () => {});",
    }
