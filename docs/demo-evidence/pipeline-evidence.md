# MLflow Churn Registry — Pipeline Evidence

_Generated: 2026-08-02 15:32 UTC_

## 1. Container Status

| Name | Service | Status |
| --- | --- | --- |
| `mlflow-model-serving` | serving | Up 13 minutes (healthy) |
| `mlflow-tracking-server` | tracking-server | Up 3 hours (healthy) |

## 2. Model Registry — Aliases

| Alias | Points to |
| --- | --- |
| `@champion` | BankChurnModel v1 |
| `@challenger` | BankChurnModel v1 |
| `@previous-champion` | _(not set)_ |

## 3. Governance — Current Champion

| Property | Value |
| --- | --- |
| Version | v1 |
| Leakage checked | true |
| Leakage method | `id_columns_dropped_before_split` |
| Train ROC-AUC | 0.8663 |
| Test ROC-AUC | 0.8579 |
| Train/test gap | 0.0084 |

## 4. Promotion Audit Trail

```
[2026-08-02 15:15:19 UTC] EVALUATING | BankChurnModel v1 | by=MRT
[2026-08-02 15:15:19 UTC] PROMOTED | v1 -> @champion | ROC-AUC=0.8579 gap=0.0084 | by=MRT
```

