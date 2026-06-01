"""Load configuration from environment variables (or a .env file).

Secrets are read from the environment only — nothing is hardcoded and
nothing is committed. See .env.example for the variable names.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    # Optional: load a local .env if present. Safe no-op if not installed.
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # pragma: no cover
    pass


def _get(name: str) -> Optional[str]:
    val = os.environ.get(name)
    return val.strip() if val else None


@dataclass
class GorgiasConfig:
    domain: Optional[str]
    email: Optional[str]
    api_key: Optional[str]

    @property
    def ready(self) -> bool:
        return all([self.domain, self.email, self.api_key])


@dataclass
class JudgeMeConfig:
    api_token: Optional[str]
    shop_domain: Optional[str]

    @property
    def ready(self) -> bool:
        return all([self.api_token, self.shop_domain])


@dataclass
class FacebookConfig:
    page_id: Optional[str]
    access_token: Optional[str]
    api_version: str

    @property
    def ready(self) -> bool:
        return all([self.page_id, self.access_token])


@dataclass
class Config:
    gorgias: GorgiasConfig
    judgeme: JudgeMeConfig
    facebook: FacebookConfig


def load_config() -> Config:
    return Config(
        gorgias=GorgiasConfig(
            domain=_get("GORGIAS_DOMAIN"),
            email=_get("GORGIAS_EMAIL"),
            api_key=_get("GORGIAS_API_KEY"),
        ),
        judgeme=JudgeMeConfig(
            api_token=_get("JUDGEME_API_TOKEN"),
            shop_domain=_get("JUDGEME_SHOP_DOMAIN"),
        ),
        facebook=FacebookConfig(
            page_id=_get("FACEBOOK_PAGE_ID"),
            access_token=_get("FACEBOOK_ACCESS_TOKEN"),
            api_version=_get("FACEBOOK_API_VERSION") or "v19.0",
        ),
    )
