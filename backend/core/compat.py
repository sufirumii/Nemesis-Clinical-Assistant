"""
Compatibility shim — pydantic_settings ships separately in pydantic v2.
If pydantic_settings is not installed, fall back to pydantic v1 BaseSettings.
"""
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # noqa: F401
except ImportError:
    from pydantic import BaseSettings  # type: ignore  # noqa: F401
    SettingsConfigDict = dict  # type: ignore
