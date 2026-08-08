package cliutil

import (
	"testing"
	"time"
)

func TestParseISOTime(t *testing.T) {
	got, err := ParseISOTime("2021-04-15T20:10:00.000Z")
	if err != nil {
		t.Fatalf("ParseISOTime: %v", err)
	}
	want := time.Date(2021, 4, 15, 20, 10, 0, 0, time.UTC)
	if !got.Equal(want) {
		t.Errorf("got %v, want %v", got, want)
	}
}

func TestParseISOTimeInvalid(t *testing.T) {
	if _, err := ParseISOTime("not-a-time"); err == nil {
		t.Fatalf("expected error")
	}
}

func TestParseTimeSpan(t *testing.T) {
	cases := []struct {
		in   string
		want time.Duration
	}{
		{"6 hours", 6 * time.Hour},
		{"5 mins before", 5 * time.Minute},
		{"1 hour and 30 mins", 90 * time.Minute},
		{"15 seconds ago", 15 * time.Second},
	}
	for _, c := range cases {
		got, err := ParseTimeSpan(c.in)
		if err != nil {
			t.Fatalf("ParseTimeSpan(%q): %v", c.in, err)
		}
		if got != c.want {
			t.Errorf("ParseTimeSpan(%q) = %v, want %v", c.in, got, c.want)
		}
	}
}

func TestParseTimeSpanInvalid(t *testing.T) {
	if _, err := ParseTimeSpan("bogus"); err == nil {
		t.Fatalf("expected error")
	}
}

func TestLoadPVList(t *testing.T) {
	pvs, err := LoadPVList([]string{"A", "B"}, "")
	if err != nil {
		t.Fatalf("LoadPVList: %v", err)
	}
	if len(pvs) != 2 || pvs[0] != "A" || pvs[1] != "B" {
		t.Errorf("pvs = %v", pvs)
	}
}

func TestLoadPVListMissingFile(t *testing.T) {
	pvs, err := LoadPVList([]string{"A"}, "/nonexistent/path.txt")
	if err != nil {
		t.Fatalf("LoadPVList: %v", err)
	}
	if len(pvs) != 1 || pvs[0] != "A" {
		t.Errorf("pvs = %v", pvs)
	}
}
