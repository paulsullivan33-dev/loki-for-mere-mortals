# LogQL — Parsing and Metrics

By the end of this chapter you can do the
two things that turn a pile of lines into
an instrument: pull named **fields** out
of a line's text at query time, test
them like labels, and **count lines over
time** so logs can be graphed and alerted
on like metrics. Nothing here changes
what is stored; parsing is reading, done
fresh on every query.

## Parsers: fields on demand

Chapter 5 kept interesting values —
`status`, `duration_ms`, `path` — inside
the line text, safe from the cardinality
cliff. A **parser** stage promotes them
to named fields for the rest of the
pipeline. The fixture's lines are
logfmt, so the lab used the logfmt
parser:

```logql
{service_name="api"} | logfmt
```

After that stage, every `key=value` in
the line is a field, and later stages can
test fields exactly like the metadata
filters of chapter 6. The lab's query
kept only the lines whose parsed
`status` was 400 or more:

```logql
{service_name="api"} | logfmt | status >= 400
```

Three lines returned: the 404, the 500
and the 503 (full answer in
`loki-lab/transcripts/t05-query-logfmt-and-metric.txt`).
Notice what made that query possible:
the comparison is **numeric**. Label and
field values are strings, but LogQL's
label filters understand numeric tests —
`>=`, `<`, a duration like
`duration_ms > 100`, a byte size — when
the field's contents parse as a number.
`| logfmt | status >= 400` is the single
most useful shape in this chapter; it is
how "show me the failures" stops meaning
"show me lines containing the word
error".

The other parsers, same idea, other
shapes of line:

- `| json` — fields from JSON lines, the
  natural partner of programs that log in
  JSON; nested fields are reachable with
  expressions like `| json level="level"`.
- `| pattern "<ip> - - <_> ..."` — pull
  named pieces out of a line that follows
  a fixed layout, common for web-server
  access logs.
- `| regexp "..."` — the same with a
  regular expression and named groups.

Two honest costs. Parsing is paid per
query, per line: on a wide selector over
a month of lines it is real work, and
the error you get from a line the parser
cannot digest is a field named
`__error__` attached to it, not a failed
query — filter it out or hunt it down,
but do not mistake its presence for your
data being broken. And fields exist only
for that query. Nothing is re-indexed;
tomorrow's identical query pays again.
That is the deal chapter 1 promised.

## Metric queries: lines into numbers

Wrap a log query in a function over a
time window and LogQL stops returning
lines and starts returning **series** —
the same result shape Prometheus
returns, plottable in Grafana and usable
in alerts. The lab counted error lines
across the whole fixture, five minutes at
a time:

```logql
count_over_time({job="lab"} |= "level=error" [5m])
```

Sent through `query_range` with
`step=5m`, it answered (`resultType:
matrix`) with one series per stream —
api: 1 error in one window, 1 in another;
worker: 1 — as the transcript t05 keeps.
The family is small and worth knowing
whole:

- `count_over_time({...} [5m])` — lines
  per window. The errors-per-hour chart,
  the heartbeat of a quiet service.
- `rate({...} [5m])` — the same count as
  a per-second rate; Prometheus habits
  transfer directly.
- `bytes_over_time(...)` — volume, for
  "which service shouts loudest".
- `sum by (service_name) (...)` and
  friends — metric queries accept the
  usual Prometheus-style aggregation, so
  `sum by` and `topk` behave as a
  Prometheus reader expects.
- **Unwrapped expressions** —
  `unwrap duration_ms` after a parser
  turns a field into a plottable value,
  feeding functions like
  `quantile_over_time(0.95, ...)`:
  the 95th-percentile request duration,
  computed from log lines. Powerful, and
  the point where chapter 13's question
  — *should this have been a metric all
  along?* — deserves a hearing.

## The bridge between the halves

Stand back and the shape of LogQL is one
idea used twice. The selector spends the
index to name a few streams; the pipeline
spends reading to test, parse and count
their lines. Filters answer *which
lines*; parsers answer *what is in them*;
metric functions answer *how many, how
often*. Every recipe in chapter 11 is a
combination of those three questions, and
every limit in chapter 13 is one of them
asked at a scale the bargain did not
budget for.

Check: on the fixture, `count_over_time`
over the full hour for `{service_name=
"api"} |= "level=error"` reports 2, and
the lab's logcli instant query in
transcript t06 reports api 2, worker 1.
If your counts agree, your parsers and
metrics are telling the truth about your
lines — the only foundation the rest of
the guide needs.
