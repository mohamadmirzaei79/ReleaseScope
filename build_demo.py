"""Generate a reproducible, offline release fixture and static report."""
import json
from pathlib import Path
from random import Random

from analysis_core import compare, summarize

RELEASES = [
    ("Checkout API", "checkout-api", "2.8.0", 11, 145, 1.65, .025),
    ("Search API", "search-api", "1.14.2", 19, 205, .81, .003),
    ("Events worker", "events-worker", "3.2.1", 31, 100, 1.04, .004),
]


def build():
    releases = []
    for name, service, version, seed, base, factor, errors in RELEASES:
        rng = Random(seed)
        buckets = []
        for i in range(24):
            scale = base * (factor if i >= 12 else 1)
            count = rng.randint(110, 165)
            buckets.append([(round(rng.lognormvariate(0, .28) * scale),
                             503 if rng.random() < (errors if i >= 12 else .003) else 200)
                            for _ in range(count)])
        before = [r for bucket in buckets[:12] for r in bucket]
        after = [r for bucket in buckets[12:] for r in bucket]
        releases.append(dict(service=name, slug=service, version=version,
                             buckets=[summarize(b) for b in buckets], **compare(before, after)))
    return {"bucket_minutes": 5, "releases": releases}


if __name__ == "__main__":
    Path(__file__).with_name("demo.json").write_text(json.dumps(build(), indent=2) + "\n")
