# Writing criteria for this guide

Every "for Mere Mortals" guide is written to the same nine-point
standard, so a reader who trusts one can trust the rest. Here it
is, with the verification notes for this particular guide below.

1. **Fix it first.** Reader outcomes lead, not action items: each
   chapter opens by naming the outcome it delivers, shows a check
   the reader can run to confirm they got it, and a reasonable
   reader finishes able to state what was done, what it means,
   and what to try next.
2. **Plain language.** Short sentences, everyday vocabulary,
   technical terms defined on first use. No slang, and no
   idioms that only make sense in one country — the reader may
   be translating as they go.
3. **No dead ends.** A guide never tells the reader to do
   something it cannot show them how to verify. Every claim a
   reader relies on — an install, a command, an output — is
   something this guide demonstrates or clearly labels
   documented-only below.
4. **Live-verified where it matters.** Procedures are run for
   real in the guide's lab wherever the build machine allows it,
   and the transcripts kept in the repository are the evidence.
   What could not be run is listed honestly below, never
   presented as if it had been.
5. **General audiences.** Nothing in this guide — examples,
   fixtures, names, addresses — is modelled on any particular
   reader or author's real life, network, or organisations.
   The lab's traffic is the lab talking to itself.
6. **Standalone.** A reader needs this guide, its lab, and
   nothing else. Where another guide would genuinely help, it
   is pointed to once, by name, and the chapter still completes
   without it.
7. **Honest about limits.** Chapter 13 names what the tool
   cannot do: labels that explode into millions of streams,
   log text that is stored but never indexed, lines that arrive
   too old to accept, logs that are other people's words, and
   the gap between one honest server and a promised cluster.
8. **The ethics rule is in the text, early.** Chapter 1 and the
   README state the rule plainly — *your logs, your machines,
   or explicit permission* — before any procedure depends on
   it, and later chapters point back to it where the tooling
   would make crossing the line easy.
9. **Builds clean.** The site builds with MkDocs in strict mode
   with no warnings, and a fresh reader following the chapters
   in order reaches the stated outcome of each.

## Verification notes for this guide

The build machine is a 2-CPU, 7.7 GB Ubuntu 24.04 sandbox.
Loki **3.7.9** and logcli **3.7.9** were downloaded as the
official release binaries from the grafana/loki GitHub
releases page and run in single-binary mode with the local
configuration kept in this repository (`loki-lab/loki-local.yaml`),
storing chunks and index on the local filesystem in scratch
space. All transcripts live in `loki-lab/transcripts/`; the
push payload was built by `loki-lab/make_push.py`.

Run for real, with transcripts as evidence:

- Both binaries reporting their version (t00).
- First start under the local config, the `/ready` endpoint
  turning from 503 to `ready`, `/metrics` answering 200, and
  the labels endpoint listing exactly the labels in use after
  the push (t01).
- A push of ten logfmt lines in two labelled streams through
  the HTTP push API, answered with HTTP 204 and an empty body
  (t02).
- A stream-selector query returning the pushed lines,
  including Loki 3.x's automatic `detected_level` grouping
  (t03).
- Line filters both ways: a plain substring filter (`|=`)
  and a regular-expression filter (`|~`), each returning the
  two error lines (t04).
- A `logfmt` parser stage with a numeric label filter on the
  parsed `status` field, and a `count_over_time` metric query
  returning counts per stream (t05).
- logcli against the same server: `labels`, a filtered range
  query, and an instant metric query (t06).
- A forced flush (`/flush`) and the storage it produced on
  disk: one chunk file per stream under the tenant folder,
  the TSDB index shipper folders, and the write-ahead logs
  (t07).
- Three edge behaviours in one sitting: `detected_level`
  used as a query filter, a duplicate push deduplicated
  (the line count stays at ten), and a ten-day-old line
  rejected with HTTP 400 naming the oldest timestamp the
  config accepts (t08).

Documented only — described from the project's documentation,
not run, and the text does not claim otherwise:

- The microservices deployment mode, multi-node clusters,
  and multi-tenancy beyond the single `fake` tenant the lab
  ran with `auth_enabled: false`.
- S3, GCS and Azure object storage backends; the lab used
  the filesystem store throughout.
- Grafana's Explore view, dashboards and log-based alerting
  (chapter 9 describes the setup; the verified query face in
  this guide is the HTTP API and logcli).
- Log shippers end to end. Chapter 8 states Promtail's
  status from Grafana's own documentation (end of life
  2 March 2026) and describes the current recommended agent,
  Grafana Alloy, and the other push-API clients at the level
  the docs support; no shipper was run in the lab.
- Retention actually deleting aged data: the settings are
  shown and explained, the waiting is not run.
- The ruler component and alerting rules over log queries.

Fixtures are this guide's own and deliberately generic: ten
logfmt lines from two invented services of a small fictional
web shop — an API and a batch worker — generated by a script
in this repository. No example is modelled on any real
person, service, network or organisation, and every line the
lab stored was a line the lab itself invented.
