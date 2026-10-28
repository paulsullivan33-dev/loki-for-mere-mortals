# Labels and Streams

By the end of this chapter you can choose
labels for a new log source and defend
the choice — because labels are the one
decision in Loki that is cheap today and
expensive to change your mind about.
Everything in chapter 1's bargain follows
from them: the index holds labels, so
labels decide what is findable, and how
much store you need to find it.

## A stream is a label set, exactly

A **stream** is all the lines that carry
the same set of labels — same names, same
values. `{job="lab", service_name="api"}`
is one stream. Change a single value —
`service_name="worker"` — and you are
looking at a different stream. Loki's
index is, in essence, a catalogue of
these sets and where their chunks live.
When chapter 4's query named two labels,
it was naming one row of that catalogue.

This means labels are not tags sprinkled
per line, like keywords on a photo. They
are the line's *address*. Two lines that
differ in any label live at different
addresses, in different chunks, and a
query must name the address before it may
read a single word.

## The labels the lab used, and why

The fixture pushed two labels:

- **`job`** — the collection the lines
  belong to (`lab` for the fixture; on a
  real machine, often the shipper's name
  for a group of sources).
- **`service_name`** — which service
  wrote the line (`api`, `worker`). Loki
  3.x treats `service_name` as the
  standard name for this idea; shippers
  set it automatically when they can.

Both have few possible values, change
rarely, and are exactly what a question
starts with: *the api's lines*, *the
worker's errors*. That is the shape of a
good label. Good candidates share it:
`hostname`, `environment` (`prod`,
`test`), `unit` for a systemd service,
`container` for a container name. A
question you will actually ask, answered
from a short list of values — that is a
label.

## The cardinality cliff

Now the warning this chapter exists for.
Every distinct label *set* is a stream,
every stream gets its own chunks and its
own index entries, so the number of
streams is the product of the values of
all the labels. A label whose value is
nearly unique per line — a request ID, a
user ID, a session token, an IP address
per visitor, a full file path with a date
in it — does not create a useful address.
It creates **millions of one-line
streams**, an index that dwarfs the logs,
an ingester drowning in bookkeeping, and
queries that crawl. This failure has a
name, **high cardinality**, and it is the
classic way a Loki install dies: not with
an error, but with a label somebody
thought would be handy.

The test is one question: *how many
different values will this label ever
take?* If the honest answer is "a
handful, ever" — label. If it is "it
grows with traffic" — that value belongs
*inside the line*, where chapter 7's
parsers can still pull it out at query
time (request IDs work perfectly well
that way), or in **structured metadata**:
per-line extras, like the `detected_level`
that appeared in chapter 4, which travel
with lines without defining streams.
Metadata is the middle shelf: filterable,
not indexed as identity, and the right
home for things like a trace ID.

## Rules of thumb worth keeping

- **Few labels, few values.** Two to five
  labels per stream is a healthy shape;
  thousands of streams is fine, millions
  is a smell.
- **Name things the Prometheus way.**
  Labels are `name="value"` pairs with
  lowercase names; `{service_name="api"}`
  will feel familiar to anyone who has
  met `{job="api"}` in PromQL, because
  the model is deliberately the same.
- **Same labels, same spelling,
  everywhere.** `service_name="api"` and
  `service_name="API"` are two streams.
  Let the shipper set them, consistently,
  rather than each program improvising.
- **Never put secrets in labels.** Labels
  are the index — the most visible,
  most queried part of the store. Chapter
  13 returns to this.
- **Changing labels later means a new
  stream**, and history stays under the
  old one. Queries can span both, but
  the tidy time to choose is before the
  first real push — which is to say, now.

Check your instincts against the fixture:
the lab's two labels produce exactly two
streams and an index you could write on
an envelope (`loki-lab/transcripts/t07-storage-on-disk.txt`
shows the whole store at 20 KB). Every
question in chapters 6 and 7 — by
service, by level, by status — is
answered from those two streams, because
the interesting differences were left in
the lines, where they belong.
