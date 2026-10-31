package crm

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strconv"
	"time"
)

const (
	// ProductionURL is the default CRM API host.
	ProductionURL = "https://crm-gateways.hitechcloud.vn"
	// SandboxURL is the sandbox CRM API host.
	SandboxURL = "https://crm-gateways-sandbox.hitechcloud.vn"
	// Version of the SDK.
	Version = "1.0.0"

	tokenPath = "/v1/oauth/token"
)

// httpClient is the low-level transport with OAuth2 token management.
type httpClient struct {
	baseURL      string
	client       *http.Client
	clientID     string
	clientSecret string
	scope        string
	token        string
	tokenExpiry  time.Time
	maxRetries   int
}

func newHTTPClient(baseURL, clientID, clientSecret, scope, token string, timeout time.Duration, maxRetries int) *httpClient {
	h := &httpClient{
		baseURL:      baseURL,
		client:       &http.Client{Timeout: timeout},
		clientID:     clientID,
		clientSecret: clientSecret,
		scope:        scope,
		token:        token,
		maxRetries:   maxRetries,
	}
	if token != "" {
		h.tokenExpiry = time.Now().Add(100 * 365 * 24 * time.Hour)
	}
	return h
}

// SetToken installs a pre-issued access token.
func (c *httpClient) SetToken(token string) {
	c.token = token
	c.tokenExpiry = time.Now().Add(100 * 365 * 24 * time.Hour)
}

// FetchToken performs the client_credentials exchange.
func (c *httpClient) FetchToken() (map[string]interface{}, error) {
	if c.clientID == "" || c.clientSecret == "" {
		return nil, &Error{Message: "no client credentials configured"}
	}
	payload := map[string]string{
		"grant_type":    "client_credentials",
		"client_id":     c.clientID,
		"client_secret": c.clientSecret,
	}
	if c.scope != "" {
		payload["scope"] = c.scope
	}
	body, _ := json.Marshal(payload)
	req, err := http.NewRequest("POST", c.baseURL+tokenPath, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	req.Header.Set("User-Agent", "hitechcloud-crm-go/"+Version)

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	parsed := decode(raw)
	if resp.StatusCode >= 400 {
		return nil, errorFromResponse(resp, parsed)
	}
	data, _ := parsed["data"].(map[string]interface{})
	if tok, ok := data["access_token"].(string); ok {
		c.token = tok
	}
	expiresIn := 3600
	if v, ok := data["expires_in"].(float64); ok {
		expiresIn = int(v)
	}
	lead := expiresIn - 60
	if lead < 30 {
		lead = 30
	}
	c.tokenExpiry = time.Now().Add(time.Duration(lead) * time.Second)
	return data, nil
}

func (c *httpClient) ensureToken() error {
	if c.token != "" && time.Now().Before(c.tokenExpiry) {
		return nil
	}
	if c.clientID == "" || c.clientSecret == "" {
		if c.token != "" {
			return nil
		}
		return &Error{Message: "no access token and no client credentials configured"}
	}
	_, err := c.FetchToken()
	return err
}

type requestOptions struct {
	params      map[string]string
	body        interface{}
	multipart   *multipartBody
	contentType string
	retryAuth   bool
}

type multipartBody struct {
	data        []byte
	contentType string
}

// Request performs an authenticated request with retries.
func (c *httpClient) Request(method, path string, opts requestOptions) (map[string]interface{}, error) {
	if err := c.ensureToken(); err != nil {
		return nil, err
	}
	fullURL := c.baseURL + path
	if len(opts.params) > 0 {
		q := url.Values{}
		for k, v := range opts.params {
			q.Set(k, v)
		}
		fullURL += "?" + q.Encode()
	}

	retryAuth := opts.retryAuth
	var lastErr error
	for attempt := 0; attempt <= c.maxRetries; attempt++ {
		var reader io.Reader
		contentType := ""
		if opts.multipart != nil {
			reader = bytes.NewReader(opts.multipart.data)
			contentType = opts.multipart.contentType
		} else if opts.body != nil {
			b, err := json.Marshal(opts.body)
			if err != nil {
				return nil, fmt.Errorf("marshal body: %w", err)
			}
			reader = bytes.NewReader(b)
			contentType = "application/json"
		}

		req, err := http.NewRequest(method, fullURL, reader)
		if err != nil {
			return nil, err
		}
		req.Header.Set("Accept", "application/json")
		req.Header.Set("User-Agent", "hitechcloud-crm-go/"+Version)
		req.Header.Set("Authorization", "Bearer "+c.token)
		if contentType != "" {
			req.Header.Set("Content-Type", contentType)
		}

		resp, err := c.client.Do(req)
		if err != nil {
			lastErr = err
			if attempt < c.maxRetries {
				time.Sleep(time.Duration(1<<uint(attempt)) * time.Second)
				continue
			}
			return nil, fmt.Errorf("request failed: %w", err)
		}
		raw, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		if resp.StatusCode == 401 && retryAuth && c.clientID != "" {
			if _, ferr := c.FetchToken(); ferr != nil {
				return nil, ferr
			}
			retryAuth = false
			attempt--
			continue
		}

		if resp.StatusCode == 429 {
			retryAfter := parseRetryAfter(resp)
			if attempt < c.maxRetries {
				time.Sleep(time.Duration(retryAfter) * time.Second)
				continue
			}
			return nil, errorFromResponse(resp, decode(raw))
		}

		if resp.StatusCode >= 500 && attempt < c.maxRetries {
			time.Sleep(time.Duration(1<<uint(attempt)) * time.Second)
			continue
		}

		parsed := decode(raw)
		if resp.StatusCode >= 400 {
			return nil, errorFromResponse(resp, parsed)
		}
		return parsed, nil
	}
	if lastErr != nil {
		return nil, lastErr
	}
	return nil, &Error{Message: "request failed after retries"}
}

func (c *httpClient) Get(path string, params map[string]string) (map[string]interface{}, error) {
	return c.Request("GET", path, requestOptions{params: params, retryAuth: true})
}

func (c *httpClient) Post(path string, body interface{}) (map[string]interface{}, error) {
	return c.Request("POST", path, requestOptions{body: body, retryAuth: true})
}

func (c *httpClient) Patch(path string, body interface{}) (map[string]interface{}, error) {
	return c.Request("PATCH", path, requestOptions{body: body, retryAuth: true})
}

func (c *httpClient) Delete(path string) (map[string]interface{}, error) {
	return c.Request("DELETE", path, requestOptions{retryAuth: true})
}

// PostFile uploads a file via multipart/form-data with extra form fields.
func (c *httpClient) PostFile(path, fileField, filePath string, fields map[string]string) (map[string]interface{}, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)
	part, err := writer.CreateFormFile(fileField, filepath.Base(filePath))
	if err != nil {
		return nil, err
	}
	if _, err := io.Copy(part, f); err != nil {
		return nil, err
	}
	for k, v := range fields {
		if err := writer.WriteField(k, v); err != nil {
			return nil, err
		}
	}
	if err := writer.Close(); err != nil {
		return nil, err
	}
	return c.Request("POST", path, requestOptions{
		multipart: &multipartBody{data: buf.Bytes(), contentType: writer.FormDataContentType()},
		retryAuth: true,
	})
}

func decode(raw []byte) map[string]interface{} {
	if len(raw) == 0 {
		return map[string]interface{}{}
	}
	var out map[string]interface{}
	if err := json.Unmarshal(raw, &out); err != nil {
		return map[string]interface{}{"message": string(raw)}
	}
	return out
}

func parseRetryAfter(resp *http.Response) int {
	if v := resp.Header.Get("Retry-After"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return 60
}

func errorFromResponse(resp *http.Response, parsed map[string]interface{}) error {
	message, _ := parsed["message"].(string)
	if message == "" {
		message = fmt.Sprintf("HTTP %d", resp.StatusCode)
	}
	code, _ := parsed["code"].(string)
	errs, _ := parsed["errors"].(map[string]interface{})
	return mapError(resp.StatusCode, code, message, errs, parseRetryAfter(resp))
}
