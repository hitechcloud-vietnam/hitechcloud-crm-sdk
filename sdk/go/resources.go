package crm

import (
	"fmt"
	"net/url"
)

// Response is the decoded JSON envelope returned by the API.
type Response = map[string]interface{}

// BulkOperation is one entry in a bulk request.
type BulkOperation struct {
	Op   string                 `json:"op"`
	Data map[string]interface{} `json:"data"`
}

var bulkResources = map[string]bool{"contacts": true, "deals": true}

// CrudResource is a generic REST resource bound to a collection path.
type CrudResource struct {
	client *httpClient
	path   string
}

// List performs GET /v1/{path} with optional query params.
func (r *CrudResource) List(params map[string]string) (Response, error) {
	return r.client.Get("/v1/"+r.path, params)
}

// Get performs GET /v1/{path}/{id}.
func (r *CrudResource) Get(id string) (Response, error) {
	return r.client.Get("/v1/"+r.path+"/"+url.PathEscape(id), nil)
}

// Create performs POST /v1/{path}.
func (r *CrudResource) Create(data map[string]interface{}) (Response, error) {
	return r.client.Post("/v1/"+r.path, data)
}

// Update performs PATCH /v1/{path}/{id}.
func (r *CrudResource) Update(id string, data map[string]interface{}) (Response, error) {
	return r.client.Patch("/v1/"+r.path+"/"+url.PathEscape(id), data)
}

// Delete performs DELETE /v1/{path}/{id}.
func (r *CrudResource) Delete(id string) (Response, error) {
	return r.client.Delete("/v1/" + r.path + "/" + url.PathEscape(id))
}

// Bulk performs POST /v1/{path}/bulk (contacts and deals only).
func (r *CrudResource) Bulk(operations []BulkOperation) (Response, error) {
	if !bulkResources[r.path] {
		return nil, fmt.Errorf("crm: bulk operations are not supported for %s", r.path)
	}
	return r.client.Post("/v1/"+r.path+"/bulk", map[string]interface{}{"operations": operations})
}

// FilesResource handles file upload, metadata and download.
type FilesResource struct {
	*CrudResource
}

// Upload uploads a local file and attaches it to a resource.
func (r *FilesResource) Upload(filePath, resourceType, resourceID string) (Response, error) {
	return r.client.PostFile("/v1/files", "file", filePath, map[string]string{
		"resource_type": resourceType,
		"resource_id":   resourceID,
	})
}

// DownloadURL returns the binary download URL for a file.
func (r *FilesResource) DownloadURL(id string) string {
	return r.client.baseURL + "/v1/files/" + url.PathEscape(id) + "/download"
}

// WebhooksResource manages webhook registrations.
type WebhooksResource struct {
	client *httpClient
}

// List returns registered webhooks.
func (r *WebhooksResource) List() (Response, error) {
	return r.client.Get("/v1/webhooks", nil)
}

// Register registers a webhook endpoint. Pass "" for secret to omit it.
func (r *WebhooksResource) Register(endpointURL string, events []string, secret string) (Response, error) {
	body := map[string]interface{}{"url": endpointURL, "events": events}
	if secret != "" {
		body["secret"] = secret
	}
	return r.client.Post("/v1/webhooks", body)
}

// Delete removes a webhook registration.
func (r *WebhooksResource) Delete(id string) (Response, error) {
	return r.client.Delete("/v1/webhooks/" + url.PathEscape(id))
}

// ImportsResource manages asynchronous CSV import jobs.
type ImportsResource struct {
	client *httpClient
}

// Create starts a CSV import job (entity: contact|company).
func (r *ImportsResource) Create(filePath, entity string) (Response, error) {
	return r.client.PostFile("/v1/imports", "file", filePath, map[string]string{"entity": entity})
}

// Get returns the status of an import job.
func (r *ImportsResource) Get(id string) (Response, error) {
	return r.client.Get("/v1/imports/"+url.PathEscape(id), nil)
}

// ExportsResource manages asynchronous CSV export jobs.
type ExportsResource struct {
	client *httpClient
}

// Create starts a CSV export job (entity: contact|deal|activity). filter may be nil.
func (r *ExportsResource) Create(entity string, filter map[string]interface{}) (Response, error) {
	body := map[string]interface{}{"entity": entity}
	if filter != nil {
		body["filter"] = filter
	}
	return r.client.Post("/v1/exports", body)
}

// Get returns the status and download link of an export job.
func (r *ExportsResource) Get(id string) (Response, error) {
	return r.client.Get("/v1/exports/"+url.PathEscape(id), nil)
}
