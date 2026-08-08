package config

import (
	"os"
	"path/filepath"
	"testing"
)

func writeConfig(t *testing.T, dir, content string) string {
	t.Helper()
	p := filepath.Join(dir, "config.ini")
	if err := os.WriteFile(p, []byte(content), 0o644); err != nil {
		t.Fatalf("writing config: %v", err)
	}
	return p
}

func TestLoadExplicitPath(t *testing.T) {
	dir := t.TempDir()
	p := writeConfig(t, dir, `
[main]
use = default.server

[default.server]
url = http://127.0.0.1
admin_port = 17665
data_port = 17668
data_format = raw
admin_disabled = true

[misc]
local_timezone = America/Detroit
`)
	cfg, err := Load(p)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.Server.URL != "http://127.0.0.1" {
		t.Errorf("URL = %q", cfg.Server.URL)
	}
	if cfg.AdminURL() != "http://127.0.0.1:17665" {
		t.Errorf("AdminURL = %q", cfg.AdminURL())
	}
	if cfg.DataURL() != "http://127.0.0.1:17668" {
		t.Errorf("DataURL = %q", cfg.DataURL())
	}
	if !cfg.Server.AdminDisabled {
		t.Errorf("AdminDisabled = false, want true")
	}
	if cfg.LocalTimezone() != "America/Detroit" {
		t.Errorf("LocalTimezone = %q", cfg.LocalTimezone())
	}
}

func TestLoadMultiServerSelection(t *testing.T) {
	dir := t.TempDir()
	p := writeConfig(t, dir, `
[main]
use = local

[default.server]
url = http://127.0.0.1
admin_port = 17665
data_port = 17668

[local]
url = http://127.0.0.1
admin_port = 17666
data_port = 17666
admin_disabled = false
`)
	cfg, err := Load(p)
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.AdminURL() != "http://127.0.0.1:17666" {
		t.Errorf("AdminURL = %q", cfg.AdminURL())
	}
	if cfg.Server.AdminDisabled {
		t.Errorf("AdminDisabled = true, want false")
	}
}

func TestLoadDefaultsToEmbedded(t *testing.T) {
	t.Setenv(EnvConfigPathName, "")
	cfg, err := Load("")
	if err != nil {
		t.Fatalf("Load: %v", err)
	}
	if cfg.Server.URL == "" {
		t.Errorf("expected a non-empty default URL")
	}
}

func TestLoadMissingURL(t *testing.T) {
	dir := t.TempDir()
	p := writeConfig(t, dir, `
[main]
use = default.server

[default.server]
admin_port = 17665
`)
	if _, err := Load(p); err == nil {
		t.Fatalf("expected error for missing url")
	}
}

func TestLoadMissingServerSection(t *testing.T) {
	dir := t.TempDir()
	p := writeConfig(t, dir, `
[main]
use = nonexistent
`)
	if _, err := Load(p); err == nil {
		t.Fatalf("expected error for missing server section")
	}
}
