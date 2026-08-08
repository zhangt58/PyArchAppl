// Package cliutil holds small helpers shared by the pyarchappl-get and
// pyarchappl-inspect command-line tools.
package cliutil

import (
	"bufio"
	"os"
	"strings"
)

// LoadPVList merges PV names given directly via repeated flags with PV
// names read from a file (one per line, blank lines and lines starting
// with '#' are skipped), preserving order and de-duplicating, matching the
// behavior of the Python CLIs.
func LoadPVList(pvList []string, pvFile string) ([]string, error) {
	result := append([]string(nil), pvList...)
	if pvFile == "" {
		return result, nil
	}
	f, err := os.Open(pvFile)
	if err != nil {
		// Match Python scripts: a missing/unreadable PV file is silently
		// ignored, falling back to whatever was passed via --pv.
		return result, nil
	}
	defer f.Close()

	seen := map[string]bool{}
	for _, pv := range result {
		seen[pv] = true
	}
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		if !seen[line] {
			result = append(result, line)
			seen[line] = true
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return result, nil
}
