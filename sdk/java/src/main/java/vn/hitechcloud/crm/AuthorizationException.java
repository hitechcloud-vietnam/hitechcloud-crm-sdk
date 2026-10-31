package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: AuthorizationException. */
public class AuthorizationException extends CRMException {
    public AuthorizationException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
