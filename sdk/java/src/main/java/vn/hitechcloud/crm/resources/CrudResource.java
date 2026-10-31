package vn.hitechcloud.crm.resources;

import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.HttpClient;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Generic CRUD resource bound to a collection path (e.g. "contacts"). */
public class CrudResource {
    private static final Set<String> BULK = Set.of("contacts", "deals");

    protected final HttpClient http;
    protected final String path;

    public CrudResource(HttpClient http, String path) {
        this.http = http;
        this.path = path;
    }

    public String path() {
        return path;
    }

    /** GET /v1/{path} — list records with pagination and filters. */
    public Map<String, Object> list(Map<String, String> params) throws CRMException {
        return http.get("/v1/" + path, params == null ? Collections.emptyMap() : params);
    }

    public Map<String, Object> list() throws CRMException {
        return list(Collections.emptyMap());
    }

    /** GET /v1/{path}/{id} — fetch a single record. */
    public Map<String, Object> get(String id) throws CRMException {
        return http.get("/v1/" + path + "/" + enc(id), Collections.emptyMap());
    }

    /** POST /v1/{path} — create a record. */
    public Map<String, Object> create(Map<String, Object> data) throws CRMException {
        return http.post("/v1/" + path, data);
    }

    /** PATCH /v1/{path}/{id} — partially update a record. */
    public Map<String, Object> update(String id, Map<String, Object> data) throws CRMException {
        return http.patch("/v1/" + path + "/" + enc(id), data);
    }

    /** DELETE /v1/{path}/{id} — delete a record. */
    public Map<String, Object> delete(String id) throws CRMException {
        return http.delete("/v1/" + path + "/" + enc(id));
    }

    /** POST /v1/{path}/bulk — up to 100 create/update/delete operations. */
    public Map<String, Object> bulk(List<Map<String, Object>> operations) throws CRMException {
        if (!BULK.contains(path)) {
            throw new IllegalArgumentException("Bulk operations are not supported for " + path);
        }
        return http.post("/v1/" + path + "/bulk", Collections.singletonMap("operations", operations));
    }

    protected static String enc(String s) {
        return URLEncoder.encode(s, StandardCharsets.UTF_8);
    }
}
