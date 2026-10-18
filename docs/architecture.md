# MetaSense Architecture (Starter Interpretation)

## Purpose
MetaSense is implemented here as a local configuration and environment structure checker. This is a working starter interpretation because the supplied feedback names MetaSense but does not provide the complete original specification.

## Components
1. **CLI (`src/metasense/cli.py`)** — parses arguments and chooses text or JSON output.
2. **Engine (`src/metasense/engine.py`)** — loads configuration, runs checks, summarizes outcomes.
3. **Checks (`src/metasense/checks.py`)** — validates configuration fields and verifies expected directories.
4. **JSON configuration (`config/metasense.json`)** — lists required and optional paths.
5. **Tests (`tests/`)** — verify configuration validation, directory behavior, and report generation.

## Data flow
```text
CLI arguments
    |
    v
Load JSON configuration -> Validate configuration
    |                           |
    +---------------------------+
                |
                v
       Check required/optional paths
                |
                v
     Build report + summary + timestamp
                |
         +------+------+
         |             |
         v             v
    Text output     JSON output
```

## Security and privacy boundaries
- No credentials or secrets are requested or stored.
- The program checks local directory existence only; it does not upload files.
- Paths are read-only; the program does not create directories or change permissions.
- The tool is not a cloud security scanner and does not claim NIST/ISO/CSA compliance.
