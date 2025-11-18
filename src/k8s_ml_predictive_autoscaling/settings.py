"""Application-wide configuration helpers."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed settings leveraging environment variables for overrides."""

    environment: Literal["local", "dev", "prod"] = Field(
        default="local", description="Deployment environment descriptor."
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    service_name: str = Field(default="k8s-ml-predictive-autoscaling-demo")
    metrics_path: str = Field(default="/metrics")

    model_config = {
        "env_file": ".env",
        "env_prefix": "AUTOSCALER_",
        "env_file_encoding": "utf-8",
    }


@lru_cache
def get_settings() -> Settings:
    """Cache Settings to avoid re-parsing env on every injection."""

    return Settings()
