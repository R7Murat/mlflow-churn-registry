# MLflow Churn Registry — Pipeline Evidence

_Generated: 2026-08-02 17:45 UTC_

## 1. Container Status

| Name | Service | Status |
| --- | --- | --- |
| `mlflow-model-serving` | serving | Up 37 seconds (healthy) |
| `mlflow-tracking-server` | tracking-server | Up 16 minutes (healthy) |

## 2. Model Registry — Aliases

| Alias | Points to |
| --- | --- |
| `@champion` | BankChurnModel v1 |
| `@challenger` | BankChurnModel v2 |
| `@previous-champion` | _(not set)_ |
| `@rolled-back` | BankChurnModel v2 |

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
[2026-08-02 17:34:37 UTC] EVALUATING | BankChurnModel v1 | by=MRT
[2026-08-02 17:34:37 UTC] PROMOTED | v1 -> @champion | ROC-AUC=0.8579 gap=0.0084 | by=MRT
[2026-08-02 17:39:08 UTC] EVALUATING | BankChurnModel v2 | by=MRT
[2026-08-02 17:39:09 UTC] ROLLBACK-POINT | v1 -> @previous-champion
[2026-08-02 17:39:09 UTC] PROMOTED | v2 -> @champion | ROC-AUC=0.8579 gap=0.0084 | by=MRT
[2026-08-02 17:39:54 UTC] ROLLBACK-START | champion v2 -> previous v1 | by=MRT
[2026-08-02 17:39:54 UTC] ROLLED-BACK | @champion restored to v1 | v2 tagged @rolled-back | by=MRT
```

