"""Shared pytest configuration and fixtures.

This file is automatically discovered by pytest and makes fixtures
available to all test files without importing them.
"""
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_yaml_content():
    """Return sample YAML config content for testing."""
    return """
app:
  name: "devops-tool"
  version: "0.1.0"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/devops_tool.log"

paths:
  workdir: "."
  output: "output"
"""
