# LogQL — Selecting and Filtering

By the end of this chapter you can write
the two halves of every log query: the
**stream selector** that chooses which
streams to read, and the **line filters**
that choose which of their lines to keep.
This is the half of LogQL you will use
daily; chapter 7 adds parsers and
numbers.

A log query is a small pipeline, read
left to right:

```text
{ stream selector } | filter | filter | ...
```

The braces choose addresses (chapter 5);
everything after them reads lines. No
braces, no query — a filter alone cannot
run, because Loki insists on knowing
which streams to open before it scans a
single line. That insistence is chapter
1's bargain, enforced by grammar.

## Stream selectors

Inside the braces, label matchers:

```logql
{job="lab"}
{service_name="api"}
{job="lab", service_name="api"}
{service_name=~"api|worker"}
{service_name!="api"}
```

- `=` exact match, `!=` not equal,
  `=~` regular-expression match, `!~`
  regex that must not match.
- Several matchers in one selector are
  ANDed: every one must hold.
- At least one matcher must name a
  non-empty value — `{job=~".+"}` is the
  "all streams in this job" shape, and
  the width of that net is your
  responsibility (chapter 13).

The selector runs against the index, so
it costs almost nothing. Everything
after it costs reading.

## The four line filters

After the selector, a **pipeline** of
stages. The first kind of stage tests the
line's text:

| Filter | Keeps lines that… |
|---|---|
| `\|= "text"` | contain the text |
| `!= "text"` | do not contain the text |
| `\|~ "regex"` | match the regular expression |
| `!~ "regex"` | do not match the regex |

The lab ran two of them against the
fixture (full answers in
`loki-lab/transcripts/t04-query-line-filters.txt`).
The plain contains-filter found the
errors:

```logql
{service_name="api"} |= "level=error"
```

Two lines came back: the checkout's 500
and the items call's 503. The regex
filter reached the same two lines by a
different idea — *the status begins with
5*:

```logql
{service_name="api"} |~ "status=5.."
```

Same answer, different tool: `|=` is a
substring test anybody can read at a
glance; `|~` is for shapes — `status=5..`,
`duration_ms=[0-9]{3,}`, an address
pattern. Regexes are RE2 syntax (the Go
family: no lookahead, no backreferences),
and they cost more than substrings, so
the plain filter is the house style until
a shape is genuinely needed.

Filters chain, and each narrows the
survivors of the last:

```logql
{service_name="api"} |= "level=error" != "checkout"
```

— errors, but not the checkout one.
Order costs nothing in correctness and a
little in speed: put the filter that
kills the most lines first.

## Filtering on metadata: detected_level

One more stage shape, met in chapter 4:
a **label filter** on structured
metadata. The lab's third query in
transcript t08 asked both services at
once for lines Loki had detected as
errors:

```logql
{job="lab"} | detected_level="error"
```

Three lines returned — the api's two and
the worker's one — with no text test at
all. Filters like this, written
`| name="value"`, test attached metadata
or (chapter 7) fields a parser just
extracted. The selector grammar they are
not; they run after the streams are open,
which is why they live after the pipe.

## Reading the answer

A log query's answer (`resultType:
streams`) groups surviving lines by their
stream — plus the metadata split you saw
with `detected_level` — each line with
its nanosecond timestamp, newest or
oldest first according to `direction`.
Two habits save confusion:

- **Mind the range.** A query_range
  answer only ever covers the `start` to
  `end` you sent. "No results" more often
  means *wrong window* than *no lines* —
  chapter 14's first entry.
- **Mind the limit.** Answers are capped
  (the lab sent `limit=20`); a busy stream
  returns the newest slice, not a summary
  saying there was more.

Check: with the fixture in place, the
three queries above return 7, 2 and 3
lines respectively — the whole api
stream, its errors, and every error in
the lab. If your run of the lab matches
those counts, your selectors and filters
are doing what this chapter claims.
