package crm

import "fmt"

// Error is the base error type returned by the CRM API.
type Error struct {
	StatusCode int
	Code       string
	Message    string
	Errors     map[string]interface{}
}

func (e *Error) Error() string {
	if e.Code != "" {
		return fmt.Sprintf("crm: [%d %s] %s", e.StatusCode, e.Code, e.Message)
	}
	return fmt.Sprintf("crm: [%d] %s", e.StatusCode, e.Message)
}

// AuthenticationError represents a 401 response.
type AuthenticationError struct{ *Error }

// AuthorizationError represents a 403 response.
type AuthorizationError struct{ *Error }

// NotFoundError represents a 404 response.
type NotFoundError struct{ *Error }

// ConflictError represents a 409 response.
type ConflictError struct{ *Error }

// ValidationError represents a 400/422 response.
type ValidationError struct{ *Error }

// RateLimitError represents a 429 response and carries Retry-After seconds.
type RateLimitError struct {
	*Error
	RetryAfter int
}

// ServerError represents a 5xx response.
type ServerError struct{ *Error }

func mapError(status int, code, message string, errs map[string]interface{}, retryAfter int) error {
	base := &Error{StatusCode: status, Code: code, Message: message, Errors: errs}
	switch status {
	case 400, 422:
		return &ValidationError{base}
	case 401:
		return &AuthenticationError{base}
	case 403:
		return &AuthorizationError{base}
	case 404:
		return &NotFoundError{base}
	case 409:
		return &ConflictError{base}
	case 429:
		return &RateLimitError{Error: base, RetryAfter: retryAfter}
	default:
		if status >= 500 {
			return &ServerError{base}
		}
		return base
	}
}
