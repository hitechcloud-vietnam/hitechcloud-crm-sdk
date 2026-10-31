package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: ValidationException. */
public class ValidationException extends CRMException {
    public ValidationException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
