# Storage and Retention

By the end of this chapter you have seen
Loki's storage the way the lab did — as
files, with names and sizes — and you can
set the two numbers that govern a store's
life: how long lines are kept, and how
old a line may be when it knocks.

## What the lab's ten lines occupied

After the pushes of chapter 4, the data
folder held only promise: a write-ahead
log and folders being prepared. The lab
then told the ingester to flush, the way
time or volume eventually would:

```bash
curl -X POST http://127.0.0.1:3100/flush
```

and photographed the result
(`loki-lab/transcripts/t07-storage-on-disk.txt`):

```text
data/chunks/fake/15555cd5be71d803/MWExODBiZDE5NjM6MWExODBjZjY4ZTQ6YmIwMTgxZTU=
data/chunks/fake/c608c70f6096f841/MWExODBjMWFkNDM6MWExODBjZDk0MjQ6NWU0OTI0N2U=
data/tsdb-shipper-active/uploader/name
data/tsdb-shipper-active/wal/filesystem_2020-10-24/1793162756/00000000
data/wal/00000000

20K  data   (in total)
```

Read it with chapter 2's model in hand:

- **`data/chunks/fake/…`** — the chunks
  themselves, one file per stream in this
  small lab, under a folder named for the
  tenant. With authentication off the
  tenant is `fake`, and it owns every
  folder you see. The long hashed names
  are chunk identifiers, not meant for
  human browsing; Loki finds them through
  the index, not the directory listing.
- **`data/tsdb-shipper-*`** — the TSDB
  index in its local working clothes: an
  active area and a write-ahead log,
  shipping finished index files to the
  same filesystem store the chunks use.
  In the lab's config the index's home
  and the chunks' home are one disk; the
  `object_store: filesystem` line in the
  schema is what says so.
- **`data/wal`** — the ingester's
  write-ahead log, the safety net for
  lines held in memory.

Twenty kilobytes for ten lines proves
little about volume — chunk files have
fixed overheads, and real compression
shows at real counts — but the *shape*
is the truth at any scale: many small
chunk files, a compact index, no database
server, nothing that needs a caretaker of
its own. On a real deployment the same
two kinds of object live in S3, GCS or
Azure storage instead of a folder
(documented, not run here), which is why
Loki's storage bill surprises people
pleasantly: object storage is cheap, and
the index — the part a full-text system
spends its life growing — stays small
because it only ever held labels.

## Retention: deciding how long

A log store that keeps everything forever
is a liability with a search box, so Loki
expects a decision. Two settings, often
confused, govern different doors:

- **`retention_period`** (under
  `limits_config`, applied by the
  compactor) — how long stored chunks
  live before deletion. Set
  `compactor:` with
  `retention_enabled: true` and a period
  such as `720h` (thirty days) and older
  data is deleted as the compactor makes
  its rounds. The lab did not run the
  waiting; the setting is documented
  here, and its effect is mechanical and
  exactly as described in the project's
  docs.
- **`reject_old_samples_max_age`** — the
  door the lab *did* test: how old an
  incoming line may be. The lab set
  `168h`, and its ten-day-old line was
  refused at push time with HTTP 400,
  naming the oldest acceptable timestamp
  (transcript t08). One guards the past
  you keep; the other guards the past you
  accept.

Choose the retention period as a policy,
not a default: long enough to cover the
questions you actually revisit (an
incident reviewed next week, a pattern
checked month over month), short enough
that the store does not become an
unexamined archive of everything every
program ever said — chapter 13 gives
that archive its proper, wary name.
Deletion is per tenant and, with the
TSDB schema, stream filters can retire
one noisy source's history earlier than
the rest: a valve worth knowing exists
before you need it.
