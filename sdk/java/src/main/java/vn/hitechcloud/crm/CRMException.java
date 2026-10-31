package vn.hitechcloud.crm;

import java.util.Collections;
import java.util.Map;

/** Base exception for the HiTechCloud CRM SDK. */
public class CRMException extends Exception {
    private final int statusCode;
    private final String code;
    private final Map<String, Object> errors;

    public CRMException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message);
        this.statusCode = statusCode;
        this.code = code;
        this.errors = errors == null ? Collections.emptyMap() : errors;
    }

    public CRMException(String message) {
        this(message, 0, null, null);
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getCode() {
        return code;
    }

    public Map<String, Object> getErrors() {
        return errors;
    }
}
