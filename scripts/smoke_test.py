"""Smoke test — verifies the served model responds correctly before promotion."""
import sys
import time
import json
import urllib.request

SERVING_URL = "http://localhost:5001/invocations"

SAMPLE_INPUT = {
    "dataframe_records": [
        {
            "CreditScore": 650, "Geography": "France", "Gender": "Female",
            "Age": 40, "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
            "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000,
        }
    ]
}


def call_model(url: str, payload: dict, timeout: int = 10) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_smoke_test() -> bool:
    print("=== Smoke test: served churn model ===")

    start = time.time()
    try:
        result = call_model(SERVING_URL, SAMPLE_INPUT)
    except Exception as e:
        print(f"[FAIL] Request error: {e}")
        return False
    latency_ms = (time.time() - start) * 1000

    preds = result.get("predictions")
    if not preds or not isinstance(preds, list):
        print(f"[FAIL] Unexpected response shape: {result}")
        return False

    row = preds[0]

    # Check 1 — required fields present
    required = {"churn_probability", "churn_prediction", "risk_tier"}
    if not required.issubset(row.keys()):
        print(f"[FAIL] Missing fields. Got: {list(row.keys())}")
        return False

    # Check 2 — probability in valid range
    prob = row["churn_probability"]
    if not (0.0 <= prob <= 1.0):
        print(f"[FAIL] Probability out of range: {prob}")
        return False

    # Check 3 — prediction is binary
    if row["churn_prediction"] not in (0, 1):
        print(f"[FAIL] Prediction not binary: {row['churn_prediction']}")
        return False

    print(f"[PASS] Response valid")
    print(f"       probability : {prob}")
    print(f"       prediction  : {row['churn_prediction']}")
    print(f"       risk_tier   : {row['risk_tier']}")
    print(f"       latency     : {latency_ms:.0f} ms")
    return True


if __name__ == "__main__":
    ok = run_smoke_test()
    sys.exit(0 if ok else 1)