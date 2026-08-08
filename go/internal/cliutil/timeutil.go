package cliutil

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// ParseISOTime parses an ISO8601 timestamp, accepting a trailing 'Z' or an
// explicit UTC offset, e.g. "2021-04-15T20:10:00.000Z".
func ParseISOTime(s string) (time.Time, error) {
	layouts := []string{
		time.RFC3339Nano,
		time.RFC3339,
		"2006-01-02T15:04:05.000Z",
		"2006-01-02T15:04:05Z",
		"2006-01-02T15:04:05",
	}
	var lastErr error
	for _, layout := range layouts {
		if t, err := time.Parse(layout, s); err == nil {
			return t.UTC(), nil
		} else {
			lastErr = err
		}
	}
	return time.Time{}, fmt.Errorf("invalid ISO8601 time %q: %w", s, lastErr)
}

var unitAliases = map[string]time.Duration{
	"year": 365 * 24 * time.Hour, "years": 365 * 24 * time.Hour,
	"month": 30 * 24 * time.Hour, "months": 30 * 24 * time.Hour,
	"week": 7 * 24 * time.Hour, "weeks": 7 * 24 * time.Hour,
	"day": 24 * time.Hour, "days": 24 * time.Hour,
	"hour": time.Hour, "hours": time.Hour,
	"minute": time.Minute, "minutes": time.Minute, "min": time.Minute, "mins": time.Minute,
	"second": time.Second, "seconds": time.Second, "sec": time.Second, "secs": time.Second,
	"microsecond": time.Microsecond, "microseconds": time.Microsecond,
	"msec": time.Millisecond, "msecs": time.Millisecond,
}

var timeSpanTokenRE = regexp.MustCompile(`(?i)(\d+)\s*([a-z]+)`)

// ParseTimeSpan parses a small subset of natural-language relative time
// spans, e.g. "6 hours", "1 hour and 30 mins", "5 mins before", "15 seconds
// ago". It supports the units accepted by the Python CLI's --time-span
// option, joined with "and"/",", with an optional trailing "before"/"ago".
func ParseTimeSpan(s string) (time.Duration, error) {
	s = strings.TrimSpace(s)
	s = strings.TrimSuffix(strings.TrimSpace(s), "ago")
	s = strings.TrimSuffix(strings.TrimSpace(s), "before")
	s = strings.NewReplacer(" and ", ",", " and,", ",").Replace(s)

	matches := timeSpanTokenRE.FindAllStringSubmatch(s, -1)
	if len(matches) == 0 {
		return 0, fmt.Errorf("invalid time span %q", s)
	}
	var total time.Duration
	for _, m := range matches {
		n, err := strconv.Atoi(m[1])
		if err != nil {
			return 0, fmt.Errorf("invalid time span %q: %w", s, err)
		}
		unit := strings.ToLower(m[2])
		d, ok := unitAliases[unit]
		if !ok {
			return 0, fmt.Errorf("invalid time span unit %q in %q", unit, s)
		}
		total += time.Duration(n) * d
	}
	return total, nil
}
