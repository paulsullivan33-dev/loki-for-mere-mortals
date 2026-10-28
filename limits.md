# Limits

What Loki cannot do, and what it must not
be asked to do — the chapter the rest of
the guide has been promising.

## The text is not indexed

Everything else in this chapter is a
footnote to chapter 1's bargain, and this
is its sharpest edge. Loki indexes
labels; the words inside a line are just
stored. So the question *which lines,
anywhere, mention this string* is
answered by opening streams and reading —
fine within a service and an hour, slow
across a fleet and a season, and never
the sub-second magic a full-text index
performs. If your real work is arbitrary
search over all text, chapter 12's
full-text neighbours are not the enemy;
they are the right tool, and forcing
Loki into their job makes it look bad at
something it never claimed. The
mitigations are habits, not settings:
label so the selector is narrow, parse
so the fields are testable, and keep the
interesting differences findable by
structure rather than by hope.

## Labels can explode, quietly

Chapter 5's cliff deserves its place
here too, stated as a limit: Loki does
not protect you from a high-cardinality
label. It will accept the request-ID
label, build the million streams, grow
the index, slow the queries, and report
no error at any point — the failure is
arithmetic, delivered gradually. The
guardrails are yours: review every label
a shipper attaches, ask the chapter 5
question of it (*how many values, ever?*),
and treat a sudden growth in stream
count as an incident, not a curiosity.

## Time is strict, in both directions

Loki stores lines under the timestamps
their senders claim, and guards them:

- **Too old is refused.** The lab set a
  seven-day door and watched a ten-day-old
  line turned away with HTTP 400. A
  shipper that falls behind, or a machine
  whose clock is wrong, loses lines at
  that door — by design, and silently
  unless somebody watches for the
  refusals.
- **Duplicates collapse.** The same line
  at the same timestamp in one stream is
  stored once (chapter 4's repeated push
  changed nothing). Honest retries are
  forgiven; so is, on occasion, a genuine
  second occurrence that happened to be
  identical in the same nanosecond —
  rare, real, and the price of safe
  retries.
- **Clocks are content.** A machine an
  hour wrong writes an hour of lies into
  the record, in order, findable only
  where the lie put them. Synchronised
  time is not housekeeping for a log
  store; it is data quality.

## Logs are other people's words

A central log store concentrates exactly
the data privacy rules exist for: names,
addresses, identifiers, fragments of
messages, and — regularly, in every real
estate — credentials that some program
printed and nobody noticed. Chapter 1's
rule (*your logs, your machines, or
explicit permission*) has three working
consequences here:

- **Access is a decision.** The lab's
  server has no login at its port; that
  was a lab on one machine, not a model.
  A shared Loki needs its tenancy,
  authentication and network placement
  chosen by a person, on purpose.
- **Retention is a decision** — chapter
  10's settings exist so "forever, by
  accident" is not the policy.
- **Redaction belongs at the source.**
  The password in the log line should
  never have been printed; the store
  faithfully keeping it is the symptom,
  not the disease. Fix the printing, and
  treat existing stores as secrets when
  you copy, export or back them up —
  because that is what they are.

## One server is not a cluster

Everything this guide verified ran on
one process with `replication_factor: 1`
and an in-memory ring: if that process
dies, queries stop; if its disk dies,
the chunks on it are gone. Loki's other
shapes (chapter 2) exist precisely to
remove those sentences, at the cost of
operating several components and a real
object store — work this guide labelled
documented-only because the lab could
not honestly rehearse it. Do not let the
lab's calm single server testify about
availability it never had. The step from
*my logs, findable* to *our logs,
dependable* is a deployment project, and
it deserves to be planned as one.

## And it is not a metrics system

Chapter 7 counted lines and unwrapped
durations, and those are honest tricks.
They remain tricks. A number the
business watches belongs in a metrics
system, measured at the source; a log
line is evidence, written for humans,
inconsistent in shape, and an expensive
place to keep a graph's raw material.
Loki's designers say the same: logs for
the story, metrics for the numbers,
traces for the path — and one Grafana
over all three.
