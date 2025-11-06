"""Configuration management."""
import os
import yaml
from pathlib import Path
from typing import Any, Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    ntfy_url: str = "http://ntfy:80"
    ntfy_topic: str = "nifty-alerts"
    alert_check_time: str = "16:00"
    timezone: str = "Asia/Kolkata"

    class Config:
        env_file = ".env"
        case_sensitive = False


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)
