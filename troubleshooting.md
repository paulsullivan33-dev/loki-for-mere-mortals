# Troubleshooting

The failures a first Loki meets, in the
order a first Loki meets them. The ones
the lab provoked on purpose are marked
with their transcript; the rest are
labelled documented, from the project's
own materials and the behaviour of the
parts involved.

## "My query returns nothing"

Work the list in order; nearly every
empty answer is one of these:

1. **The window is wrong.** `query_range`
   only covers the `start`–`end` sent.
   The lines are at their *own*
   timestamps, which come from the
   sending machine's clock (chapter 13).
   Widen the window before doubting the
   store.
2. **The selector names no stream.**
   Labels must match exactly, spelling
   and case included. Ask the index what
   exists: `GET /loki/api/v1/labels`, then
   `GET /loki/api/v1/label/<name>/values`
   — or `logcli labels`. The lab's
   answers are in transcript t01.
3. **The push never landed.** A 204 is
   the only *yes* (chapter 4). Silence
   from a script usually means the push
   was never sent, or its error was never
   read. Which brings us to —
4. **The lines were refused.** Check the
   push response body, not just that a
   request happened. The next entry is
   the usual suspect.

## "My push was rejected" *(lab-verified)*

The refusal names its reason; read it.
The lab's specimen, from transcript t08:

```text
entry for stream '{job="lab", service_name="api"}' has timestamp too old: 2026-10-18T04:46:01Z, oldest acceptable timestamp is: 2026-10-21T04:46:01Z
```

HTTP 400, cause in plain words: the
line's timestamp is older than
`reject_old_samples_max_age` (168h in the
lab) permits. The fixes are at the
sender: a shipper that fell behind, a
clock that is wrong, or a door that
genuinely needs widening — a decision,
not a reflex (chapter 10). The same
family, documented: malformed JSON,
labels with illegal characters, and
lines over the size limit each return
their own named 400s. A 429 or a stream
limit message means a configured ceiling
(`max_streams_per_user` and friends) —
usually chapter 5's cardinality arriving
to collect its debt.

## "I pushed twice and the count didn't change" *(lab-verified)*

Not a fault. Identical timestamp plus
identical line in one stream is a
duplicate, and Loki keeps one copy —
transcript t08 re-pushed the lab's whole
payload and the total stayed at ten.
Deduplication is what makes shipper
retries safe. The corollary for testing:
to store "the same line again", it must
differ — in timestamp, as honest new
occurrences do.

## "The disk is empty but queries work"

Also not a fault. Fresh lines live in
ingester memory and the write-ahead log
until a chunk flushes by age, size, or
request (`/flush`, chapter 10). Queries
read memory and store together, so the
evidence of chapter 4's push was complete
long before transcript t07 had files to
photograph. If the disk stays empty for
*hours* of pushing, then suspect the
data path in the config — `path_prefix`
and the chunk directory under it — and
the server's own log, which reports
flush failures by name.

## "Queries are slow"

Ask which half of chapter 1's bargain is
paying. A wide selector (many streams,
long range) makes the read half scan;
check the selector first and narrow by
labels and time. A heavy regex or a
parser over millions of lines is the
same bill itemised differently. The
documented levers: split the question
(the frontend does this for you in
bigger deployments), cache results,
query less history at once, and — the
honest one — store less noise: a stream
that logs every heartbeat at debug level
is a tax on every future question asked
near it.

## "The levels look wrong"

`detected_level` is a heuristic: Loki
reads the line, spots a level word, and
attaches it (chapter 4). Lines whose
level is written unusually — a bare
number, a word it doesn't know — can be
grouped as unknown or missed entirely.
It is metadata, offered as a convenience;
a filter on it is a filter on a guess.
For levels you depend on, have the
shipper or the program state them
plainly, in a field a parser can take
(chapter 7), rather than asking the
store to infer them.

## "The server won't start"

The config is the first suspect: Loki
validates it and exits with the offending
line named — a YAML error, an unknown
key, a schema block half-copied from an
old guide (the `boltdb-shipper` vintage
of chapter 3 is the classic). Second
suspect: the port or the data folder —
3100 already in use, or a `path_prefix`
the process may not write. Both are
stated in the server's own first screen
of logging; read it before changing
anything, because with Loki the error
messages are unusually willing to name
the actual problem — as this chapter's
specimens show.
