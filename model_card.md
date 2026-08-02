# Model Card — Bank Customer Churn Predictor

**Model name:** BankChurnModel
**Version:** v1 (`@champion`)
**Type:** Binary classification (churn / no-churn)
**Framework:** scikit-learn RandomForest, wrapped as MLflow pyfunc
**Owner:** Murat Arseven

---

## What this model IS

- A propensity model that estimates the probability a bank customer
  will churn (close their account / leave), based on demographic and
  account-activity features.
- Intended as a **decision-support** tool: to rank customers by churn
  risk so retention teams can prioritise outreach.
- Trained on the public **Kaggle "Churn Modelling"** dataset (10,000
  customers, 10 features).

## What this model is NOT

- **NOT trained on real bank data.** The dataset is a public,
  synthetic-style Kaggle dataset used for demonstration. Predictions
  must not be used for real customer decisions without retraining on
  validated production data.
- **NOT a causal model.** It identifies correlation with churn, not
  the cause. A high score does not explain *why* a customer may leave.
- **NOT fairness-audited.** The model has not been tested for
  demographic bias (e.g. across geography or gender). Any production
  use requires a fairness assessment first.

---

## Intended use

| | |
| --- | --- |
| Primary users | Retention / CRM teams (via ranked risk lists) |
| Decision type | Prioritisation, not automated action |
| Out of scope | Credit decisions, automated account closure, pricing |

---

## Performance

Evaluated on a held-out test set (15% stratified split, seed=42).

| Metric | Value |
| --- | --- |
| ROC-AUC | 0.858 |
| PR-AUC | 0.682 |
| Accuracy | 0.799 |
| Precision | 0.505 |
| Recall | 0.729 |
| F1 | 0.596 |

**Operating point:** decision threshold = **0.58** (tuned for F1,
not the default 0.5). Probabilities above 0.58 are classified as churn.

**Reading these numbers:** This is an imbalanced problem (~20% churn),
so ROC-AUC (0.858) and PR-AUC (0.682) are the primary metrics —
accuracy alone is misleading here. Recall (0.729) is intentionally
higher than precision (0.505): in churn retention, missing a customer
who will leave (false negative) is more costly than a wasted outreach
to a loyal one (false positive). The operating point is tuned to favour
recall accordingly.

**Risk tiers** (business-facing output):
`0–0.3 Low` · `0.3–0.5 Medium` · `0.5–0.7 High` · `0.7–1.0 Critical`

---

## Data leakage handling

- ID-type columns (`RowNumber`, `CustomerId`, `Surname`) are dropped
  **before** the train/test split, preventing identifier leakage.
- Verified via the `leakage_checked=true` governance tag, which the
  promotion gate (`scripts/promote.py`) enforces before any model can
  become `@champion`.

## Reproducibility

- Fixed seed (`RANDOM_SEED=42`) for split, sampling, and model init.
- Pinned dependencies in `requirements.txt`.
- Note: results were originally produced on Kaggle with slightly older
  library versions; local re-runs use the pinned versions here and may
  differ in the last decimal. Reproducibility is guaranteed at the
  seed/split level, not across library versions.

---

## Model lifecycle

- New models are registered as `@challenger`.
- Promotion to `@champion` requires passing the gate: leakage check,
  ROC-AUC ≥ 0.80, and train/test gap ≤ 0.05 (overfitting guard).
- The previous champion is retained as `@previous-champion` for rollback.
- Every promotion decision is recorded in `docs/demo-evidence/promotion-log.txt`.