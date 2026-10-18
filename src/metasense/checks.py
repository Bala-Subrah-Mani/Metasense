"""Small, deterministic environment checks used by the MetaSense CLI."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_config(config: Any) -> list[str]:
    """Return validation errors; an empty list means the config schema is acceptable."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["Configuration root must be a JSON object."]

    for key in ("project_name", "environment"):
        value = config.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"'{key}' must be a non-empty string.")

    required_fields = config.get("required_fields", ["project_name", "environment"])
    if not isinstance(required_fields, list) or not all(isinstance(x, str) for x in required_fields):
        errors.append("'required_fields' must be a list of strings.")

    for key in ("directories_to_check", "optional_directories"):
        value = config.get(key, [])
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            errors.append(f"'{key}' must be a list of non-empty directory path strings.")

    if "strict_optional_directories" in config and not isinstance(config["strict_optional_directories"], bool):
        errors.append("'strict_optional_directories' must be a boolean.")

    return errors


def check_directories(root: Path, config: dict[str, Any], strict: bool = False) -> list[dict[str, Any]]:
    """Check configured paths relative to root. Paths are not created or modified."""
    results: list[dict[str, Any]] = []
    required = config.get("directories_to_check", [])
    optional = config.get("optional_directories", [])
    strict_optional = strict or config.get("strict_optional_directories", False)

    for item in required:
        path = (root / item).resolve()
        exists = path.is_dir()
        results.append({
            "name": item,
            "kind": "required_directory",
            "status": "pass" if exists else "fail",
            "exists": exists,
            "path": str(path),
        })

    for item in optional:
        path = (root / item).resolve()
        exists = path.is_dir()
        is_failure = strict_optional and not exists
        results.append({
            "name": item,
            "kind": "optional_directory",
            "status": "fail" if is_failure else ("pass" if exists else "warn"),
            "exists": exists,
            "path": str(path),
        })
    return results
