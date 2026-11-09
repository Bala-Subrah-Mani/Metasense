# MetaSense Architecture: Implemented Baseline (v0.2.1)

How the RU-04 design components map to the code that exists in RU-06:

```text
metasense analyze <file>
   │
   ▼
[Validation Module] application/validation.py ──reject──► structured error (code, message, stage), exit 1
   │ ValidatedInput(kind=text|pdf|docx)
   ▼
[Text Extraction] processing/document_processor.py   (pypdf / python-docx / stdlib)
   │ normalized lines + warnings
   ▼
[Section Detector] processing/section_detector.py    (numbering/markdown/caps/title-case + synonym table)
   │ sections[label, line range], unrecognized headings
   ▼
[NLP Processor: baseline] assessment_engine.split_sentences  (sentence split with line numbers)
   ▼
[Assessment Engine] processing/assessment_engine.py  (resources/rubric.json: 8 criteria, regex indicators)
   │ per-criterion present/weak/missing + evidence quotes
   ▼
[Weakness Detector] processing/weakness_detector.py  (severity rules, vague-language flag)
   ▼
[Explainability] processing/explainability.py        (rule applied + cited lines + recommendation)
   ▼
[Report Generator] reporting/report_generator.py     (JSON + Markdown)
```

`application/workflow.py` runs these stages, times each one (`timings_ms`), records the input
SHA-256, and turns `ValidationError`/`ExtractionError` into a well-formed error report.

## Not yet implemented (from the RU-04 design)
Authentication, Upload UI, Dashboard, Data layer (database), Evaluation Logger beyond `evidence/`,
and the semantic/transformer NLP classifier. The rule-based components above are the
"basic rule-based baseline" that RU-04 §7.7 requires for later comparison.

## Toolchain support
`toolchain/doctor.py` (`metasense doctor`) checks the Python version, venv, package imports and versions,
write permissions, config readability, environment variables and repository layout. It reuses the RU-05 checker in
`toolchain/checks.py` and `toolchain/config_check.py`.
