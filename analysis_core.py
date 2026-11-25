"""Compare two ordered windows of HTTP request observations."""
from math import ceil, isfinite
from statistics import median


def summarize(requests):
    if not requests:
        raise ValueError("Each window needs at least one request")
    times = []
    failed = 0
    for latency, status in requests:
        if not isfinite(latency) or latency < 0 or not 100 <= status <= 599:
            raise ValueError("Invalid latency or HTTP status")
        times.append(latency)
        failed += status >= 500
    times.sort()
    return {
        "requests": len(times),
        "errors": failed,
        "error_pct": round(100 * failed / len(times), 3),
        "p50_ms": median(times),
        "p95_ms": times[ceil(.95 * len(times)) - 1],
    }


def compare(before, after):
    baseline, current = summarize(before), summarize(after)
    reasons = []
    if current["p95_ms"] > baseline["p95_ms"] * 1.25:
        reasons.append("p95 latency increased by more than 25%")
    if current["error_pct"] - baseline["error_pct"] > .5:
        reasons.append("HTTP 5xx rate increased by more than 0.5 percentage points")
    return {"before": baseline, "after": current,
            "verdict": "Review" if reasons else "Pass", "reasons": reasons}
