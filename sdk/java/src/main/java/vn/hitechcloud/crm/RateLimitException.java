package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception raised on a 429 response; carries Retry-After seconds. */
public class RateLimitException extends CRMException {
    private final int retryAfter;

    public RateLimitException(String message, String code, Map<String, Object> errors, int retryAfter) {
        super(message, 429, code, errors);
        this.retryAfter = retryAfter;
    }

    public int getRetryAfter() {
        return retryAfter;
    }
}
