# Getting Logs In

By the end of this chapter you know how
real machines feed Loki: a small agent —
a **shipper** — on each machine reads its
log files and journals, attaches labels,
and pushes batches to the same endpoint
chapter 4 used by hand. This chapter is
the guide's honest exception: the lab
pushed by hand and ran no shipper, so
what follows is the map from the
project's documentation, labelled as
such, with the one fact in it that is
worth the whole chapter stated first.

## The fact: Promtail is finished

Most older Loki tutorials — many still on
the first page of any search — tell you
to install **Promtail**, Loki's original
shipper. Do not start there now.
Grafana's own documentation states that
**Promtail reached end of life on
2 March 2026**: no further updates, no
security fixes, and an explicit
instruction to migrate. Promtail still
*works*, and an existing setup is not an
emergency tonight; but a new install
should not begin with an unmaintained
agent that reads every log on the
machine — chapter 1's rule applied to
software choice. Configs are not wasted:
Alloy ships a converter
(`alloy convert --source-format=promtail`)
that translates a Promtail configuration
into its own.

## The current answer: Grafana Alloy

**Grafana Alloy** is Grafana's general
collector — one agent for logs, metrics
and traces, built as a pipeline of named
components wired together in a config
file. For Loki, three components do the
whole job, and their names are the
chapter in miniature:

- a **source** reads lines —
  `loki.source.file` for log files,
  `loki.source.journal` for the systemd
  journal, `loki.source.docker` for
  container logs;
- a **process** stage (`loki.process`)
  may reshape lines or attach values on
  the way past;
- `loki.write` is the destination: the
  Loki URL, and the labels each batch
  carries.

Labels deserve the sentence chapter 5
trained you for: the shipper is where
`hostname`, `unit`, `service_name` and
friends are attached, once, consistently,
for every line a machine sends. Get them
right in the shipper's config and every
later chapter works; improvise them per
program and no query will save you.

Alloy's own documentation is the
authority for its config syntax and
install; this guide does not reproduce a
pipeline it did not run. What the lab
*can* certify is the destination: every
component above ends at
`POST /loki/api/v1/push` with the JSON
shape of chapter 4.

## The other roads in

The push API is a public contract, so
Alloy is not the only traveller:

- **Container platforms.** Docker has a
  Loki log driver, and Kubernetes
  collectors (Alloy among them) gather
  pod logs with the pod's labels attached
  — the labels being half the value.
- **Other collectors.** Fluent Bit and
  Vector both speak Loki's push API
  natively and are reasonable choices
  where they are already the house agent.
- **The OpenTelemetry route.** Loki
  accepts OTLP log records, for shops
  standardising on OpenTelemetry
  collectors.
- **By hand.** A script and curl, exactly
  as chapter 4 did, is a legitimate
  shipper for one program's worth of
  lines — the contract is small enough
  to honour in twenty lines of Python.

## Whichever road: three duties

A shipper of any brand owes the store
three things, and a reader choosing one
can test any candidate against them:

- **It remembers where it stopped.** A
  shipper keeps a record of how far it
  has read in each file (Promtail called
  it the positions file; every serious
  agent has the equivalent), so a restart
  resumes instead of re-sending or
  skipping. Chapter 4's deduplication
  forgives a repeated batch; it does not
  forgive a skipped one.
- **It labels from facts, not guesses** —
  the file or unit the line came from,
  the machine it is on — attached the
  same way every time.
- **It respects the door.** Loki refuses
  what chapter 3 configured it to refuse
  (too-old lines among them); a shipper
  that falls a week behind will meet the
  refusal in transcript t08, and the
  right response is to notice, loudly,
  rather than to widen the door in a
  panic.

With a shipper on each machine, the
architecture of chapter 2 is alive: lines
flow in continuously, labelled at the
source, and the rest of this guide —
querying, viewing, keeping — applies to
real logs exactly as it did to ten
invented ones.
