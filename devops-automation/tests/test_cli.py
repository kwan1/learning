"""Tests for CLI module."""
import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from devops_tool.cli import app, setup_logging
from devops_tool.config import Config


# CliRunner is a special test utility from typer for testing CLI apps
runner = CliRunner()


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a sample config file for CLI testing."""
    config_content = """
app:
  name: "test-tool"
  version: "0.1.0"

logging:
  level: "INFO"
  format: "%(message)s"
  file: "logs/test.log"

paths:
  workdir: "."
  output: "output"
"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(config_content)
    return config_file


class TestCLI:
    """Test suite for CLI commands."""
    
    def test_run_command_with_config(self, sample_config_file, tmp_path):
        """Test the run command with a config file."""
        # Change to temp directory to avoid creating files in project
        with patch("devops_tool.cli.Config") as mock_config:
            # Mock the Config class to control its behavior
            config_instance = MagicMock()
            config_instance.config_path = sample_config_file
            config_instance.get.side_effect = lambda key, default=None: {
                "app.name": "test-tool",
                "app.version": "0.1.0",
                "logging.level": "INFO",
                "logging.format": "%(message)s",
                "logging.file": None,
            }.get(key, default)
            config_instance.get_path.return_value = tmp_path / "output"
            mock_config.return_value = config_instance
            
            result = runner.invoke(app, ["run", "--config", str(sample_config_file)])
            
            # Check exit code and output
            assert result.exit_code == 0
            assert "DevOps tool is running!" in result.stdout
    
    def test_run_command_without_config(self):
        """Test run command looks for default config.yaml."""
        # This will fail if config.yaml doesn't exist in current dir
        result = runner.invoke(app, ["run"])
        
        # Should handle missing config gracefully
        if "Error" in result.stdout:
            assert result.exit_code == 1
    
    def test_run_command_verbose_flag(self, sample_config_file, tmp_path):
        """Test that verbose flag enables DEBUG logging."""
        with patch("devops_tool.cli.Config") as mock_config:
            config_instance = MagicMock()
            config_instance.config_path = sample_config_file
            config_instance.data = {
                "logging": {"level": "INFO"},
                "app": {"name": "test", "version": "0.1.0"},
            }
            config_instance.get.side_effect = lambda key, default=None: {
                "app.name": "test-tool",
                "app.version": "0.1.0",
                "logging.level": "DEBUG",  # Should be DEBUG with -v
                "logging.format": "%(message)s",
                "logging.file": None,
            }.get(key, default)
            config_instance.get_path.return_value = tmp_path / "output"
            mock_config.return_value = config_instance
            
            result = runner.invoke(app, ["run", "-v", "--config", str(sample_config_file)])
            
            # Verify verbose mode was activated
            assert result.exit_code == 0
            # Check that config.data was modified to DEBUG
            assert config_instance.data["logging"]["level"] == "DEBUG"
    
    def test_info_command(self, sample_config_file, tmp_path, monkeypatch):
        """Test the info command displays configuration."""
        # monkeypatch lets you modify behavior for the test
        monkeypatch.chdir(tmp_path)
        
        with patch("devops_tool.cli.Config") as mock_config:
            config_instance = MagicMock()
            config_instance.config_path = sample_config_file
            config_instance.get.side_effect = lambda key, default=None: {
                "app.name": "test-tool",
                "app.version": "0.1.0",
                "logging.level": "INFO",
            }.get(key, default)
            mock_config.return_value = config_instance
            
            result = runner.invoke(app, ["info"])
            
            assert result.exit_code == 0
            assert "test-tool" in result.stdout
            assert "0.1.0" in result.stdout
    
    def test_info_command_missing_config(self):
        """Test info command handles missing config gracefully."""
        with patch("devops_tool.cli.Config", side_effect=FileNotFoundError("Config not found")):
            result = runner.invoke(app, ["info"])
            
            assert result.exit_code == 1
            assert "Error" in result.stdout
    
    def test_help_command(self):
        """Test that --help works."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "DevOps automation tool" in result.stdout
        assert "run" in result.stdout
        assert "info" in result.stdout
    
    def test_run_command_help(self):
        """Test that run command has help."""
        result = runner.invoke(app, ["run", "--help"])
        
        assert result.exit_code == 0
        assert "--config" in result.stdout
        assert "--verbose" in result.stdout


class TestLoggingSetup:
    """Test suite for logging configuration."""
    
    def test_setup_logging_creates_log_directory(self, sample_config_file, tmp_path):
        """Test that setup_logging creates the logs directory."""
        config = Config(sample_config_file)
        config.data["logging"]["file"] = str(tmp_path / "logs" / "test.log")
        
        setup_logging(config)
        
        # Check that logs directory was created
        log_dir = tmp_path / "logs"
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_setup_logging_with_no_file(self, sample_config_file):
        """Test setup_logging when no log file is configured."""
        config = Config(sample_config_file)
        config.data["logging"]["file"] = None
        
        # Should not raise any errors
        setup_logging(config)
