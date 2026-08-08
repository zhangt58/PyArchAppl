# PyArchAppl (Go CLI tools)

This directory hosts a standalone Go module providing command-line tools
that fulfill the same purpose as the Python console scripts
`pyarchappl-get` and `pyarchappl-inspect`, while reading the **same
site configuration file format and search path** as the Python
implementation (see `main/config/__init__.py`).

This is the initial scaffold kicking off the Go CLI tools development; it
is functional but does not yet have full feature parity with the Python
tools (e.g. `--resample`, `--fillna-method`, and non-CSV export formats are
not implemented yet).

## Layout

```
go/
  cmd/
    pyarchappl-get/      # CLI entry point mirroring main/scripts/get.py
    pyarchappl-inspect/  # CLI entry point mirroring main/scripts/inspect.py
  internal/
    cliutil/    # PV list loading, ISO8601/time-span parsing shared by both CLIs
    config/     # Site configuration file reader (same format/search path as Python)
    dataclient/ # Data retrieval API client (raw protobuf + JSON formats)
    mgmtclient/ # Management (mgmt/bpl) API client
    pb/         # Minimal decoder for the archiver appliance "pbraw" wire format
```

## Configuration

Configuration is resolved with the same precedence as the Python client:

1. `PYARCHAPPL_CONFIG_FILE` environment variable
2. `~/.pyarchappl/config.ini`
3. `/etc/pyarchappl/config.ini`
4. the built-in default configuration bundled with the Go module

Use `--config-file` to override this search explicitly.

## Building

```bash
cd go
go build ./...
```

This produces the `pyarchappl-get` and `pyarchappl-inspect` binaries under
`cmd/`. Install them onto `$GOBIN` with:

```bash
go install ./cmd/pyarchappl-get
go install ./cmd/pyarchappl-inspect
```

## Testing

```bash
cd go
go test ./...
```

## Usage examples

```bash
# Retrieve raw PV data in a time window and print as CSV
pyarchappl-get --pv TST:gaussianNoise \
  --from 2021-04-15T20:10:00.000Z --to 2021-04-15T21:25:00.000Z

# Inspect archiving status for one or more PVs
pyarchappl-inspect --pv TST:gaussianNoise --key status
```
