package crm

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"strings"
)

// ComputeSignature returns the expected hex HMAC-SHA256 signature for rawBody.
func ComputeSignature(rawBody []byte, secret string) string {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(rawBody)
	return hex.EncodeToString(mac.Sum(nil))
}

// VerifyWebhookSignature verifies an X-CRM-Signature header against rawBody
// using a constant-time comparison.
//
//	rawBody   the exact raw request body received.
//	signature the value of the X-CRM-Signature header.
//	secret    the webhook secret registered with the endpoint.
func VerifyWebhookSignature(rawBody []byte, signature, secret string) bool {
	if signature == "" {
		return false
	}
	expected := ComputeSignature(rawBody, secret)
	return hmac.Equal([]byte(expected), []byte(strings.TrimSpace(signature)))
}
