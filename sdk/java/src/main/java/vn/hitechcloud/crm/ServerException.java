package vn.hitechcloud.crm;

import java.util.Map;

/** CRM API exception: ServerException. */
public class ServerException extends CRMException {
    public ServerException(String message, int statusCode, String code, Map<String, Object> errors) {
        super(message, statusCode, code, errors);
    }
}
