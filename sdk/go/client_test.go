package crm

import "testing"

func newTestClient(t *testing.T) *Client {
	t.Helper()
	c, err := NewClient(WithToken("crm_at_test"), WithSandbox())
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}
	return c
}

func TestResourcesWired(t *testing.T) {
	c := newTestClient(t)
	if c.Contacts.path != "contacts" {
		t.Errorf("contacts path = %q", c.Contacts.path)
	}
	if c.CustomFields.path != "custom-fields" {
		t.Errorf("custom fields path = %q", c.CustomFields.path)
	}
	if c.LeadSources.path != "lead-sources" {
		t.Errorf("lead sources path = %q", c.LeadSources.path)
	}
	if c.Files == nil || c.Webhooks == nil || c.Imports == nil || c.Exports == nil {
		t.Fatal("special resources not wired")
	}
}

func TestBulkGuard(t *testing.T) {
	c := newTestClient(t)
	if _, err := c.Companies.Bulk([]BulkOperation{{Op: "create", Data: map[string]interface{}{}}}); err == nil {
		t.Fatal("expected error for non-bulk resource")
	}
}

func TestWebhookSignatureRoundtrip(t *testing.T) {
	secret := "whsec_6b3c15aa"
	body := []byte(`{"event":"deal.won","id":"evt_1"}`)
	sig := ComputeSignature(body, secret)
	if !VerifyWebhookSignature(body, sig, secret) {
		t.Error("expected valid signature to verify")
	}
	if VerifyWebhookSignature(body, "deadbeef", secret) {
		t.Error("expected invalid signature to fail")
	}
	if VerifyWebhookSignature(body, "", secret) {
		t.Error("expected empty signature to fail")
	}
}
