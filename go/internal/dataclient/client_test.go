package dataclient

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestGetDataJSON(t *testing.T) {
	envelope := []jsonEnvelope{{
		Meta: map[string]interface{}{"name": "TEST:pv"},
		Data: []jsonSample{
			{Secs: 1000, Nanos: 0, Val: 1.23, Severity: 0, Status: 0},
			{Secs: 1001, Nanos: 0, Val: 4.56, Severity: 0, Status: 0},
		},
	}}
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if got := r.URL.Query().Get("pv"); got != "TEST:pv" {
			t.Errorf("pv query param = %q", got)
		}
		json.NewEncoder(w).Encode(envelope)
	}))
	defer srv.Close()

	c := New(srv.URL, "json")
	points, err := c.GetData("TEST:pv", "", "")
	if err != nil {
		t.Fatalf("GetData: %v", err)
	}
	if len(points) != 2 {
		t.Fatalf("len(points) = %d, want 2", len(points))
	}
	if points[0].Val.(float64) != 1.23 {
		t.Errorf("points[0].Val = %v", points[0].Val)
	}
}

func TestGetDataHTTPError(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer srv.Close()

	c := New(srv.URL, "json")
	if _, err := c.GetData("TEST:pv", "", ""); err == nil {
		t.Fatalf("expected error")
	}
}
