// Package mgmtclient implements a Go client for the Archiver Appliance
// management (mgmt/bpl) API, mirroring archappl.admin.client.ArchiverMgmtClient.
package mgmtclient

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
)

// Client talks to the Archiver Appliance mgmt/bpl API.
type Client struct {
	// BaseURL is the server URL (scheme://host[:port]), without the
	// "/mgmt/bpl" suffix.
	BaseURL string
	HTTP    *http.Client
}

// New creates a management Client for the given base URL.
func New(baseURL string) *Client {
	return &Client{BaseURL: baseURL, HTTP: &http.Client{}}
}

func (c *Client) endpoint(path string) string {
	return strings.TrimRight(c.BaseURL, "/") + "/mgmt/bpl/" + path
}

func (c *Client) getJSON(path string, params url.Values, out interface{}) error {
	u := c.endpoint(path)
	if len(params) > 0 {
		u += "?" + params.Encode()
	}
	resp, err := c.HTTP.Get(u)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("HTTP %d requesting %s", resp.StatusCode, u)
	}
	if out == nil {
		return nil
	}
	return json.Unmarshal(body, out)
}

// GetApplianceInfo returns the appliance info as a raw JSON-decoded map.
func (c *Client) GetApplianceInfo() (map[string]interface{}, error) {
	var out map[string]interface{}
	if err := c.getJSON("getApplianceInfo", nil, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// GetAllPVs returns PV names matching the given pattern (unix wildcard).
func (c *Client) GetAllPVs(pv string, limit int, expanded bool) ([]string, error) {
	path := "getAllPVs"
	if expanded {
		path = "getAllExpandedPVNames"
	}
	params := url.Values{}
	if pv != "" {
		params.Set("pv", pv)
	}
	if limit > 0 {
		params.Set("limit", fmt.Sprintf("%d", limit))
	}
	var out []string
	if err := c.getJSON(path, params, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// GetPVStatus returns the status info for the given PV names/patterns,
// keyed by PV name.
func (c *Client) GetPVStatus(pvs []string) (map[string]map[string]interface{}, error) {
	result := map[string]map[string]interface{}{}
	for _, pv := range pvs {
		var entries []map[string]interface{}
		params := url.Values{"pv": []string{pv}}
		if err := c.getJSON("getPVStatus", params, &entries); err != nil {
			return nil, err
		}
		for _, e := range entries {
			if name, ok := e["pvName"].(string); ok {
				result[name] = e
			}
		}
	}
	return result, nil
}

// GetPVTypeInfo returns the PVTypeInfo for a single PV, or nil if not found.
func (c *Client) GetPVTypeInfo(pv string) (map[string]interface{}, error) {
	var out map[string]interface{}
	params := url.Values{"pv": []string{pv}}
	if err := c.getJSON("getPVTypeInfo", params, &out); err != nil {
		if strings.Contains(err.Error(), "HTTP 4") || strings.Contains(err.Error(), "HTTP 5") {
			return nil, nil
		}
		return nil, err
	}
	return out, nil
}

// GetPVDetails returns the details records for a single PV.
func (c *Client) GetPVDetails(pv string) ([]map[string]interface{}, error) {
	var out []map[string]interface{}
	params := url.Values{"pv": []string{pv}}
	if err := c.getJSON("getPVDetails", params, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// GetStoresForPV returns the names of the data stores for a PV.
func (c *Client) GetStoresForPV(pv string) ([]string, error) {
	var out []string
	params := url.Values{"pv": []string{pv}}
	if err := c.getJSON("getStoresForPV", params, &out); err != nil {
		return nil, err
	}
	return out, nil
}

func (c *Client) String() string {
	return fmt.Sprintf("[Admin Client] Archiver Appliance on: %s/mgmt/bpl", strings.TrimRight(c.BaseURL, "/"))
}
