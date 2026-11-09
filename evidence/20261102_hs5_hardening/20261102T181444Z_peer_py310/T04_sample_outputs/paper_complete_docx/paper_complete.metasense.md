# MetaSense assessment — paper_complete.docx

- Run ID: `5b9b6ea67bee`  |  Version: 0.2.3  |  UTC: 2026-11-02T18:15:07+00:00
- Extractor: python-docx  |  Words: 543
- Methodology section detected: **yes**
- Completeness score: **100.0 / 100** (present 8, weak 0, missing 0)
- Total processing time: 73.88 ms

## Detected sections

| Line | Heading | Label | Words |
|---|---|---|---|
| 1 | (front matter) | front_matter | 10 |
| 2 | Abstract | abstract | 43 |
| 4 | Introduction | introduction | 54 |
| 7 | Related Work | related_work | 24 |
| 9 | Methodology | methodology | 0 |
| 10 | Dataset | methodology (inherited) | 83 |
| 12 | Experimental Setup | methodology | 82 |
| 14 | Evaluation Metrics | methodology (inherited) | 33 |
| 16 | Baseline | methodology (inherited) | 30 |
| 18 | Results | results | 61 |
| 20 | Threats to Validity | threats_to_validity | 54 |
| 22 | Conclusion | conclusion | 32 |
| 24 | References | references | 10 |

## Rubric assessment

### C1 Research objective / questions — PRESENT
Rated PRESENT: 3 distinct indicator(s) found in the document (threshold 1).
- line 5 [Introduction]: "This study investigates whether simple execution-history features can identify flaky tests before they are re-run."
- line 6 [Introduction]: "We address two research questions."
- line 6 [Introduction]: "RQ1: How accurately can a gradient-boosted classifier identify flaky tests from execution-history features?"

### C2 Dataset / data source description — PRESENT
Rated PRESENT: 5 distinct indicator(s) found in the methodology section(s) (threshold 2).
- line 11 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 11 [Dataset]: "The data were split into a training set (70%) and a test set (30%) by project, so no project appears in both splits."
- line 11 [Dataset]: "All projects use OSI-approved licenses that permit research use."

### C3 Experimental setup / procedure — PRESENT
Rated PRESENT: 10 distinct indicator(s) found in the methodology section(s) (threshold 2).
- line 13 [Experimental Setup]: "The classifier was implemented in Python 3.11 using scikit-learn version 1.4."
- line 13 [Experimental Setup]: "We used 200 trees, a maximum depth of 6, and a learning rate of 0.05; these hyperparameters were selected with 5-fold cross-validation on the training set only."
- line 13 [Experimental Setup]: "Experiments ran on a workstation with an 8-core CPU and 32 GB of RAM; no GPU was required."

### C4 Evaluation metrics — PRESENT
Rated PRESENT: 4 distinct indicator(s) found in the methodology section(s) (threshold 1).
- line 15 [Evaluation Metrics]: "We report precision, recall, and F1-score for the flaky class, because flaky tests are a minority class and accuracy alone would be misleading."

### C5 Baseline / comparison — PRESENT
Rated PRESENT: 2 distinct indicator(s) found in the document (threshold 1).
- line 17 [Baseline]: "The proposed classifier is compared against a re-run baseline that labels a test flaky if it changes outcome within three re-runs, which is the heuristic used by the studied projects."

### C6 Statistical rigor / repeated trials — PRESENT
Rated PRESENT: 6 distinct indicator(s) found in the document (threshold 1).
- line 13 [Experimental Setup]: "We used 200 trees, a maximum depth of 6, and a learning rate of 0.05; these hyperparameters were selected with 5-fold cross-validation on the training set only."
- line 19 [Results]: "All experiments were repeated 10 times with different random seeds; the standard deviation of F1 was 0.02."
- line 19 [Results]: "A paired Wilcoxon signed-rank test showed the difference was statistically significant (p < 0.01)."

### C7 Threats to validity / limitations — PRESENT
Rated PRESENT: 3 distinct indicator(s) found in the document (threshold 1).
- line 21 [Threats to Validity]: "Internal validity may be affected by label noise, because a test that never failed during the observation window may still be flaky."
- line 21 [Threats to Validity]: "External validity is limited: all projects are Java projects, so the results may not generalize to other languages or CI systems."
- line 21 [Threats to Validity]: "Selection bias is possible because only active open-source projects were included."

### C8 Reproducibility / artifact availability — PRESENT
Rated PRESENT: 4 distinct indicator(s) found in the document (threshold 1).
- line 11 [Dataset]: "The dataset was collected from the public CI logs of 24 open-source Java projects hosted on GitHub between January 2023 and June 2024."
- line 19 [Results]: "All experiments were repeated 10 times with different random seeds; the standard deviation of F1 was 0.02."
- line 23 [Conclusion]: "The code and the anonymised dataset are publicly available in a replication package at https://github.com/example/flaky-history (placeholder URL for this synthetic sample)."

## Weaknesses

None detected by the baseline rules.

> MetaSense output is AI-assisted decision support produced by a rule-based baseline. It indicates whether methodology elements are reported, not whether the research is correct. A human reviewer must verify every finding.
