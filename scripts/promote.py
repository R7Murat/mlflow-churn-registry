"""
Promotion gate — evaluates the @challenger model against quality gates
and promotes it to @champion if all checks pass.

Gates (cheapest first — fail fast):
  1. leakage_checked tag present
  2. ROC-AUC above minimum threshold
  3. train/test gap below maximum (overfitting guard)

On promotion: previous champion is preserved as @previous-champion (rollback).
Every decision (pass or fail) is appended to an audit log.
"""
import os
import sys
import json
import getpass
from datetime import datetime, timezone

import mlflow
from dotenv import load_dotenv

load_dotenv()

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "BankChurnModel")
MIN_ROC_AUC = float(os.getenv("PROMOTE_MIN_ROC_AUC", "0.80"))
MAX_GAP = float(os.getenv("PROMOTE_MAX_TRAIN_TEST_GAP", "0.05"))
AUDIT_LOG = "docs/demo-evidence/promotion-log.txt"


def audit(message: str) -> None:
    """Append a timestamped line to the audit log and print it."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {message}"
    print(line)
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def promote() -> bool:
    client = mlflow.MlflowClient(tracking_uri=TRACKING_URI)
    user = getpass.getuser()

    # ── Resolve challenger ────────────────────────────────────
    try:
        challenger = client.get_model_version_by_alias(MODEL_NAME, "challenger")
    except Exception:
        audit(f"REJECTED | no @challenger found for {MODEL_NAME} | by={user}")
        return False

    version = challenger.version
    run = client.get_run(challenger.run_id)
    tags = run.data.tags

    audit(f"EVALUATING | {MODEL_NAME} v{version} | by={user}")

    # ── Gate 1: leakage check (cheapest) ──────────────────────
    if tags.get("leakage_checked") != "true":
        audit(f"REJECTED | v{version} | reason=no leakage_checked evidence")
        return False

    # ── Gate 2: ROC-AUC threshold ─────────────────────────────
    test_auc = float(tags.get("test_roc_auc", 0.0))
    if test_auc < MIN_ROC_AUC:
        audit(f"REJECTED | v{version} | reason=ROC-AUC {test_auc:.4f} < {MIN_ROC_AUC}")
        return False

    # ── Gate 3: overfitting guard ─────────────────────────────
    train_auc = float(tags.get("train_roc_auc", 0.0))
    gap = train_auc - test_auc
    if gap > MAX_GAP:
        audit(f"REJECTED | v{version} | reason=overfit gap {gap:.4f} > {MAX_GAP}")
        return False

    # ── Idempotency: already champion? ────────────────────────
    try:
        current = client.get_model_version_by_alias(MODEL_NAME, "champion")
        if current.version == version:
            audit(f"NOOP | v{version} is already champion")
            return True
        # Preserve current champion for rollback
        client.set_registered_model_alias(MODEL_NAME, "previous-champion", current.version)
        audit(f"ROLLBACK-POINT | v{current.version} -> @previous-champion")
    except Exception:
        pass  # no existing champion — first promotion

    # ── Promote ───────────────────────────────────────────────
    client.set_registered_model_alias(MODEL_NAME, "champion", version)
    audit(f"PROMOTED | v{version} -> @champion | ROC-AUC={test_auc:.4f} gap={gap:.4f} | by={user}")
    return True


if __name__ == "__main__":
    ok = promote()
    sys.exit(0 if ok else 1)