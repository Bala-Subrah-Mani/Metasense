# MetaSense assessment — paper_complete.pdf

- Run ID: `8017cf7405b8`  |  Version: 0.2.0  |  UTC: 2026-10-19T10:16:50+00:00
- Extractor: pypdf  |  Words: 543
- Methodology section detected: **yes**
- Completeness score: **100.0 / 100** (present 8, weak 0, missing 0)
- Total processing time: 71.76 ms

## Detected sections

| Line | Heading | Label | Words |
|---|---|---|---|
| 1 | (front matter) | front_matter | 54 |
| 7 | Introduction | introduction | 54 |
| 13 | Related Work | related_work | 24 |
| 16 | Methodology | methodology | 0 |
| 17 | Dataset | methodology (inherited) | 83 |
| 23 | Experimental Setup | methodology | 82 |
| 30 | Evaluation Metrics | methodology (inherited) | 33 |
| 34 | Baseline | methodology (inherited) | 30 |
| 37 | Results | results | 61 |
| 42 | Threats to Validity | threats_to_validity | 54 |
| 47 | Conclusion | conclusion | 43 |

## Rubric assessment

### C1 Research objective / questions — PRESENT
Rated PRESENT: 3 distinct indicator(s) found in the document (threshold 1).
- line 8 [Introduction]: "This study investigates whether simple execution-history features can identify flaky tests before they are re-run."
- line 10 [Introduction]: "We address two research questions."
- line 10 [Introduction]: "RQ1: How accurately can a gradient-boosted classifier identify flaky tests from execution-history features?"

### C2 Dataset / data source description — PRESENT
Rated PRESENT: 4 distinct indicator(s) found in the methodology section(s) (threshold 2).
- line 18 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 18 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 21 [Dataset]: "The data were split into a training set (70%) and a test set (30%) by project, so no project appears in both splits."

### C3 Experimental setup / procedure — PRESENT
Rated PRESENT: 10 distinct indicator(s) found in the methodology section(s) (threshold 2).
- line 24 [Experimental Setup]: "The classifier was implemented in Python 3.11 using scikit-learn version 1.4."
- line 24 [Experimental Setup]: "The classifier was implemented in Python 3.11 using scikit-learn version 1.4."
- line 24 [Experimental Setup]: "The classifier was implemented in Python 3.11 using scikit-learn version 1.4."

### C4 Evaluation metrics — PRESENT
Rated PRESENT: 4 distinct indicator(s) found in the methodology section(s) (threshold 1).
- line 32 [Evaluation Metrics]: "We report precision, recall, and F1-score for the flaky class, because flaky tests are a minority class and accuracy alone would be misleading."
- line 32 [Evaluation Metrics]: "We report precision, recall, and F1-score for the flaky class, because flaky tests are a minority class and accuracy alone would be misleading."
- line 32 [Evaluation Metrics]: "We report precision, recall, and F1-score for the flaky class, because flaky tests are a minority class and accuracy alone would be misleading."

### C5 Baseline / comparison — PRESENT
Rated PRESENT: 2 distinct indicator(s) found in the document (threshold 1).
- line 35 [Baseline]: "The proposed classifier is compared against a re-run baseline that labels a test flaky if it changes outcome within three re-runs, which is the heuristic used by the studied projects."
- line 35 [Baseline]: "The proposed classifier is compared against a re-run baseline that labels a test flaky if it changes outcome within three re-runs, which is the heuristic used by the studied projects."

### C6 Statistical rigor / repeated trials — PRESENT
Rated PRESENT: 6 distinct indicator(s) found in the document (threshold 1).
- line 24 [Experimental Setup]: "We used 200 trees, a maximum depth of 6, and a learning rate of 0.05; these hyperparameters were selected with 5-fold cross-validation on the training set only."
- line 39 [Results]: "All experiments were repeated 10 times with different random seeds; the standard deviation of F1 was 0.02."
- line 39 [Results]: "All experiments were repeated 10 times with different random seeds; the standard deviation of F1 was 0.02."

### C7 Threats to validity / limitations — PRESENT
Rated PRESENT: 3 distinct indicator(s) found in the document (threshold 1).
- line 43 [Threats to Validity]: "Internal validity may be affected by label noise, because a test that never failed during the observation window may still be flaky."
- line 44 [Threats to Validity]: "External validity is limited: all projects are Java projects, so the results may not generalize to other languages or CI systems."
- line 45 [Threats to Validity]: "Selection bias is possible because only active open-source projects were included."

### C8 Reproducibility / artifact availability — PRESENT
Rated PRESENT: 5 distinct indicator(s) found in the document (threshold 1).
- line 18 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 18 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 39 [Results]: "All experiments were repeated 10 times with different random seeds; the standard deviation of F1 was 0.02."

## Weaknesses

None detected by the baseline rules.

> MetaSense output is AI-assisted decision support produced by a rule-based baseline. It indicates whether methodology elements are reported, not whether the research is correct. A human reviewer must verify every finding.
