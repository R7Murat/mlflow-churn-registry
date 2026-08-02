"""
Rollback — reverts @champion to the previous known-good version.

Corrective control (vs promote.py's preventive gate): used when a model
passed the gate but misbehaves in production. Moves the current champion
to @rolled-back (audit trail) and restores @previous-champion to @champion.
"""
import os
import sys
import getpass
from datetime import datetime, timezone

import mlflow
from dotenv import load_dotenv

load_dotenv()

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "BankChurnModel")
AUDIT_LOG = "docs/demo-evidence/promotion-log.txt"


def audit(message: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {message}"
    print(line)
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def rollback() -> bool:
    client = mlflow.MlflowClient(tracking_uri=TRACKING_URI)
    user = getpass.getuser()

    # ── Resolve current champion ──────────────────────────────
    try:
        current = client.get_model_version_by_alias(MODEL_NAME, "champion")
    except Exception:
        audit(f"ROLLBACK-REJECTED | no @champion to roll back | by={user}")
        return False

    # ── Resolve rollback target ───────────────────────────────
    try:
        target = client.get_model_version_by_alias(MODEL_NAME, "previous-champion")
    except Exception:
        audit(f"ROLLBACK-REJECTED | no @previous-champion to restore | by={user}")
        return False

    if current.version == target.version:
        audit(f"ROLLBACK-NOOP | champion and previous-champion are both v{current.version}")
        return True

    audit(f"ROLLBACK-START | champion v{current.version} -> previous v{target.version} | by={user}")

    # ── Mark the bad champion (audit trail, not deleted) ──────
    client.set_registered_model_alias(MODEL_NAME, "rolled-back", current.version)

    # ── Restore previous champion ─────────────────────────────
    client.set_registered_model_alias(MODEL_NAME, "champion", target.version)

    # ── Clear previous-champion (it is champion again now) ────
    client.delete_registered_model_alias(MODEL_NAME, "previous-champion")

    audit(f"ROLLED-BACK | @champion restored to v{target.version} | "
          f"v{current.version} tagged @rolled-back | by={user}")
    return True


if __name__ == "__main__":
    ok = rollback()
    sys.exit(0 if ok else 1)