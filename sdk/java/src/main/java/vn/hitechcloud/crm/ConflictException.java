package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: ConflictException. */
public class ConflictException extends CRMException {
    public ConflictException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
