# Loki for Mere Mortals

Every program you run writes
**log lines**: *started*, *served a
request*, *something went wrong*. On one
machine you can read them where they
land. On five machines they are scattered
across five disks, in five formats, and
the one line that explains last night's
failure is never on the machine you are
looking at. **Loki** gathers those lines
into one store and lets you ask for them
by meaning: *show me the errors from the
checkout service between two and three
this morning.*

Loki comes from Grafana Labs and is built
like Prometheus, on purpose. Prometheus
stores numbers, each series named by a
small set of **labels**; Loki stores log
lines, each **stream** named by a small
set of labels, with the lines themselves
kept compressed and unindexed. That one
decision — index the labels, not the
text — is the whole design, and this
guide keeps returning to it, because it
explains Loki's speed, its cheapness, and
its limits in a single stroke.

This guide explains how that works, how
to run one Loki server on one machine,
how to push your first lines into it over
HTTP, and how to ask questions in
**LogQL**, Loki's query language:
selecting streams, filtering lines,
parsing fields out of the text, and
counting lines over time the way PromQL
counts numbers. It covers how logs get
in from real machines, what the storage
looks like on disk, and when to reach
for something else instead.

The rule that governs everything here is
stated in chapter 1 and returned to in
chapter 13: **your logs, your machines,
or logs you have explicit permission to
collect.** Log lines are other people's
words more often than we remember —
usernames, addresses, the occasional
password somebody printed by mistake —
and a store that gathers every machine's
logs into one place gathers all of that
too. The lab obeyed the rule strictly:
every line it stored was a line it
invented itself.

The lab behind this guide ran the real
thing: **Loki 3.7.9**, the official
release binary, in single-binary mode
with a short configuration file and
ordinary filesystem storage, on one
small Linux machine. Against it the lab
pushed ten log lines in two labelled
streams through the HTTP API and read
them back four ways — by label selector,
by text filter, through a logfmt parser
with a numeric test on a parsed field,
and as a count over time — then asked
the same questions again through
**logcli**, Loki's command-line client.
It flushed the memory store to disk and
photographed what landed there, pushed
the same payload twice to watch
deduplication decline the second copy,
and pushed a line ten days old to watch
the server refuse it, politely and by
name.

What the lab could not do, it did not
fake. One machine cannot be a cluster,
so the multi-node deployment, real
multi-tenancy, and the cloud object
stores (S3, GCS, Azure) are taught from
the documentation and labelled as such
wherever they appear. Grafana's Explore
view and dashboards are described as a
setup rather than driven, and no log
shipper was run: chapter 8 explains from
Grafana's own documentation that
Promtail is end of life and names its
replacement, Grafana Alloy. `criteria.md`
keeps the full ledger of what was run
and what was only read.

## What this guide covers

- [**What Loki is**](what-loki-is.md) —
  the mental model: Prometheus's shape
  applied to log lines, labels and
  streams, and the ethics that are part
  of the tool, not an afterthought
- [**The moving parts**](the-moving-parts.md) —
  one binary or many: the write path,
  the read path, chunks and the index,
  tenants, shippers, and which part
  holds what
- [**Installing Loki**](installing-loki.md) —
  the official binary, the configuration
  file that makes it a local store, and
  the first start's readiness check
- [**Your first logs**](your-first-logs.md) —
  pushing real lines over HTTP, reading
  the 204, and asking for them back with
  a first LogQL query
- [**Labels and streams**](labels-and-streams.md) —
  what a stream is, which labels to
  choose, and the cardinality cliff to
  stay away from
- [**LogQL — selecting and filtering**](logql-selecting-and-filtering.md) —
  stream selectors and the four line
  filters: contains, excludes, regex,
  not-regex
- [**LogQL — parsing and metrics**](logql-parsing-and-metrics.md) —
  pulling fields out of lines with
  parsers, testing them, and turning
  lines into numbers with metric queries
- [**Getting logs in**](getting-logs-in.md) —
  shippers: Promtail's end of life,
  Grafana Alloy, container and journal
  routes, and the push API underneath
  them all
- [**Seeing logs in Grafana**](seeing-logs-in-grafana.md) —
  the data source, Explore, and
  dashboards, described as a setup,
  plus logcli for the terminal
- [**Storage and retention**](storage-and-retention.md) —
  chunks and the TSDB index on disk,
  what the lab's ten lines actually
  occupied, and keeping data for exactly
  as long as you mean to
- [**Recipes**](recipes.md) — count the
  errors per hour, find the one line,
  watch a deploy, and turn a log pattern
  into an alert
- [**The neighbours**](the-neighbours.md) —
  grep and the journal, Elasticsearch
  and OpenSearch, Prometheus itself,
  and when each beats Loki or loses to it
- [**Limits**](limits.md) — the text is
  not indexed, labels can explode, old
  lines are refused, logs are sensitive,
  and one server is not a cluster
- [**Troubleshooting**](troubleshooting.md) —
  the empty query, the rejected line,
  the missing stream, and the traps this
  guide's lab verified so you don't
  have to guess at them
- [**Glossary**](glossary.md) — the
  terms, collected in one place

## What it doesn't cover

Running Loki as a multi-node cluster for
an organisation — replication, sharding,
tenant quotas, the operational care of a
system other teams depend on. That is
real work, pointed at from chapters 2
and 10, not taught; this guide stays
with one server you run yourself, where
the tool does its honest work. It also
does not teach collecting logs you have
no right to: chapter 13 explains why a
log store concentrates exactly the data
that deserves care.

## How to use this guide

Read chapter 1 for the model and the
rules, and chapter 2 before installing
anything — knowing which part holds what
turns later confusion into a named
problem. Chapter 4 stores your first
lines in the same sitting as the
install; keep the fixture small and
invented until the queries feel boring.
Chapters 6 and 7 are the heart: LogQL is
a small language, and an hour with it on
ten known lines teaches more than a week
of reading. Chapter 5 deserves its
warning read twice — labels are the one
decision that is expensive to change
your mind about. The lab's transcripts
live in `loki-lab/transcripts/`; its
configuration is `loki-lab/loki-local.yaml`
and its line generator is
`loki-lab/make_push.py`.

---

## Part of the series

This guide is one of the [For Mere Mortals](https://paulsullivan33-dev.github.io/mere-mortals/) guides: plain-language guides to the tools programmers and makers use.

Related guides:

- [Prometheus and Grafana for Mere Mortals](https://paulsullivan33-dev.github.io/prometheus-and-grafana-for-mere-mortals/)
- [Watching Your System for Mere Mortals](https://paulsullivan33-dev.github.io/watching-your-system-for-mere-mortals/)
- [systemd for Mere Mortals](https://paulsullivan33-dev.github.io/systemd-for-mere-mortals/)

## License

The writing in this guide is licensed under [CC BY 4.0](https://github.com/paulsullivan33-dev/loki-for-mere-mortals/blob/main/LICENSE). Code examples and lab scripts are licensed under the [MIT License](https://github.com/paulsullivan33-dev/loki-for-mere-mortals/blob/main/LICENSE-CODE).
