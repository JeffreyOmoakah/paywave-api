from importlib import import_module
import pkgutil
from typing import Iterable, Optional
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import Engine

# Centralised ORM model registration for SQLAlchemy (Postgres)
# - creates a shared declarative Base
# - ensures all model modules are imported so ORM classes are registered (useful for Alembic autogenerate)


Base = declarative_base()
metadata = Base.metadata


def import_submodules(package: str, recursive: bool = True) -> None:
    """
    Import all submodules of a package, to ensure model classes are registered
    on the declarative Base (useful for Alembic autogenerate and metadata.create_all).

    Example package names to import:
      - "app.models"
      - "app.db.models"
      - "models" (if models live at top level)

    This is tolerant to missing packages.
    """
    try:
        pkg = import_module(package)
    except ImportError:
        return

    # If the imported name is a simple module (not a package), nothing more to do.
    pkg_path = getattr(pkg, "__path__", None)
    if not pkg_path:
        return

    for finder, name, ispkg in pkgutil.iter_modules(pkg_path):
        full_name = f"{package}.{name}"
        try:
            import_module(full_name)
        except Exception:
            # avoid failing on a single broken model import; log or re-raise if desired
            continue
        if recursive and ispkg:
            import_submodules(full_name, recursive=recursive)


def import_all_model_packages() -> None:
    """
    Try importing common packages where application models may live.
    Adjust or extend the list to match your project layout.
    """
    candidates = [
        "app.models",
        "app.db.models",
        "models",
        "db.models",
        "app.modules",  # add any other likely locations
    ]
    for pkg in candidates:
        import_submodules(pkg)


def create_all(engine: Engine, import_models: bool = True) -> None:
    """
    Convenience wrapper to import models (so they register with Base) and
    create all tables on the provided SQLAlchemy Engine.
    """
    if import_models:
        import_all_model_packages()
    metadata.create_all(engine)


# Ensure common model locations are imported on module import so external tools
# (like Alembic autogenerate) see all mapped classes without requiring manual imports.
import_all_model_packages()