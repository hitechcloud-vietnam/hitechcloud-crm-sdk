package vn.hitechcloud.crm.resources;

import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.HttpClient;

import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Map;

/** Files: multipart upload, metadata and binary download URL. */
public class FilesResource extends CrudResource {
    public FilesResource(HttpClient http) {
        super(http, "files");
    }

    /** POST /v1/files — upload a file and attach it to a resource. */
    public Map<String, Object> upload(Path file, String resourceType, String resourceId) throws CRMException {
        Map<String, String> fields = new LinkedHashMap<>();
        fields.put("resource_type", resourceType);
        fields.put("resource_id", resourceId);
        return http.postFile("/v1/files", "file", file, fields);
    }

    public String downloadUrl(String id) {
        return http.baseUrl() + "/v1/files/" + enc(id) + "/download";
    }

    @Override
    public Map<String, Object> create(Map<String, Object> data) {
        throw new UnsupportedOperationException("Use FilesResource.upload() to create files");
    }
}
