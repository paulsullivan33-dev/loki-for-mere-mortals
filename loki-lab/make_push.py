#!/usr/bin/env python3
"""Build the lab's Loki push request: two streams of logfmt lines
for a small invented web service. Writes push.json and prints it."""
import json
import time

NOW_NS = time.time_ns()
MIN = 60 * 1_000_000_000


def ts(minutes_ago, extra_seconds=0):
    return str(NOW_NS - minutes_ago * MIN - extra_seconds * 1_000_000_000)


api_lines = [
    (25, 'level=info msg="server started" port=8080 version=1.4.2'),
    (22, "level=info method=GET path=/items status=200 duration_ms=12"),
    (19, "level=info method=GET path=/items/42 status=200 duration_ms=9"),
    (16, "level=warn method=GET path=/old-page status=404 duration_ms=3"),
    (12, 'level=error method=POST path=/checkout status=500 duration_ms=240 msg="payment gateway timeout"'),
    (9, "level=info method=POST path=/checkout status=200 duration_ms=131"),
    (5, 'level=error method=GET path=/items status=503 duration_ms=502 msg="upstream unavailable"'),
]

worker_lines = [
    (20, 'level=info msg="job started" job_name=nightly-export'),
    (15, 'level=info msg="job finished" job_name=nightly-export processed=512'),
    (7, 'level=error msg="job failed" job_name=thumbnailer error="cannot read image"'),
]

payload = {
    "streams": [
        {
            "stream": {"job": "lab", "service_name": "api"},
            "values": [[ts(m), line] for m, line in api_lines],
        },
        {
            "stream": {"job": "lab", "service_name": "worker"},
            "values": [[ts(m), line] for m, line in worker_lines],
        },
    ]
}

with open("push.json", "w") as f:
    json.dump(payload, f, indent=2)

print(json.dumps(payload, indent=2))
print("now (ns):", NOW_NS, file=__import__("sys").stderr)
