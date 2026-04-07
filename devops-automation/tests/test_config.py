"""Tests for config module."""
import pytest
from pathlib import Path
from devops_tool.config import Config


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a sample config file for testing.
    
    This is a pytest fixture - a reusable test component.
    tmp_path is a built-in pytest fixture that creates a temporary directory.
    """
    config_content = """
app:
  name: "test-app"
  version: "1.0.0"

logging:
  level: "DEBUG"
  format: "test format"
  file: "test.log"

paths:
  workdir: "/tmp/work"
  output: "/tmp/output"

nested:
  deep:
    value: 42
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    return config_file


class TestConfig:
    """Test suite for Config class."""
    
    def test_load_valid_config(self, sample_config_file):
        """Test loading a valid config file."""
        config = Config(sample_config_file)
        
        assert config.data is not None
        assert config.get("app.name") == "test-app"
        assert config.get("app.version") == "1.0.0"
    
    def test_missing_config_file(self, tmp_path):
        """Test that FileNotFoundError is raised for missing config."""
        missing_file = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            Config(missing_file)
    
    def test_get_with_dot_notation(self, sample_config_file):
        """Test getting nested values with dot notation."""
        config = Config(sample_config_file)
        
        assert config.get("logging.level") == "DEBUG"
        assert config.get("nested.deep.value") == 42
    
    def test_get_with_default(self, sample_config_file):
        """Test get() returns default for missing keys."""
        config = Config(sample_config_file)
        
        # Non-existent key should return default
        assert config.get("missing.key", "default") == "default"
        assert config.get("missing.key") is None
    
    def test_get_path(self, sample_config_file):
        """Test get_path() returns Path object."""
        config = Config(sample_config_file)
        
        workdir = config.get_path("paths.workdir")
        assert isinstance(workdir, Path)
        assert str(workdir) == "/tmp/work"
    
    def test_get_path_missing_key(self, sample_config_file):
        """Test get_path() raises ValueError for missing key."""
        config = Config(sample_config_file)
        
        with pytest.raises(ValueError, match="Path config 'missing.path' not found"):
            config.get_path("missing.path")
    
    @pytest.mark.parametrize("key,expected", [
        ("app.name", "test-app"),
        ("app.version", "1.0.0"),
        ("logging.level", "DEBUG"),
        ("nested.deep.value", 42),
    ])
    def test_get_multiple_keys(self, sample_config_file, key, expected):
        """Test getting multiple keys using parametrize.
        
        This runs the same test with different inputs - great for testing
        multiple scenarios without duplicating code!
        """
        config = Config(sample_config_file)
        assert config.get(key) == expected
    
    def test_empty_config_file(self, tmp_path):
        """Test loading an empty config file."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")
        
        config = Config(empty_file)
        assert config.data == {}
        assert config.get("any.key") is None
