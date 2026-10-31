// Package crm is the official Go SDK for the HiTechCloud CRM API.
package crm

import "time"

// Client is the main HiTechCloud CRM client.
type Client struct {
	http *httpClient

	// Standard CRUD resources
	Contacts     *CrudResource
	Companies    *CrudResource
	Deals        *CrudResource
	Pipelines    *CrudResource
	Stages       *CrudResource
	Activities   *CrudResource
	Tasks        *CrudResource
	Calls        *CrudResource
	Emails       *CrudResource
	Meetings     *CrudResource
	Notes        *CrudResource
	Tags         *CrudResource
	Segments     *CrudResource
	CustomFields *CrudResource
	LeadSources  *CrudResource
	Products     *CrudResource
	Quotes       *CrudResource
	Users        *CrudResource
	Teams        *CrudResource

	// Special resources
	Files    *FilesResource
	Webhooks *WebhooksResource
	Imports  *ImportsResource
	Exports  *ExportsResource
}

type clientConfig struct {
	baseURL      string
	clientID     string
	clientSecret string
	scope        string
	token        string
	timeout      time.Duration
	maxRetries   int
}

// Option configures the client.
type Option func(*clientConfig)

// WithClientCredentials sets OAuth2 client_credentials for automatic tokens.
func WithClientCredentials(clientID, clientSecret, scope string) Option {
	return func(c *clientConfig) {
		c.clientID = clientID
		c.clientSecret = clientSecret
		c.scope = scope
	}
}

// WithToken sets a pre-issued access token.
func WithToken(token string) Option {
	return func(c *clientConfig) { c.token = token }
}

// WithBaseURL overrides the API host.
func WithBaseURL(u string) Option {
	return func(c *clientConfig) { c.baseURL = u }
}

// WithSandbox targets the sandbox environment.
func WithSandbox() Option {
	return func(c *clientConfig) { c.baseURL = SandboxURL }
}

// WithTimeout sets the per-request timeout.
func WithTimeout(d time.Duration) Option {
	return func(c *clientConfig) { c.timeout = d }
}

// WithMaxRetries sets the retry count for 429/5xx responses.
func WithMaxRetries(n int) Option {
	return func(c *clientConfig) { c.maxRetries = n }
}

// NewClient builds a new CRM client.
func NewClient(opts ...Option) (*Client, error) {
	cfg := &clientConfig{
		baseURL:    ProductionURL,
		timeout:    30 * time.Second,
		maxRetries: 3,
	}
	for _, opt := range opts {
		opt(cfg)
	}

	h := newHTTPClient(cfg.baseURL, cfg.clientID, cfg.clientSecret, cfg.scope, cfg.token, cfg.timeout, cfg.maxRetries)
	crud := func(path string) *CrudResource { return &CrudResource{client: h, path: path} }

	return &Client{
		http:         h,
		Contacts:     crud("contacts"),
		Companies:    crud("companies"),
		Deals:        crud("deals"),
		Pipelines:    crud("pipelines"),
		Stages:       crud("stages"),
		Activities:   crud("activities"),
		Tasks:        crud("tasks"),
		Calls:        crud("calls"),
		Emails:       crud("emails"),
		Meetings:     crud("meetings"),
		Notes:        crud("notes"),
		Tags:         crud("tags"),
		Segments:     crud("segments"),
		CustomFields: crud("custom-fields"),
		LeadSources:  crud("lead-sources"),
		Products:     crud("products"),
		Quotes:       crud("quotes"),
		Users:        crud("users"),
		Teams:        crud("teams"),
		Files:        &FilesResource{CrudResource: crud("files")},
		Webhooks:     &WebhooksResource{client: h},
		Imports:      &ImportsResource{client: h},
		Exports:      &ExportsResource{client: h},
	}, nil
}

// FetchToken forces an OAuth2 token exchange and returns the token data.
func (c *Client) FetchToken() (map[string]interface{}, error) {
	return c.http.FetchToken()
}

// SetToken installs a pre-issued access token.
func (c *Client) SetToken(token string) {
	c.http.SetToken(token)
}
