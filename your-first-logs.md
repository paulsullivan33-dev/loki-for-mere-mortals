# Your First Logs

By the end of this chapter ten real lines
are stored in your Loki, pushed by your
own hand over HTTP, and you have read
them back with a query. No shipper, no
Grafana: just the contract everything
else in the guide stands on — *this JSON
goes in, those lines come out.*

## The fixture: ten lines, two services

The lab's lines describe a small invented
web shop: an **api** service that serves
requests (and sometimes fails at it) and
a **worker** that runs batch jobs. Each
line is written in **logfmt**, the
`key=value` style that chapter 7 will
take apart:

```text
level=info msg="server started" port=8080 version=1.4.2
level=info method=GET path=/items status=200 duration_ms=12
level=error method=POST path=/checkout status=500 duration_ms=240 msg="payment gateway timeout"
```

Ten lines in all — seven from the api,
three from the worker, two of them
errors — generated with fresh timestamps
by `loki-lab/make_push.py`, which also
writes the request below. The services
do not exist. That is deliberate, and
chapter 1's rule is why: a learning lab
needs lines it may keep and publish, so
it invents them.

## The push request

Lines enter Loki through one endpoint,
`POST /loki/api/v1/push`, as JSON with
two levels of structure:

```json
{
  "streams": [
    {
      "stream": { "job": "lab", "service_name": "api" },
      "values": [
        ["1793161238883337011", "level=info msg=\"server started\" port=8080 version=1.4.2"],
        ["1793162018883337011", "level=error method=POST path=/checkout status=500 duration_ms=240 msg=\"payment gateway timeout\""]
      ]
    }
  ]
}
```

(The full ten-line request is in
`loki-lab/transcripts/t02-push.txt`.)
Three things to see in it:

- **`stream`** — the labels for every
  line in this block. All lines in a
  block, and only those, carry exactly
  these labels. Chapter 5 is devoted to
  choosing them well.
- **`values`** — pairs of *timestamp,
  line*. The timestamp is a string of
  **nanoseconds** since the Unix epoch —
  Loki wants nanosecond precision, and
  the line's own time is whatever the
  sender claims, which is why a lying or
  drifting clock is a data problem, not
  a display problem.
- **One request, many streams** — a real
  shipper batches hundreds of lines this
  way. The shape never changes.

Send it:

```bash
curl -s -X POST http://127.0.0.1:3100/loki/api/v1/push \
  -H 'Content-Type: application/json' \
  --data-binary @push.json -w '%{http_code}\n' -o response.txt
```

Check: the status is **204** and
`response.txt` is empty — zero bytes.
Silence is Loki's *yes*. A malformed
push gets a 400 and a written reason
instead; chapter 14 collects those.

## Asking for them back

Reading is the mirror endpoint,
`GET /loki/api/v1/query_range`, with a
**LogQL** query and a time range. The
simplest useful query is a **stream
selector** alone — the labels, in braces:

```bash
curl -s -G http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={job="lab", service_name="api"}' \
  --data-urlencode 'start=1793158000' \
  --data-urlencode 'end=1793163000' \
  --data-urlencode 'limit=20' \
  --data-urlencode 'direction=forward'
```

(`start` and `end` are epoch seconds
bracketing the fixture; use an hour ago
and now for your own lines.) The answer
is JSON: a `resultType` of `streams`,
then one entry per stream with its
labels and its `[timestamp, line]` pairs
— the push format coming home. The lab's
full answer is in
`loki-lab/transcripts/t03-query-selector.txt`,
and it holds one surprise worth meeting
early: the api stream came back as
*three* result streams, grouped by a
label nobody pushed — `detected_level`,
with values `info`, `warn` and `error`.
Loki 3.x reads the level word out of each
line and attaches it as **structured
metadata**: extra per-line information
that travels with the line, can be
filtered on (chapter 6 does), but is not
part of the stream's identity. The lines
themselves are unchanged.

## Where the lines are now

Not, at first, on disk. Your ten lines
are sitting in the ingester's memory,
already queryable, with the write-ahead
log as their safety net. They will be
flushed into a chunk file when the chunk
is old enough, full enough, or asked to
(chapter 10 asks). That delay is normal
and is why "I pushed it but the disk is
empty" is not a fault — chapter 14 lists
it under false alarms.

You now hold the whole loop: labels on,
JSON in, 204, selector, lines out.
Chapters 5 to 7 turn that loop into a
language; chapter 8 replaces your hand
with a shipper, so real machines can
join in.
