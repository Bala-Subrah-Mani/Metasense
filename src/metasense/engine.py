"""Application logic for MetaSense environment/configuration checks."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .checks import check_directories, validate_config


def load_config(config_path: Path) -> dict[str, Any]:
    """Load a JSON config and raise ValueError with a clear message on malformed input."""
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"Configuration file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in configuration file: {exc.msg}") from exc

    errors = validate_config(data)
    if errors:
        raise ValueError("Configuration validation failed: " + "; ".join(errors))
    return data


def run_checks(config_path: Path, root: Path, strict: bool = False) -> dict[str, Any]:
    """Run checks and return a serializable report."""
    config = load_config(config_path)
    required_fields = config.get("required_fields", ["project_name", "environment"])
    field_results = []
    for field in required_fields:
        present = isinstance(config.get(field), str) and bool(config[field].strip())
        field_results.append({
            "name": field,
            "kind": "required_config_field",
            "status": "pass" if present else "fail",
            "exists": present,
        })

    directory_results = check_directories(root, config, strict=strict)
    checks = field_results + directory_results
    failures = sum(1 for item in checks if item["status"] == "fail")
    warnings = sum(1 for item in checks if item["status"] == "warn")
    return {
        "application": "MetaSense",
        "version": "0.1.0",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root.resolve()),
        "config_path": str(config_path.resolve()),
        "status": "fail" if failures else ("warning" if warnings else "pass"),
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for item in checks if item["status"] == "pass"),
            "warnings": warnings,
            "failed": failures,
        },
        "checks": checks,
    }
