# Glossary

**Chunk** — a compressed block of lines
from one stream over one stretch of time;
the unit Loki stores, moves and deletes
(chapters 2, 10).

**Compactor** — the background component
that tidies the index and enforces
retention by deleting aged chunks
(chapter 10).

**count_over_time** — the LogQL metric
function that counts lines in a window;
the errors-per-hour chart's raw material
(chapter 7).

**Detected level** — in Loki 3.x, the
level (`info`, `warn`, `error`) the
server reads out of a line and attaches
as structured metadata (chapter 4).

**Distributor** — the write path's front
door: validates incoming lines and routes
them to the ingester that owns their
stream (chapter 2).

**Fake tenant** — the built-in tenant
named `fake` that owns everything when
`auth_enabled` is false (chapters 2, 10).

**Flush** — an ingester writing its
in-memory chunk to the store; happens by
age, size, or on request (chapter 10).

**Grafana Alloy** — Grafana's current
collector agent; the recommended shipper
for Loki, with `loki.source.*` and
`loki.write` components (chapter 8).

**High cardinality** — a label taking so
many values that streams multiply beyond
sense; the classic way a Loki install
dies (chapter 5).

**Index** — the catalogue of streams,
their labels and their chunks' locations.
Modern Loki uses the TSDB index; only
labels are in it, never line text
(chapters 1, 2).

**Ingester** — the component that holds
recent lines in memory, builds chunks,
and answers queries for what it holds
(chapter 2).

**Label** — a `name="value"` pair
attached to a stream at push time;
labels are the index, and the query's
first language (chapter 5).

**Label filter** — a pipeline stage
testing a field or metadata value, like
`| status >= 400` (chapters 6, 7).

**Line filter** — a pipeline stage testing
a line's text: `|=`, `!=`, `|~`, `!~`
(chapter 6).

**logcli** — Loki's command-line client:
the same queries as the HTTP API, output
as lines (chapter 9).

**logfmt** — the `key=value` line format,
and the parser that takes it apart at
query time (chapters 4, 7).

**LogQL** — Loki's query language: stream
selectors, pipelines, parsers and metric
functions (chapters 6, 7).

**Monolithic mode** — all of Loki in one
process; this guide's deployment shape
(chapter 2).

**Parser** — a pipeline stage (`logfmt`,
`json`, `pattern`, `regexp`) that
promotes pieces of a line's text to named
fields for one query (chapter 7).

**Promtail** — Loki's original shipper,
end of life since 2 March 2026; replaced
by Grafana Alloy (chapter 8).

**Push API** — `POST /loki/api/v1/push`,
the endpoint every shipper — and chapter
4's curl — uses to store lines.

**Querier** — the read path's worker:
fetches from ingesters and the store,
merges, deduplicates and sorts (chapter 2).

**Query frontend** — the read path's front
door: splits, queues and caches queries
(chapter 2).

**Retention** — how long stored lines are
kept before the compactor deletes them;
a policy decision with a setting, not a
default to inherit (chapter 10).

**Ruler** — the component that evaluates
LogQL metric queries as alerting and
recording rules (chapter 11).

**Shipper** — any program that reads logs
where they are written and pushes them to
Loki with labels attached (chapter 8).

**Stream** — all lines sharing one exact
set of labels; the address a selector
names (chapter 5).

**Stream selector** — the `{...}` that
opens every LogQL query, choosing streams
by their labels (chapter 6).

**Structured metadata** — per-line extras
attached without defining the stream,
like `detected_level`; filterable, not
part of a stream's identity (chapters 4, 5).

**Tenant** — one isolated owner's worth
of streams inside a shared Loki; chosen by
header when authentication is on
(chapter 2).

**TSDB index** — the current index format,
shared in design with Prometheus's,
storing label sets and chunk references
(chapters 2, 3, 10).

**Write-ahead log (WAL)** — the on-disk
journal that lets an ingester's memory
survive a crash (chapters 2, 10).
