package vn.hitechcloud.crm.resources;

import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.HttpClient;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Webhook registration management. */
public class WebhooksResource {
    private final HttpClient http;

    public WebhooksResource(HttpClient http) {
        this.http = http;
    }

    public Map<String, Object> list() throws CRMException {
        return http.get("/v1/webhooks", Collections.emptyMap());
    }

    /** Register a webhook endpoint. Pass null for secret to omit it. */
    public Map<String, Object> register(String url, List<String> events, String secret) throws CRMException {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("url", url);
        body.put("events", events);
        if (secret != null) {
            body.put("secret", secret);
        }
        return http.post("/v1/webhooks", body);
    }

    public Map<String, Object> delete(String id) throws CRMException {
        return http.delete("/v1/webhooks/" + URLEncoder.encode(id, StandardCharsets.UTF_8));
    }
}
