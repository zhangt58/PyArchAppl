// Package config reads the same site configuration file format used by the
// Python implementation (PyArchAppl), so both CLIs share one configuration.
package config

import (
	"bufio"
	"embed"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

//go:embed default.ini
var embedded embed.FS

// EnvConfigPathName is the environment variable that, when set, overrides
// the configuration file search path (highest priority), matching the
// Python client's PYARCHAPPL_CONFIG_FILE.
const EnvConfigPathName = "PYARCHAPPL_CONFIG_FILE"

// ServerConfig holds the resolved values of the active "server" section.
type ServerConfig struct {
	URL           string
	AdminPort     string
	DataPort      string
	DataFormat    string
	AdminDisabled bool
	Extra         map[string]string
}

// SiteConfig is the fully parsed configuration file, mirroring the
// dictionary produced by archappl.config.read_config in Python.
type SiteConfig struct {
	Path   string
	Server ServerConfig
	// Raw holds every section as parsed, keyed by section name.
	Raw map[string]map[string]string
}

// iniData is a minimal ordered representation of an INI file: section name
// to key/value pairs. It supports the small subset of configparser syntax
// used by the site configuration file: "[section]" headers, "key = value"
// pairs and "#"/";" full line comments.
type iniData map[string]map[string]string

func parseINI(r *bufio.Scanner) (iniData, error) {
	data := iniData{}
	section := ""
	for r.Scan() {
		line := strings.TrimSpace(r.Text())
		if line == "" || strings.HasPrefix(line, "#") || strings.HasPrefix(line, ";") {
			continue
		}
		if strings.HasPrefix(line, "[") && strings.HasSuffix(line, "]") {
			section = strings.TrimSpace(line[1 : len(line)-1])
			if _, ok := data[section]; !ok {
				data[section] = map[string]string{}
			}
			continue
		}
		idx := strings.IndexAny(line, "=:")
		if idx < 0 {
			continue
		}
		key := strings.ToLower(strings.TrimSpace(line[:idx]))
		val := strings.TrimSpace(line[idx+1:])
		if section == "" {
			continue
		}
		data[section][key] = val
	}
	if err := r.Err(); err != nil {
		return nil, err
	}
	return data, nil
}

func parseINIFile(path string) (iniData, error) {
	f, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return parseINI(bufio.NewScanner(f))
}

// GetConfigPath returns the configuration file path following the same
// search order as the Python implementation:
//  0. env PYARCHAPPL_CONFIG_FILE
//  1. ~/.pyarchappl/config.ini
//  2. /etc/pyarchappl/config.ini
//  3. the default configuration bundled with this tool
func GetConfigPath() string {
	if p := os.Getenv(EnvConfigPathName); p != "" {
		return expandUser(p)
	}
	if home, err := os.UserHomeDir(); err == nil {
		p := filepath.Join(home, ".pyarchappl", "config.ini")
		if fileExists(p) {
			return p
		}
	}
	if fileExists("/etc/pyarchappl/config.ini") {
		return "/etc/pyarchappl/config.ini"
	}
	return ""
}

func fileExists(p string) bool {
	info, err := os.Stat(p)
	return err == nil && !info.IsDir()
}

func expandUser(p string) string {
	if strings.HasPrefix(p, "~") {
		if home, err := os.UserHomeDir(); err == nil {
			return filepath.Join(home, strings.TrimPrefix(p, "~"))
		}
	}
	return p
}

// Load reads and parses the site configuration file. If path is empty,
// GetConfigPath is used to locate one, falling back to the built-in
// default.ini bundled with this module.
func Load(path string) (*SiteConfig, error) {
	if path == "" {
		path = GetConfigPath()
	}

	var data iniData
	var err error
	usedPath := path
	if path == "" {
		b, rerr := embedded.ReadFile("default.ini")
		if rerr != nil {
			return nil, rerr
		}
		data, err = parseINI(bufio.NewScanner(strings.NewReader(string(b))))
		usedPath = "(built-in default.ini)"
	} else {
		data, err = parseINIFile(path)
	}
	if err != nil {
		return nil, fmt.Errorf("reading config file %q: %w", path, err)
	}

	mainSection, ok := data["main"]
	if !ok {
		return nil, fmt.Errorf("'main' section not found in %s", usedPath)
	}
	serverKey := mainSection["use"]
	serverSection, ok := data[serverKey]
	if !ok {
		return nil, fmt.Errorf("'%s' section not found in %s", serverKey, usedPath)
	}
	url, ok := serverSection["url"]
	if !ok {
		return nil, fmt.Errorf("'url' not found in '%s' section", serverKey)
	}

	adminDisabled := false
	if v, ok := serverSection["admin_disabled"]; ok {
		adminDisabled, _ = strconv.ParseBool(v)
	}

	extra := map[string]string{}
	for k, v := range serverSection {
		switch k {
		case "url", "admin_port", "data_port", "data_format", "admin_disabled":
			continue
		default:
			extra[k] = v
		}
	}

	sc := &SiteConfig{
		Path: usedPath,
		Server: ServerConfig{
			URL:           url,
			AdminPort:     serverSection["admin_port"],
			DataPort:      serverSection["data_port"],
			DataFormat:    defaultString(serverSection["data_format"], "raw"),
			AdminDisabled: adminDisabled,
			Extra:         extra,
		},
		Raw: data,
	}
	return sc, nil
}

func defaultString(v, d string) string {
	if v == "" {
		return d
	}
	return v
}

// AdminURL returns the base URL for the management (mgmt/bpl) API.
func (c *SiteConfig) AdminURL() string {
	if c.Server.AdminPort == "" {
		return c.Server.URL
	}
	return c.Server.URL + ":" + c.Server.AdminPort
}

// DataURL returns the base URL for the data retrieval API.
func (c *SiteConfig) DataURL() string {
	if c.Server.DataPort == "" {
		return c.Server.URL
	}
	return c.Server.URL + ":" + c.Server.DataPort
}

// LocalTimezone returns the "misc.local_timezone" value if defined.
func (c *SiteConfig) LocalTimezone() string {
	if misc, ok := c.Raw["misc"]; ok {
		return misc["local_timezone"]
	}
	return ""
}
