"""
Generates a human-readable Markdown evidence report of the current
MLOps pipeline state — container status, registry aliases, governance
tags, and promotion audit trail.

Output: docs/demo-evidence/pipeline-evidence.md (rendered on GitHub)
"""
import os
import subprocess
from datetime import datetime, timezone

import mlflow
from dotenv import load_dotenv

load_dotenv()

TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "BankChurnModel")
OUT_FILE = "docs/demo-evidence/pipeline-evidence.md"

client = mlflow.MlflowClient(tracking_uri=TRACKING_URI)
md = []


# ── Header ────────────────────────────────────────────────────
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
md.append("# MLflow Churn Registry — Pipeline Evidence\n")
md.append(f"_Generated: {ts}_\n")

# ── 1. Container status ───────────────────────────────────────
md.append("## 1. Container Status\n")
md.append("| Name | Service | Status |")
md.append("| --- | --- | --- |")
try:
    out = subprocess.run(
        ["docker", "compose", "ps", "--format",
         "{{.Name}}|{{.Service}}|{{.Status}}"],
        capture_output=True, text=True, timeout=15,
    ).stdout.strip()
    for line in out.splitlines():
        name, service, status = line.split("|")
        md.append(f"| `{name}` | {service} | {status} |")
except Exception as e:
    md.append(f"| _(could not read docker status: {e})_ | | |")
md.append("")

# ── 2. Registry aliases ───────────────────────────────────────
md.append("## 2. Model Registry — Aliases\n")
md.append("| Alias | Points to |")
md.append("| --- | --- |")
for alias in ["champion", "challenger", "previous-champion", "rolled-back"]:
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, alias)
        md.append(f"| `@{alias}` | {MODEL_NAME} v{mv.version} |")
    except Exception:
        md.append(f"| `@{alias}` | _(not set)_ |")
md.append("")

# ── 3. Governance tags of current champion ────────────────────
md.append("## 3. Governance — Current Champion\n")
md.append("| Property | Value |")
md.append("| --- | --- |")
try:
    champ = client.get_model_version_by_alias(MODEL_NAME, "champion")
    run = client.get_run(champ.run_id)
    t = run.data.tags
    train = float(t.get("train_roc_auc", 0))
    test = float(t.get("test_roc_auc", 0))
    md.append(f"| Version | v{champ.version} |")
    md.append(f"| Leakage checked | {t.get('leakage_checked', 'MISSING')} |")
    md.append(f"| Leakage method | `{t.get('leakage_method', 'MISSING')}` |")
    md.append(f"| Train ROC-AUC | {train:.4f} |")
    md.append(f"| Test ROC-AUC | {test:.4f} |")
    md.append(f"| Train/test gap | {train - test:.4f} |")
except Exception as e:
    md.append(f"| _(no champion set)_ | {e} |")
md.append("")

# ── 4. Promotion audit trail ──────────────────────────────────
md.append("## 4. Promotion Audit Trail\n")
audit_path = "docs/demo-evidence/promotion-log.txt"
if os.path.exists(audit_path):
    md.append("```")
    with open(audit_path, encoding="utf-8") as f:
        md.append(f.read().strip())
    md.append("```")
else:
    md.append("_(no audit log yet)_")
md.append("")

# ── Write ─────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
report = "\n".join(md) + "\n"
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print(f"[OK] Evidence report written to {OUT_FILE}")