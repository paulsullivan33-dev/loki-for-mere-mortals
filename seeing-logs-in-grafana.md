# Seeing Logs in Grafana

By the end of this chapter you know how
logs are viewed once they are stored:
Grafana in a browser for looking and
dashboards, logcli in a terminal for
asking from the command line. The lab
ran logcli against its server and kept
the transcripts; Grafana itself is
described here as a setup — honestly
labelled, per this guide's rules —
because the lab's verified faces are
the API and logcli, and a browser tour
leaves no transcript to keep.

## Grafana: the data source is the whole trick

Grafana does not store logs; it asks
Loki for them, using the same query API
as chapter 4. Connecting the two is one
form: in Grafana, add a **data source**
of type *Loki* and give it the server's
address — `http://localhost:3100` when
they share a machine, or the Loki host's
name and port on a network. Save and
test; Grafana checks the labels endpoint
(the very one transcript t01 shows
answering) and reports the connection.

From there, **Explore** is the working
surface: pick the Loki data source,
choose labels from dropdowns Grafana
builds out of the label endpoint, add
filters in a query box that speaks the
LogQL of chapters 6 and 7, and the lines
appear as a scrollable, time-ordered
list, with a bar strip above them showing
line volume per moment — the count metric
of chapter 7, drawn automatically. Two
Explore habits carry over from this
guide unchanged: narrow by labels before
filtering by text, and treat an empty
answer as a time-range question first
(chapter 14).

**Dashboards** are Explore queries that
stayed: a panel charting
`sum(count_over_time({job="lab"} |= "level=error" [5m]))`
is an errors-per-window graph any team
can glance at, and a logs panel pinned
under a metrics chart — same time range,
same service — is the combination Grafana
Labs built Loki for: *the numbers say it
broke at 02:10; the panel below shows the
lines from 02:10.* Log-based **alerts**
(close the loop by having Grafana or
Loki's ruler component evaluate a metric
query on a schedule and notify when it
crosses a line) are described in
chapter 11's last recipe; their
configuration lives in Grafana's and
Loki's documentation and is not
reproduced here, because the lab did not
run them.

If the Prometheus and Grafana guide in
this series is on your shelf, all of this
will feel familiar: one more data source,
one more query language that rhymes with
PromQL, the same dashboards wearing a
second kind of evidence.

## logcli: the terminal face, verified

**logcli** is Loki's own client, the same
release as the server, and everything it
does is the HTTP API with better manners.
The lab ran it against the local server
(transcript t06) with one setting:

```bash
export LOKI_ADDR=http://127.0.0.1:3100
```

Three commands from that session, worth
making reflexes:

```bash
logcli labels
logcli query '{service_name="api"} |= "level=error"' --since=1h --limit=5
logcli instant-query 'count_over_time({job="lab"} |= "level=error" [1h])'
```

- `labels` lists what the index knows —
  the fastest sanity check that a server
  holds anything at all.
- `query` runs a range query and prints
  bare lines, newest first unless
  `--forward` says otherwise, each
  prefixed with its timestamp. It is the
  natural tool for scripts and for the
  *grep, but across every machine* moment.
- `instant-query` evaluates a metric
  query at a point in time and prints the
  resulting series as JSON — the lab's
  answer counted error lines per stream
  (api 2, worker 1), agreeing with the
  raw API's count in chapter 7, as it
  must: same server, same questions.

logcli also speaks multi-tenant Loki
(point `LOKI_ADDR` at a real server, add
credentials and a tenant with
`LOKI_ORG_ID`); the lab's single-tenant
server needed none of it. Where Grafana
is the face for watching, logcli is the
face for asking once, precisely, and
keeping the answer in a file — which is
why this guide's evidence is written in
it.
