package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: AuthenticationException. */
public class AuthenticationException extends CRMException {
    public AuthenticationException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
