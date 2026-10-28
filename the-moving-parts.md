# The Moving Parts

By the end of this chapter you can name
the part of Loki responsible for any
behaviour you meet later: what takes a
line in, what keeps it, what answers a
query, and what lives outside the server
entirely. Loki can be deployed as a
village of specialised services; this
guide runs it as one program, and this
chapter explains both shapes so the small
one never feels like a different tool.

## One binary, several jobs

Loki is a single program that can run in
three shapes:

- **Monolithic mode** — one process doing
  every job. This is the lab's shape, the
  right shape for one person and a few
  machines, and what most of this guide
  assumes. Start it with a config file
  and it simply works.
- **Simple scalable mode** — the write
  path and the read path split into
  separate processes behind a load
  balancer, so a busy store can grow each
  side on its own. (Documented here, not
  run: the lab had one machine.)
- **Microservices mode** — every component
  below runs as its own service, scaled
  independently. This is how very large
  installations run, and it is operations
  work of its own; this guide points at
  it and stays with the first shape.

The components are the same in all three
shapes. In the lab they share one process
and one config file, but knowing their
names pays off the first time a log
message or an error mentions one.

## The write path: a line comes in

A log line arrives at the **distributor**,
which checks it against the limits —
labels valid, timestamp acceptable,
nothing malformed — and works out which
**ingester** owns its stream. The ingester
holds recent lines in memory, gathered
into **chunks**: compressed blocks of
lines from one stream over one stretch of
time. Periodically — or when told, as the
lab told it in chapter 10 — the ingester
**flushes** a finished chunk to the store,
and writes the stream's labels into the
**index**, so the stream can be found
later. A **write-ahead log** on disk lets
an ingester that crashes hand its memory
to its replacement rather than losing the
last minutes of lines.

Two consequences worth remembering.
Recent lines are queryable before they
are flushed — the ingester answers for
its memory as well as the store. And the
write path is where refusals happen:
chapter 14 meets the timestamp refusal
the lab provoked on purpose.

## The read path: a question goes out

A query arrives at the **query frontend**,
which can split a long question into
pieces, queue them, and cache answers.
The pieces run on **queriers**, which ask
two places and merge the results: the
ingesters, for lines still held in
memory, and the store, for flushed
chunks. Merging, deduplicating (chapter 4
watches a repeated push produce no second
copy of a line: the same timestamp and
text in one stream is stored once), and
sorting by time happen here, before the
answer travels back as JSON.

## What is kept, and where

Two kinds of data, kept apart on purpose:

- **Chunks** — the lines themselves,
  compressed. In the lab they are files
  under `data/chunks/`; at scale they are
  objects in S3, GCS or Azure storage.
  Chapter 10 photographs the lab's.
- **The index** — which streams exist,
  their labels, and where their chunks
  live. Modern Loki uses the **TSDB**
  index (the same family Prometheus
  uses), kept on the same store as the
  chunks and cached locally. The lab's
  `data/tsdb-shipper-*` folders are this
  index on its way to and from the
  filesystem store.

A **compactor** works in the background,
tidying the index and — the part you
will care about — enforcing **retention**:
deleting chunks older than the limit you
set. Chapter 10 covers both.

## Tenants: whose lines are these

Loki can serve many separate **tenants**
from one installation, each tenant's
lines invisible to the others, chosen by
a header on every request. The lab turned
authentication off (`auth_enabled: false`),
which collapses the world to a single
built-in tenant whose name, visible all
over the disk layout in chapter 10, is
literally `fake`. Remember that shape: a
real multi-user Loki is the lab's server
with the header switched on and names
where `fake` sits — and with real access
control being somebody's deliberate job,
not a default.

## The parts that are not Loki

Three neighbours complete the picture,
each with its own chapter:

- **Shippers** — the programs that read
  log files and journals on each machine
  and push lines to Loki with labels
  attached. Chapter 8: the family
  includes Grafana Alloy (the current
  recommendation), the now-retired
  Promtail, container log drivers and
  others. Loki itself reads nobody's
  files; something must bring the lines.
- **Grafana** — the usual viewing face:
  point it at Loki as a **data source**
  and browse, search and dashboard the
  lines in a browser. Chapter 9 describes
  the setup. It is a face, not the store:
  everything Grafana shows, the HTTP API
  underneath can answer too.
- **logcli** — Loki's own command-line
  client, the terminal face the lab used
  alongside raw curl. Same queries, less
  typing, output as lines instead of
  JSON.

Check the model holds: a line's life is
*shipper → distributor → ingester →
chunk + index → querier → you*, and every
chapter from here is one stretch of that
journey in detail.
