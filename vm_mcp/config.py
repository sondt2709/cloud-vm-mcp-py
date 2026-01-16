"""Configuration loader with file watching for hot-reload."""

import logging
import os
import threading
from pathlib import Path
from typing import Callable

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from vm_mcp.model.credentials import (
    AWSAccount,
    AWSConfig,
    AzureConfig,
    AzureDirectory,
    ProvidersConfig,
)

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """Handles file system events for config file changes."""

    def __init__(self, config_path: Path, on_change: Callable[[], None]):
        self.config_path = config_path
        self.on_change = on_change

    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path) == self.config_path:
            self.on_change()


class ConfigLoader:
    """Loads and watches provider configuration from YAML file."""

    def __init__(self, enable_watch: bool = True):
        self._config: ProvidersConfig | None = None
        self._config_path: Path | None = None
        self._observer: Observer = None # type: ignore
        self._lock = threading.RLock()  # Use RLock for reentrant locking
        self._enable_watch = enable_watch

    def load(self) -> ProvidersConfig:
        """Load configuration from PROVIDERS_CONFIG_PATH environment variable."""
        config_path_str = os.getenv("PROVIDERS_CONFIG_PATH")

        if not config_path_str:
            raise ValueError("PROVIDERS_CONFIG_PATH environment variable is not set")

        config_path = Path(config_path_str)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with self._lock:
            self._config_path = config_path
            self._config = self._parse_config(config_path)
            if self._enable_watch:
                self._start_watcher()

        return self._config

    def _parse_config(self, config_path: Path) -> ProvidersConfig:
        """Parse YAML configuration file."""
        try:
            with open(config_path, "r") as f:
                raw_config = yaml.safe_load(f)

            if not raw_config or "providers" not in raw_config:
                return ProvidersConfig(providers={})

            providers = {}
            raw_providers = raw_config.get("providers", {})

            # Parse AWS config
            if "aws" in raw_providers:
                aws_raw = raw_providers["aws"]
                accounts = [
                    AWSAccount.model_validate(acc)
                    for acc in aws_raw.get("accounts", [])
                ]
                providers["aws"] = AWSConfig(accounts=accounts)

            # Parse Azure config
            if "azure" in raw_providers:
                azure_raw = raw_providers["azure"]
                directories = [
                    AzureDirectory.model_validate(d)
                    for d in azure_raw.get("directories", [])
                ]
                providers["azure"] = AzureConfig(directories=directories)

            return ProvidersConfig(providers=providers)

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")

    def _start_watcher(self):
        """Start file watcher for hot-reload."""
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=1)

        if self._config_path is None:
            return

        self._observer = Observer()
        self._observer.daemon = True  # Make it a daemon thread so it doesn't block exit
        handler = ConfigFileHandler(self._config_path, self._on_config_change)
        self._observer.schedule(
            handler, str(self._config_path.parent), recursive=False
        )
        self._observer.start()

    def _on_config_change(self):
        """Handle configuration file change."""
        if self._config_path is None:
            return

        try:
            new_config = self._parse_config(self._config_path)
            with self._lock:
                self._config = new_config
        except Exception:
            # Keep previous valid config on error
            logger.exception("Failed to reload configuration")

    def get_config(self) -> ProvidersConfig:
        """Get current configuration."""
        with self._lock:
            if self._config is None:
                return self.load()
            return self._config

    def stop(self):
        """Stop the file watcher."""
        if self._observer is not None:
            self._observer.stop()
            # Don't join - let daemon thread die naturally
            self._observer = None


# Global config loader instance
_config_loader: ConfigLoader | None = None


def get_config_loader() -> ConfigLoader:
    """Get or create the global config loader."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_config() -> ProvidersConfig:
    """Get the current provider configuration."""
    return get_config_loader().get_config()


def reset_config_loader() -> None:
    """Reset the global config loader. Useful for testing."""
    global _config_loader
    if _config_loader is not None:
        _config_loader.stop()
        _config_loader = None
