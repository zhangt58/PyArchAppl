// Package dataclient implements a Go client for the Archiver Appliance data
// retrieval API, mirroring archappl.data.client.ArchiverDataClient.
package dataclient

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/zhangt58/PyArchAppl/go/internal/pb"
)

// Point is a single decoded sample for a PV, aligned with the columns
// produced by the Python client's DataFrame ('val', 'status', 'severity'
// indexed by 'time').
type Point struct {
	Time     time.Time
	Val      interface{}
	Status   int32
	Severity int32
}

// Client retrieves PV data from the Archiver Appliance data retrieval API.
type Client struct {
	// BaseURL is the server URL (scheme://host[:port]), without the
	// "/retrieval/data/getData.<format>" suffix.
	BaseURL string
	// Format is either "raw" or "json".
	Format string
	HTTP   *http.Client
}

// New creates a Client for the given base URL and format ("raw" or "json").
func New(baseURL, format string) *Client {
	if format == "" {
		format = "raw"
	}
	return &Client{BaseURL: baseURL, Format: strings.ToLower(format), HTTP: &http.Client{}}
}

func (c *Client) endpoint() string {
	return strings.TrimRight(c.BaseURL, "/") + "/retrieval/data/getData." + c.Format
}

// GetData retrieves the samples for a single PV within the optional time
// window [fromTime, toTime), both in ISO8601 format. An empty string omits
// the corresponding query parameter, matching the Python client behavior.
func (c *Client) GetData(pv, fromTime, toTime string) ([]Point, error) {
	params := url.Values{"pv": []string{pv}}
	if fromTime != "" {
		params.Set("from", fromTime)
	}
	if toTime != "" {
		params.Set("to", toTime)
	}
	u := c.endpoint() + "?" + params.Encode()

	resp, err := c.HTTP.Get(u)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("error fetching data for %q: HTTP %d", pv, resp.StatusCode)
	}

	if c.Format == "json" {
		return parseJSONData(body)
	}
	return parseRawData(body)
}

func parseRawData(body []byte) ([]Point, error) {
	pvData, err := pb.UnpackRawData(body)
	if err != nil {
		return nil, err
	}
	if pvData.Info == nil {
		return nil, nil
	}
	yearStart := time.Date(int(pvData.Info.Year), 1, 1, 0, 0, 0, 0, time.UTC)
	points := make([]Point, 0, len(pvData.Samples))
	for _, s := range pvData.Samples {
		ts := yearStart.Add(time.Duration(s.SecondsIntoYear)*time.Second + time.Duration(s.Nano)*time.Nanosecond)
		points = append(points, Point{
			Time:     ts,
			Val:      s.Val,
			Status:   s.Status,
			Severity: s.Severity,
		})
	}
	return points, nil
}

// jsonEnvelope mirrors the JSON shape returned by the getData.json
// endpoint: a single-element array with 'meta' and 'data' keys.
type jsonEnvelope struct {
	Meta map[string]interface{} `json:"meta"`
	Data []jsonSample           `json:"data"`
}

type jsonSample struct {
	Secs     int64       `json:"secs"`
	Nanos    int64       `json:"nanos"`
	Val      interface{} `json:"val"`
	Severity int32       `json:"severity"`
	Status   int32       `json:"status"`
}

func parseJSONData(body []byte) ([]Point, error) {
	var envelopes []jsonEnvelope
	if err := json.Unmarshal(body, &envelopes); err != nil {
		return nil, err
	}
	if len(envelopes) == 0 {
		return nil, nil
	}
	points := make([]Point, 0, len(envelopes[0].Data))
	for _, s := range envelopes[0].Data {
		points = append(points, Point{
			Time:     time.Unix(s.Secs, s.Nanos).UTC(),
			Val:      s.Val,
			Status:   s.Status,
			Severity: s.Severity,
		})
	}
	return points, nil
}
