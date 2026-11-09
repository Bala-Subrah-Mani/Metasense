# MetaSense assessment — E1-strimel23a.pdf

- Run ID: `d1810f7489c4`  |  Version: 0.2.1  |  UTC: 2026-10-25T20:22:46+00:00
- Extractor: pypdf  |  Words: 10835
- Methodology section detected: **no**
- Completeness score: **56.2 / 100** (present 3, weak 3, missing 2)
- Total processing time: 563.41 ms

## Detected sections

| Line | Heading | Label | Words |
|---|---|---|---|
| 1 | (front matter) | front_matter | 32 |
| 4 | Abstract | abstract | 194 |
| 23 | Introduction | introduction | 589 |
| 83 | Related Work | related_work | 720 |
| 153 | Adaptive Non-causal Design | unknown | 223 |
| 172 | Compute DAGs and Attention Masking | unknown | 268 |
| 219 | j ≤ i | unknown | 49 |
| 227 | P = | unknown | 17 |
| 235 | PT | unknown | 4 |
| 238 | ≤ i, j≤ T | unknown | 15 |
| 241 | Learned Schedulers | unknown | 137 |
| 265 | − σ | unknown | 13 |
| 273 | otherwise, | unknown | 103 |
| 286 | Regularizing Future Context | unknown | 30 |
| 291 | Naive Regularization | unknown | 66 |
| 299 | LL1 = 1 | unknown | 0 |
| 300 | T | unknown | 0 |
| 301 | X | unknown | 1 |
| 303 | X | unknown | 159 |
| 348 | Algorithmic Latency | unknown | 105 |
| 359 | T | unknown | 0 |
| 360 | X | unknown | 502 |
| 457 | T | unknown | 0 |
| 458 | X | unknown | 4 |
| 461 | T | unknown | 0 |
| 462 | X | unknown | 24 |
| 469 | Compute-Induced UPL | unknown | 168 |
| 488 | X | unknown | 1 |
| 490 | X | unknown | 67 |
| 499 | i = 0 | unknown | 111 |
| 523 | Experimental Results | unknown | 134 |
| 538 | ANCAT-L1 | unknown | 3 |
| 542 | ANCAT-L1 | unknown | 3 |
| 546 | ANCAT-L1 | unknown | 187 |
| 563 | LibriSpeech Experimental Setup | unknown | 109 |
| 572 | stacked blocks, one-layer 640-unit LSTM prediction | unknown | 150 |
| 588 | Baselines | unknown | 100 |
| 599 | Algorithmic Latency Results | unknown | 803 |
| 675 | Industrial Voice Assistant | unknown | 73 |
| 682 | Compute-Induced UPL | unknown | 99 |
| 691 | Additional Findings and Analysis | unknown | 121 |
| 704 | Conclusion | conclusion | 155 |
| 722 | References | references | 1457 |
| 892 | Emission Latency and Endpointer Latency | unknown | 164 |
| 907 | ANCAT-L1 | unknown | 3 |
| 911 | ANCAT-L1 | unknown | 3 |
| 915 | ANCAT-L1 | unknown | 46 |
| 920 | LibriSpeech “Other” and Noise Impact | unknown | 428 |
| 947 | Voice Assistant Data | unknown | 497 |
| 982 | Compute-Induced UPL Results | unknown | 636 |
| 1020 | Attention Dynamics | unknown | 316 |
| 1041 | Training Characteristics | unknown | 880 |
| 1098 | Training Configuration Specifics | unknown | 204 |
| 1120 | Voice Assistant Result Tables | unknown | 48 |
| 1134 | UPL | unknown | 406 |
| 1191 | UPL | unknown | 63 |

Unrecognized headings: Adaptive Non-causal Design; Compute DAGs and Attention Masking; j ≤ i; P =; PT; ≤ i, j≤ T; Learned Schedulers; − σ; otherwise,; Regularizing Future Context; Naive Regularization; LL1 = 1; T; X; X; Algorithmic Latency; T; X; T; X; T; X; Compute-Induced UPL; X; X; i = 0; Experimental Results; ANCAT-L1; ANCAT-L1; ANCAT-L1; LibriSpeech Experimental Setup; stacked blocks, one-layer 640-unit LSTM prediction; Baselines; Algorithmic Latency Results; Industrial Voice Assistant; Compute-Induced UPL; Additional Findings and Analysis; Emission Latency and Endpointer Latency; ANCAT-L1; ANCAT-L1; ANCAT-L1; LibriSpeech “Other” and Noise Impact; Voice Assistant Data; Compute-Induced UPL Results; Attention Dynamics; Training Characteristics; Training Configuration Specifics; Voice Assistant Result Tables; UPL; UPL

## Rubric assessment

### C1 Research objective / questions — PRESENT
Rated PRESENT: 1 distinct indicator(s) found in the document (threshold 1).
- line 422 [X]: "Since Dℓ−1 t,j−1 ≥ Dℓ−1 t,j by induction hypothesis, there exists at least one t′, namely t′ = t, over which a maximum is taken such that Dℓ i,j−1 ≥ Mℓ i,t′ · Dℓ−1 t′,j−1 ≥ Mℓ i,t · Dℓ−1 t,j = Dℓ i,j."

### C2 Dataset / data source description — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (4 found elsewhere).
- line 20 [Abstract]: "We showcase our design experimentally by reporting comparative ASR task results with measures of accuracy and latency on both publicly accessible and productionscale, voice-assistant datasets."
- line 564 [LibriSpeech Experimental Setup]: "We investigate our architectures using the LibriSpeech corpus (Panayotov et al., 2015) comprised of 960 hours of training data collected from read audio books."
- line 564 [LibriSpeech Experimental Setup]: "We investigate our architectures using the LibriSpeech corpus (Panayotov et al., 2015) comprised of 960 hours of training data collected from read audio books."
- *Recommendation:* Describe the data source, how it was collected or selected, its size, and its train/test split or sampling procedure.

### C3 Experimental setup / procedure — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (7 found elsewhere).
- line 100 [Related Work]: "Similar to dual-mode training, (Swietojanski et al., 2022) also extends in-place distillation to chunking of variable sizes, training a single model but allowing different chunk sizes to be configured at inference to ma…"
- line 576 [stacked blocks, one-layer 640-unit LSTM prediction]: "For LibriSpeech, all the models are trained for 150 epochs of 1k steps with the Transformer-based encoder backbone and schedulers trained end-to-end jointly using the Adam optimizer (Kingma & Lei Ba, 2015) using the sam…"
- line 576 [stacked blocks, one-layer 640-unit LSTM prediction]: "For LibriSpeech, all the models are trained for 150 epochs of 1k steps with the Transformer-based encoder backbone and schedulers trained end-to-end jointly using the Adam optimizer (Kingma & Lei Ba, 2015) using the sam…"
- *Recommendation:* Report the procedure step by step, including software/hardware environment and parameter settings, so the study could be repeated.

### C4 Evaluation metrics — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (4 found elsewhere).
- line 5 [Abstract]: "Streaming speech recognition architectures are employed for low-latency, real-time applications."
- line 8 [Abstract]: "Causal architectures emit tokens at each frame, relying only on current and past signal, while non-causal models are exposed to a window of future frames at each step to increase predictive accuracy."
- line 128 [Related Work]: "Additionally, all adaptive techniques effectively tie their compute to a particular cost metric, such as floating point operations."
- *Recommendation:* Name the evaluation metrics and explain why they fit the research question.

### C5 Baseline / comparison — PRESENT
Rated PRESENT: 2 distinct indicator(s) found in the document (threshold 1).
- line 304 [X]: "j>i Mℓ i,j This L1-type regularization will serve as a baseline for our experiments."
- line 630 [Algorithmic Latency Results]: "Observe also, that compared with naive L1 regularization, for a given algorithmic latency budget, our ANCAT-Alg.Lat. models allow for a greater total amount of future frame attention based on ℓ1-norm measures."

### C6 Statistical rigor / repeated trials — MISSING
Rated MISSING: no indicator for this criterion was found in the document.
- *Recommendation:* Report variability (e.g., standard deviation over repeated runs) and, where claims compare methods, a significance test or confidence interval.

### C7 Threats to validity / limitations — PRESENT
Rated PRESENT: 1 distinct indicator(s) found in the document (threshold 1).
- line 11 [Abstract]: "This dichotomy amounts to a tradeoff for real-time Automatic Speech Recognition (ASR) system design: profit from the low-latency benefit of strictly-causal architectures while accepting predictive performance limitation…"

### C8 Reproducibility / artifact availability — MISSING
Rated MISSING: no indicator for this criterion was found in the document.
- *Recommendation:* Provide a link to code/data or a replication package and record random seeds and versions.

## Weaknesses

- **W01 [high]** No methodology-related section heading was detected; criteria scoped to the methodology can only be found outside it, so they are rated 'weak' at best.
- **W02 [medium]** Dataset / data source description: limited reporting (only outside the methodology section).
- **W03 [medium]** Experimental setup / procedure: limited reporting (only outside the methodology section).
- **W04 [medium]** Evaluation metrics: limited reporting (only outside the methodology section).
- **W05 [medium]** Statistical rigor / repeated trials: no indicator found.
- **W06 [medium]** Reproducibility / artifact availability: no indicator found.

> MetaSense output is AI-assisted decision support produced by a rule-based baseline. It indicates whether methodology elements are reported, not whether the research is correct. A human reviewer must verify every finding.
