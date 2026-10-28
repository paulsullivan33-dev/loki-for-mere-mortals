# Recipes

Four jobs Loki is asked to do constantly,
each one a combination of the pieces from
chapters 6 and 7. Every query below runs
against the lab's fixture or a light
generalisation of it, and each ends with
the check that tells you it worked.

## 1. Count the errors, per service, per hour

The morning question: *did anything break
overnight, and what?* Count first, read
second:

```logql
sum by (service_name) (
  count_over_time({job="lab"} |= "level=error" [1h])
)
```

On the fixture this reports api 2,
worker 1 for the lab's hour — the same
numbers chapters 7 and 9 each verified by
a different road. In Grafana the same
expression, ranged, is the errors panel
of chapter 9. Check: the counts add up
to the error lines a plain filtered query
returns for the same window; if they
don't, a filter differs between the two,
and the count is the one to distrust
second.

## 2. Find the one line

An error message, a request ID, a name —
something rare, in a known service, on a
known day. Selector tight, then the text:

```logql
{service_name="api"} |= "payment gateway timeout"
```

One line returns. Widen one notch at a
time if it doesn't: drop the text to a
shorter fragment, widen the time range
before widening the labels, and remember
chapter 6's arithmetic — the scan is only
ever as wide as the selector you gave it.
For a value you know is *inside* the
lines, like an order number, this recipe
is the whole tool; there is no index of
the text to consult, and chapter 13
explains why that is a design and not an
oversight. Check: quote a distinctive
phrase from a line you can already see in
the stream and confirm the filtered query
returns exactly that line.

## 3. Watch a deploy

A new version goes out; you want its
first minutes, live, and nothing else's.
The shipper labels carry the version only
if someone planned it (chapter 5's sermon
again) — but the line itself announces
it, as the fixture's first line does:

```logql
{service_name="api"} |= "server started"
```

Find the start line, note its timestamp,
then read forward from it with the errors
filter of chapter 6 and the status filter
of chapter 7 in the hour that follows.
The pairing — *a beginning, then its
consequences* — is most of incident
reading, and it needs nothing this guide
hasn't already run. Check: the "started"
line for the current version is present
exactly once per restart; more copies
mean restarts you hadn't heard about,
which is itself the news.

## 4. Turn a pattern into an alert

Counting errors (recipe 1) becomes an
alert when something evaluates the count
on a schedule and complains. Two homes
for that evaluation, both documented
rather than run by the lab: **Grafana
alerting**, evaluating the metric query
from inside the dashboards you already
have, and **Loki's ruler**, a component
that evaluates LogQL metric queries and
Prometheus-style rules against the store
itself and sends firing alerts to an
Alertmanager. Either way the query you
alert on is the one from recipe 1 with a
threshold the team chose on purpose —
*more than five errors in five minutes,
sustained* — and the craft is in the
threshold and the wording of the message,
not in the plumbing. This guide's
neighbour, *Prometheus and Grafana for
Mere Mortals*, teaches alert design —
firing only when it should — in the depth
it deserves; a log alert obeys the same
discipline, with one extra warning from
chapter 13: alert on patterns in *your*
systems' behaviour, and never let an
alert message quote log lines into a
channel where the lines themselves
shouldn't travel.
