package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: NotFoundException. */
public class NotFoundException extends CRMException {
    public NotFoundException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
