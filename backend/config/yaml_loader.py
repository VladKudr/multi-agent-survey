"""YAML Agent config loader with validation."""

import os
from pathlib import Path
from typing import List

import structlog
import yaml

from schemas.agent import AgentConfig, AgentConfigFile

logger = structlog.get_logger()


class ConfigLoadError(Exception):
    """Error loading agent config."""

    pass


class AgentConfigLoader:
    """Loader for agent YAML configurations."""

    def __init__(self, config_path: str | None = None):
        """Initialize loader with config directory path."""
        self.config_path = Path(config_path or os.getenv("AGENT_CONFIG_PATH", "./agent-configs"))
        self._cache: dict[str, AgentConfig] = {}

    def _sanitize_yaml_content(self, content: str) -> str:
        """Sanitize YAML content to prevent injection attacks."""
        # Remove potentially dangerous tags
        dangerous_tags = ["!!python", "!!java", "!!ruby", "!!perl", "!!object"]
        for tag in dangerous_tags:
            if tag in content:
                raise ConfigLoadError(f"Dangerous YAML tag detected: {tag}")
        return content

    def load_config(self, agent_id: str) -> AgentConfig:
        """Load a single agent config by ID."""
        if agent_id in self._cache:
            return self._cache[agent_id]

        config_file = self.config_path / f"{agent_id}.yaml"
        if not config_file.exists():
            raise ConfigLoadError(f"Config file not found: {config_file}")

        try:
            content = config_file.read_text(encoding="utf-8")
            sanitized = self._sanitize_yaml_content(content)
            data = yaml.safe_load(sanitized)

            if not isinstance(data, dict) or "agent" not in data:
                raise ConfigLoadError(f"Invalid config structure for {agent_id}")

            config_file_model = AgentConfigFile(**data)
            config = config_file_model.agent

            # Validate ID matches filename
            if config.id != agent_id:
                raise ConfigLoadError(
                    f"Config ID mismatch: file={agent_id}, config={config.id}"
                )

            self._cache[agent_id] = config
            logger.info("agent_config_loaded", agent_id=agent_id)
            return config

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"YAML parsing error for {agent_id}: {e}")
        except Exception as e:
            raise ConfigLoadError(f"Failed to load config {agent_id}: {e}")

    def load_all_configs(self) -> List[AgentConfig]:
        """Load all agent configs from the config directory."""
        configs = []

        if not self.config_path.exists():
            logger.warning("config_path_not_found", path=str(self.config_path))
            return configs

        for config_file in self.config_path.glob("*.yaml"):
            agent_id = config_file.stem
            try:
                config = self.load_config(agent_id)
                configs.append(config)
            except ConfigLoadError as e:
                logger.error("config_load_failed", agent_id=agent_id, error=str(e))
                continue

        return configs

    def list_available_agents(self) -> List[str]:
        """List all available agent IDs."""
        if not self.config_path.exists():
            return []
        return [f.stem for f in self.config_path.glob("*.yaml")]

    def clear_cache(self) -> None:
        """Clear the config cache."""
        self._cache.clear()


# Global loader instance
_config_loader: AgentConfigLoader | None = None


def get_config_loader() -> AgentConfigLoader:
    """Get or create global config loader."""
    global _config_loader
    if _config_loader is None:
        _config_loader = AgentConfigLoader()
    return _config_loader
