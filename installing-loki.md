# Installing Loki

By the end of this chapter Loki is
running on your machine in its simplest
honest shape — one binary, one short
configuration file, data on the local
disk — and you have proven it is ready
with its own health endpoint rather than
by hoping. Everything later in the guide
assumes exactly this install.

## Get the binary

Loki is one self-contained program. The
official releases live on the grafana/loki
GitHub releases page, as archives named
by system: `loki-linux-amd64.zip` for a
typical Linux PC or server,
`loki-linux-arm64.zip` for a Raspberry Pi
or other ARM board, with macOS and
Windows builds beside them. Its
command-line companion, **logcli**, ships
the same way (`logcli-linux-amd64.zip`
and friends), and chapter 9 uses it;
fetch both now.

```bash
curl -LO https://github.com/grafana/loki/releases/download/v3.7.9/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
./loki-linux-amd64 --version
```

Check: the version command answers with
the release and its build details. The
lab's answer is kept in
`loki-lab/transcripts/t00-version.txt`:

```text
loki, version 3.7.9 (branch: release-3.7.x, revision: d3b4a2f7)
```

A Docker image (`grafana/loki`) and
package installs exist too; they run the
same binary under the same config, and
nothing in this guide depends on the
difference. The binary alone keeps the
lab — and your first install — free of
moving parts that are not Loki.

## The configuration file

Loki takes hundreds of settings; a local
store needs a page of them. The lab's
file is kept verbatim in
`loki-lab/loki-local.yaml`; its working
parts are these:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /path/to/your/loki-data
  storage:
    filesystem:
      chunks_directory: /path/to/your/loki-data/chunks
      rules_directory: /path/to/your/loki-data/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
```

Read it as five decisions:

- `auth_enabled: false` — no tenants and
  no tenant header; the single built-in
  tenant named `fake` owns everything.
  Right for one person; chapter 13 says
  what it is *not* right for.
- `http_listen_port: 3100` — where the API
  lives. Everything in this guide talks
  to port 3100.
- `common` — one data folder
  (`path_prefix`, with the chunk and rules
  folders under it — substitute your own
  path), one copy of everything
  (`replication_factor: 1`, because there
  is one server), and an in-memory ring
  (the server's membership list contains
  only itself, in RAM).
- `schema_config` — how stored data is
  organised: the **TSDB** index, the
  **filesystem** object store, schema
  **v13**, one index period per day. This
  block is the current recommended shape;
  older guides showing `boltdb-shipper`
  are describing yesterday's index.
- A `limits_config` section in the lab's
  file sets `reject_old_samples_max_age`
  to `168h`: lines older than seven days
  are refused at the door. Chapter 4
  provokes that refusal on purpose, and
  chapter 10 explains the setting as part
  of retention.

Put the file where you will keep it —
`/etc/loki/loki-local.yaml` on a server,
beside the binary while you are learning —
and give Loki a data folder it owns.

## First start, and the readiness check

```bash
./loki-linux-amd64 -config.file=loki-local.yaml
```

The server logs its components starting,
then settles. Do not trust the quiet;
ask. Loki exposes a health endpoint that
answers **503** while it warms up and
**200** with the word `ready` when it
will take writes and queries:

```bash
curl -s http://127.0.0.1:3100/ready
```

Check: the answer is the single word
`ready`. The lab polled for about
eighteen seconds on its small machine
before the word arrived
(`loki-lab/transcripts/t01-ready-and-labels.txt`).
A second endpoint, `/metrics`, answering
200 with a page of Prometheus-format
numbers, confirms the server is fully up
and gives you a first sight of how Loki
reports on itself — the same numbers the
Prometheus and Grafana guide in this
series teaches you to chart.

To run Loki as a service under systemd,
the shape is the obvious one: a unit
whose `ExecStart` is the command above,
a dedicated user, and the data folder
owned by that user. The systemd guide in
this series covers unit files, restart
policies and hardening in the depth they
deserve; this guide's chapters work the
same whether the process was started by
your shell or by the supervisor.

One warning that belongs to the install,
not later: port 3100 has no login in this
configuration. On one machine, bound to
your own use, that is the lab's honest
simplicity. Do not expose this server to
a network you do not control — anyone who
can reach the port can read every log and
write new ones. Chapter 13 returns to
this; for now, a laptop or a private LAN
is the right neighbourhood for it.
