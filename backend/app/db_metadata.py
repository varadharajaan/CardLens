"""Aggregates all ORM metadata so Alembic and test setup can see every table.

Import each model module here as the project grows. This module exists so a single import
(``app.db_metadata``) registers every entity on the shared declarative ``Base.metadata``.
"""

from app.auth import models as _auth_models  # noqa: F401
from app.cards import models as _cards_models  # noqa: F401
from app.registry import models as _registry_models  # noqa: F401
from app.shared.database.base import Base
from app.statements import models as _statements_models  # noqa: F401
from app.users import models as _users_models  # noqa: F401

metadata = Base.metadata

__all__ = ["metadata"]
