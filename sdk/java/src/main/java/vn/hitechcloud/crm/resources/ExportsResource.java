package vn.hitechcloud.crm.resources;

import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.HttpClient;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/** Asynchronous CSV export jobs. */
public class ExportsResource {
    private final HttpClient http;

    public ExportsResource(HttpClient http) {
        this.http = http;
    }

    /** POST /v1/exports — start a CSV export job (entity: contact|deal|activity). */
    public Map<String, Object> create(String entity, Map<String, Object> filter) throws CRMException {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("entity", entity);
        if (filter != null) {
            body.put("filter", filter);
        }
        return http.post("/v1/exports", body);
    }

    public Map<String, Object> get(String id) throws CRMException {
        return http.get("/v1/exports/" + URLEncoder.encode(id, StandardCharsets.UTF_8), Collections.emptyMap());
    }
}
