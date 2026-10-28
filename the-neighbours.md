# The Neighbours

Loki is one answer to *the lines are
scattered; gather them*. Other tools
gather, index or dodge the question
differently, and an honest guide says
where each wins. These are characterised
from their designs and documentation,
not benchmarked — the lab ran only Loki.

## grep, find, and the journal

The oldest log system is a file and
`grep`, and on one machine it is still
hard to beat: no install, no store, the
text searched exactly. The systemd
**journal** (`journalctl`) adds structure
on a single Linux box — by unit, by time,
by priority — and for one machine's own
questions it is often the whole answer.
Loki earns its place at the moment the
question spans machines or outlives the
box: when the container is gone, the
journal rotated, the laptop asleep. If
your estate is one server you love, the
neighbours on your own disk may be all
you need, and this guide will not be
offended.

## Elasticsearch and OpenSearch

The full-text school: index the words,
all of them, and let any string be
findable at index speed, with rich
search, aggregations and a mature
ecosystem (Kibana; OpenSearch Dashboards)
around the store. For log *search* as a
product — support teams hunting arbitrary
strings across oceans of text — it is
the stronger instrument. The price is
the one chapter 1 quoted: the index is
large, the machines that hold it are
hungry, and running the cluster well is
a specialism. Loki's bargain is the
mirror image: weak at the arbitrary
string, cheap and calm at everything
label-shaped. Shops with both usually
route deliberately: search-heavy text to
the full-text store, service logs to
Loki, and no apology either way.

## Prometheus

Not a rival — the sibling. Prometheus
stores numbers with labels; Loki stores
lines with labels; Grafana draws both.
The working rule from chapter 1: a value
you will chart every day (latency,
counts, queue depth) should be *measured*
into Prometheus by the program itself,
not counted afterwards out of its log
lines — chapter 7's unwrapped quantiles
are a bridge, not a destination. But the
incident workflow belongs to the pair:
Prometheus says *errors began at 02:10*,
Loki shows the lines from 02:10, and the
labels that name the series name the
stream, because the two systems were
designed to share them.

## The other log stores

- **Graylog** — a log platform with its
  own store and interface, long popular
  in Windows-and-Linux estates; more
  all-in-one product, less
  build-it-from-parts than Loki.
- **VictoriaLogs** — a younger store from
  the VictoriaMetrics family, full-text
  indexed and proud of its efficiency;
  worth an honest look if Loki's
  unindexed text chafes.
- **Cloud logging** (CloudWatch, Google
  Cloud Logging, Azure Monitor) — the
  logs stay where the machines already
  are; priced per gigabyte and per query
  in ways that reward doing the sums
  before the first busy month.
- **A folder of files and a rotation
  policy** — the null neighbour. For a
  service that writes a log nobody reads
  until it breaks, rotated text files
  plus Loki later is a respectable life
  story; not every line needs a store
  from birth.

The pattern in every comparison is the
same: decide what your questions look
like — *by service and time*, or *by any
word ever written* — and the tool picks
itself. This guide exists because the
first shape of question is the common
one, and Loki answers it with the least
machinery that honestly can.
