# What Loki Is

A program writes a **log line** when
something happens: it started, it served
a request, it failed at a thing. The line
is text, stamped with a time, and it
usually lands in a file on the machine
that wrote it. That is fine while there
is one machine. It stops being fine
quickly: the web service on one box, the
worker on another, the database on a
third, and a question like *what happened
just before the errors started?* becomes
an afternoon of logging into boxes and
reading files in the wrong order.

**Loki is a store for log lines.** Programs
(or small agents acting for them) send
their lines to one Loki server, and Loki
keeps them — compressed, ordered by time,
and findable. You ask for lines with a
query language called **LogQL**, and the
answer comes back as the lines themselves,
or as numbers counted from them. Loki is
made by Grafana Labs, the people behind
the Grafana dashboards, and it is built
deliberately in Prometheus's image.

## The one idea: index the labels, not the text

Full-text log systems — Elasticsearch is
the famous one — read every line, break
it into words, and build an index of
*where each word appears*. That makes any
word findable, and it costs what it
sounds like: big indexes, hungry servers.

Loki refuses that bargain. When a line
arrives, Loki looks only at its **labels**:
a small set of name-and-value pairs the
sender attached, like
`service_name="api"` or `job="lab"`. A set
of lines sharing the same labels forms a
**stream**. Loki indexes the labels, so a
stream can be found instantly, and stores
the lines themselves compressed in
**chunks**, unread. A query therefore
works in two steps: the labels pick the
streams (fast, indexed), then Loki opens
those streams and scans the lines inside
them (honest work, but only within the
streams you named).

That is the whole trade, stated once
because every later chapter leans on it:

- **Cheap to run.** A small index and
  compressed text mean one modest machine
  can hold a lot of logs.
- **Fast when you know where to look.**
  *Errors from the api service* is a label
  question, answered at once.
- **Deliberate when you don't.** *Find the
  line containing this rare string*
  means scanning — Loki will do it, at
  reading speed, not index speed.

If that sounds like Prometheus, it is
meant to: same label model, same style of
query language, same operating habits. If
you know Prometheus, chapter 2 will feel
like meeting a sibling. If you don't, the
Prometheus and Grafana guide in this
series teaches the metrics half; this
guide stands on its own without it.

## The rule, stated before everything else

A log store gathers the words of every
program on every machine it serves, and
programs write careless things: usernames,
email addresses, session tokens, the
occasional password a debugging line
should never have printed, fragments of
other people's private data. Collecting
logs into one place concentrates all of
that into one searchable pile. So this
guide has one rule, and it is not fine
print:

> **Collect only logs that are yours —
> from machines you own, or where every
> party involved has given you explicit
> permission.**

Your own servers: yes. A work system you
are employed to operate, within the
policies that govern it: that is the
permission talking, and chapter 13 has
more to say about retention and access.
A machine you were merely handed a login
for once, a housemate's or customer's
logs "to have a quick look": no. The lab
in this guide went further than most
readers will need to: every line it
stored was invented by the lab itself,
written by a small generator script,
describing two services that do not
exist.

## A first taste

After installing (chapter 3), the lab's
whole first hour fits in three commands.
Start the server:

```bash
./loki-linux-amd64 -config.file=loki-local.yaml
```

Push two streams of lines over HTTP —
chapter 4 shows the request in full; its
shape is JSON naming the labels and the
lines:

```bash
curl -X POST http://127.0.0.1:3100/loki/api/v1/push \
  -H 'Content-Type: application/json' \
  --data-binary @push.json
```

A quiet **204** with no body means
*stored*. Then ask for some of it back:

```bash
curl -G http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service_name="api"} |= "level=error"'
```

Check: the lab's version of that query
returned exactly two lines — the two its
fixture had marked as errors — and
`loki-lab/transcripts/t04-query-line-filters.txt`
keeps the full answer as evidence.

## Who it is for

The person running a handful of machines
or services who is tired of the SSH tour.
The home-lab keeper whose containers
recreate themselves and take their logs
with them. The developer who keeps a
week of logs "just in case" and wants the
week searchable. The common thread is one
person, their own machines, and questions
that begin *show me the lines where…*

## What it is not

Loki is not a full-text search engine:
the text is stored, not indexed, and
chapter 13 is blunt about what that costs
a certain kind of question. It is not a
metrics system: it can count lines and
turn the counts into numbers (chapter 7),
but a value you will chart every day
belongs in Prometheus proper. It is not
an archive of record: retention is a
setting, old lines are refused and later
deleted by design, and anything you must
*prove* later deserves a sterner home.
And it is not a security tool: it will
faithfully store a password a program
shouted into its logs, which is a reason
to fix the program, not to blame the
store.
