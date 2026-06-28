"""Externalized configuration data access.

Loads and validates the YAML data files that hold evolving domain data (bank identities, PDF password
rules, reward valuations). Feature code asks this loader for typed values instead of hardcoding bank
names or rules. A malformed data file fails fast at startup via :func:`DataLoader.validate_all`.
"""

from app.shared.config.data_loader import (
    BankConfig,
    DataLoader,
    PasswordRule,
    get_data_loader,
)

__all__ = ["BankConfig", "DataLoader", "PasswordRule", "get_data_loader"]
