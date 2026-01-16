"""Tests for configuration loader."""


import pytest

from vm_mcp.config import ConfigLoader


class TestConfigLoader:
    """Tests for configuration loader."""

    def test_load_valid_config(self, sample_providers_yaml, monkeypatch):
        """Test loading valid YAML configuration."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        loader = ConfigLoader(enable_watch=False)
        config = loader.load()

        assert len(config.get_aws_accounts()) == 1
        assert len(config.get_azure_directories()) == 1
        assert config.get_aws_accounts()[0].alias == "test-aws"
        assert config.get_azure_directories()[0].alias == "test-azure"

    def test_missing_config_path_env(self, monkeypatch):
        """Test error when PROVIDERS_CONFIG_PATH is not set."""
        monkeypatch.delenv("PROVIDERS_CONFIG_PATH", raising=False)

        loader = ConfigLoader(enable_watch=False)
        with pytest.raises(ValueError, match="PROVIDERS_CONFIG_PATH"):
            loader.load()

    def test_missing_config_file(self, tmp_path, monkeypatch):
        """Test error when config file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.yaml"
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(nonexistent))

        loader = ConfigLoader(enable_watch=False)
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_invalid_yaml(self, tmp_path, monkeypatch):
        """Test error when config file has invalid YAML."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("{ invalid yaml content")
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(invalid_file))

        loader = ConfigLoader(enable_watch=False)
        with pytest.raises(ValueError, match="Invalid YAML"):
            loader.load()

    def test_empty_config(self, tmp_path, monkeypatch):
        """Test loading empty configuration."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(empty_file))

        loader = ConfigLoader(enable_watch=False)
        config = loader.load()

        assert config.get_aws_accounts() == []
        assert config.get_azure_directories() == []

    def test_get_config_lazy_load(self, sample_providers_yaml, monkeypatch):
        """Test lazy loading via get_config."""
        monkeypatch.setenv("PROVIDERS_CONFIG_PATH", str(sample_providers_yaml))

        # Use a local loader with watch disabled for testing
        loader = ConfigLoader(enable_watch=False)
        
        # First call should load
        config1 = loader.get_config()
        assert config1 is not None
        
        # Second call should return cached (same object)
        config2 = loader.get_config()
        assert config1 is config2
        assert len(config1.get_aws_accounts()) == 1
