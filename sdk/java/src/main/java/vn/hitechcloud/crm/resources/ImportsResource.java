package vn.hitechcloud.crm.resources;

import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.HttpClient;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;

/** Asynchronous CSV import jobs. */
public class ImportsResource {
    private final HttpClient http;

    public ImportsResource(HttpClient http) {
        this.http = http;
    }

    /** POST /v1/imports — start a CSV import job (entity: contact|company). */
    public Map<String, Object> create(Path file, String entity) throws CRMException {
        return http.postFile("/v1/imports", "file", file, Collections.singletonMap("entity", entity));
    }

    public Map<String, Object> get(String id) throws CRMException {
        return http.get("/v1/imports/" + URLEncoder.encode(id, StandardCharsets.UTF_8), Collections.emptyMap());
    }
}
