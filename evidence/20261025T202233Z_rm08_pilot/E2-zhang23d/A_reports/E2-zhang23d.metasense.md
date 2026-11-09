# MetaSense assessment — E2-zhang23d.pdf

- Run ID: `e33741a062f4`  |  Version: 0.2.1  |  UTC: 2026-10-25T20:24:04+00:00
- Extractor: pypdf  |  Words: 7950
- Methodology section detected: **no**
- Completeness score: **56.2 / 100** (present 3, weak 3, missing 2)
- Total processing time: 609.61 ms

## Detected sections

| Line | Heading | Label | Words |
|---|---|---|---|
| 1 | (front matter) | front_matter | 34 |
| 6 | Abstract | abstract | 175 |
| 28 | INTRODUCTION | introduction | 894 |
| 125 | Related work | related_work | 414 |
| 168 | PROBLEM SETUP AND NOTATIONS | unknown | 463 |
| 225 | PROV ABLE LINEAR SEPARABILITY | unknown | 0 |
| 226 | OF ADVERSARIAL NOISES | unknown | 36 |
| 231 | Linear Separability at Initialization | unknown | 263 |
| 266 | = E | unknown | 28 |
| 283 | = E | unknown | 11 |
| 293 | + 5 | unknown | 263 |
| 336 | X =Π⊥ | unknown | 0 |
| 337 | A1 | unknown | 0 |
| 338 | ˜XΠ⊥ | unknown | 0 |
| 339 | A2 + Π⊥ | unknown | 0 |
| 340 | A1 XΠA2 | unknown | 0 |
| 341 | + ΠA1 XΠ⊥ | unknown | 47 |
| 348 | Π⊥ | unknown | 49 |
| 355 | W = ˜WΠ⊥ | unknown | 658 |
| 462 | Linear Separability in NTK Regime | unknown | 380 |
| 507 | D∗ | unknown | 38 |
| 514 | − δ, 1 | unknown | 0 |
| 515 | + δ) and | unknown | 134 |
| 545 | W⊤ | unknown | 0 |
| 547 | · ∥Dx(∆a)∥ | unknown | 7 |
| 551 | = O( 1√ | unknown | 179 |
| 569 | VERIFY LINEAR SEPARABILITY OF | unknown | 0 |
| 570 | ADVERSARIAL NOISES IN PRACTICE | unknown | 73 |
| 580 | General Setup of Experiments | unknown | 140 |
| 594 | Adversarial Noises Within Theoretical Regime | unknown | 556 |
| 653 | Adversarial Noises Beyond Theoretical Regime | unknown | 841 |
| 741 | CONCLUSION AND LIMITATION | unknown | 204 |
| 761 | References | references | 970 |
| 891 | Some Proofs in Theorem 3.1 | unknown | 0 |
| 892 | The Independent Case | unknown | 66 |
| 897 | ). We further | unknown | 30 |
| 901 | (23) | unknown | 41 |
| 918 | d | unknown | 50 |
| 929 | P | unknown | 91 |
| 954 | − z | unknown | 83 |
| 966 | (29) | unknown | 168 |
| 990 | P | unknown | 1 |
| 992 | NX | unknown | 16 |
| 1002 | K | unknown | 1 |
| 1004 | N | unknown | 16 |
| 1009 | P | unknown | 22 |
| 1023 | K | unknown | 39 |
| 1032 | and hence ∥aD∥2 | unknown | 4 |
| 1034 | , whose probability is at least | unknown | 61 |
| 1045 | (34) | unknown | 16 |
| 1047 | holds with probability at least | unknown | 23 |
| 1050 | Proof of Lemma 3.4 | unknown | 56 |
| 1055 | − 2Φ(− | unknown | 57 |
| 1064 | More Experiments | unknown | 92 |

Unrecognized headings: PROBLEM SETUP AND NOTATIONS; PROV ABLE LINEAR SEPARABILITY; OF ADVERSARIAL NOISES; Linear Separability at Initialization; = E; = E; + 5; X =Π⊥; A1; ˜XΠ⊥; A2 + Π⊥; A1 XΠA2; + ΠA1 XΠ⊥; Π⊥; W = ˜WΠ⊥; Linear Separability in NTK Regime; D∗; − δ, 1; + δ) and; W⊤; · ∥Dx(∆a)∥; = O( 1√; VERIFY LINEAR SEPARABILITY OF; ADVERSARIAL NOISES IN PRACTICE; General Setup of Experiments; Adversarial Noises Within Theoretical Regime; Adversarial Noises Beyond Theoretical Regime; CONCLUSION AND LIMITATION; Some Proofs in Theorem 3.1; The Independent Case; ). We further; (23); d; P; − z; (29); P; NX; K; N; P; K; and hence ∥aD∥2; , whose probability is at least; (34); holds with probability at least; Proof of Lemma 3.4; − 2Φ(−; More Experiments

## Rubric assessment

### C1 Research objective / questions — PRESENT
Rated PRESENT: 1 distinct indicator(s) found in the document (threshold 1).
- line 126 [Related work]: "There are some explanations why adversarial examples exist, e.g., the deep network classifiers being too linear locally because of ReLU like activations (Goodfellow et al., 2014), the boundary tilting hypothesis that th…"

### C2 Dataset / data source description — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (3 found elsewhere).
- line 65 [INTRODUCTION]: "More specifically, in this paper we argue that under some assumption adversarial noises are almost linearly separable if they are equipped with the labels of the corresponding original samples, i.e., a new constructed d…"
- line 96 [INTRODUCTION]: "The theory indicates that the linear separability of adversarial noises actually are generalizable to the test set, which is also verified in Figure 2."
- line 428 [W = ˜WΠ⊥]: "For the two-layer network defined in Equation 3 and the adversarial samples given byxadv i = xi+ηri, if d > poly(n) there exists v′ = −Π⊥ XW⊤a such that ∀i : ⟨v′, xadv i ⟩ > 0 with high probability."
- *Recommendation:* Describe the data source, how it was collected or selected, its size, and its train/test split or sampling procedure.

### C3 Experimental setup / procedure — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (5 found elsewhere).
- line 54 [INTRODUCTION]: "In this paper, we study the adversarial noises from a population’s perspective and ask “What property do the adversarial noises exhibit when they are put together?” Due to the complicated procedure of generating adversa…"
- line 103 [INTRODUCTION]: "We also empirically explore the property of adversarial noises beyond the theoretical regime, especially for the case where the neural network is trained with a large learning rate, the case of other adversarial noise g…"
- line 562 [= O( 1√]: "Second, it is desirable if one can extend the result to the PGD with respect to the l∞ constraint."
- *Recommendation:* Report the procedure step by step, including software/hardware environment and parameter settings, so the study could be repeated.

### C4 Evaluation metrics — WEAK
Rated WEAK: indicator(s) found only outside the methodology section(s) (1 found elsewhere).
- line 29 [INTRODUCTION]: "Modern deep learning models have achieved great accuracy on vast intelligence tasks."
- *Recommendation:* Name the evaluation metrics and explain why they fit the research question.

### C5 Baseline / comparison — PRESENT
Rated PRESENT: 1 distinct indicator(s) found in the document (threshold 1).
- line 453 [W = ˜WΠ⊥]: "By choosing η = d1/4, the adversarial noise is still small compared with the original signal, i.e., ∥xadv−x∥ ∥x∥ = O(d−1/4) but the effect of the adversarial noise overweighs that of the original signal, i.e., |⟨−W⊤a,xa…"

### C6 Statistical rigor / repeated trials — MISSING
Rated MISSING: no indicator for this criterion was found in the document.
- *Recommendation:* Report variability (e.g., standard deviation over repeated runs) and, where claims compare methods, a significance test or confidence interval.

### C7 Threats to validity / limitations — PRESENT
Rated PRESENT: 2 distinct indicator(s) found in the document (threshold 1).
- line 96 [INTRODUCTION]: "The theory indicates that the linear separability of adversarial noises actually are generalizable to the test set, which is also verified in Figure 2."
- line 750 [CONCLUSION AND LIMITATION]: "One limitation of the work is that we do not have a straightforward way to exploit such phenomenon to improve the adversarial attack or defense."

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
