# Test Plan

## Scope
Validate configuration parsing, schema checks, directory checks, summary generation, and CLI smoke-test behavior.

## Test cases
| ID | Scenario | Expected result |
|---|---|---|
| TC-01 | Valid configuration | No schema validation errors |
| TC-02 | Non-object configuration | Validation error |
| TC-03 | Missing project name | Validation error |
| TC-04 | Existing required directory | `pass` |
| TC-05 | Missing required directory | `fail` |
| TC-06 | Missing optional directory in default mode | `warn` |
| TC-07 | Missing optional directory in strict mode | `fail` |
| TC-08 | Valid JSON file | Configuration loaded |
| TC-09 | Missing configuration file | Clear `ValueError` |
| TC-10 | Malformed JSON | Clear `ValueError` |
| TC-11 | Full report generation | Status and summary present |

## Run
```bash
python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

## Evidence requirements
Capture the terminal session from the actual environment, including timestamp, exact command, output, and exit status. The included test cases define expected outcomes; they are not a substitute for a local execution record.
