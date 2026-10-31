package vn.hitechcloud.crm;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.IOException;
import java.lang.reflect.Type;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;

/**
 * Low-level HTTP transport with OAuth2 client_credentials token management.
 */
public class HttpClient {
    public static final String VERSION = "1.0.0";
    private static final String TOKEN_PATH = "/v1/oauth/token";

    private final String baseUrl;
    private final int maxRetries;
    private final java.net.http.HttpClient client;
    private final Gson gson = new Gson();
    private static final Type MAP_TYPE = new TypeToken<Map<String, Object>>() {}.getType();

    private final String clientId;
    private final String clientSecret;
    private final String scope;
    private String token;
    private Instant tokenExpiry = Instant.EPOCH;

    public HttpClient(String baseUrl, String clientId, String clientSecret, String scope,
                      String token, int timeout, int maxRetries) {
        this.baseUrl = baseUrl.replaceAll("/+$", "");
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.scope = scope;
        this.token = token;
        this.maxRetries = maxRetries;
        if (token != null) {
            this.tokenExpiry = Instant.MAX;
        }
        this.client = java.net.http.HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(timeout))
                .build();
    }

    public String baseUrl() {
        return baseUrl;
    }

    public void setToken(String token) {
        this.token = token;
        this.tokenExpiry = Instant.MAX;
    }

    public Map<String, Object> fetchToken() throws CRMException {
        if (clientId == null || clientSecret == null) {
            throw new CRMException("No client credentials configured");
        }
        Map<String, Object> payload = new java.util.HashMap<>();
        payload.put("grant_type", "client_credentials");
        payload.put("client_id", clientId);
        payload.put("client_secret", clientSecret);
        if (scope != null) {
            payload.put("scope", scope);
        }
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + TOKEN_PATH))
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .header("User-Agent", "hitechcloud-crm-java/" + VERSION)
                .POST(HttpRequest.BodyPublishers.ofString(gson.toJson(payload)))
                .build();
        try {
            HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
            Map<String, Object> body = decode(resp.body());
            if (resp.statusCode() >= 400) {
                throw mapError(resp.statusCode(), body, retryAfter(resp));
            }
            @SuppressWarnings("unchecked")
            Map<String, Object> data = (Map<String, Object>) body.getOrDefault("data", new java.util.HashMap<>());
            this.token = (String) data.get("access_token");
            double expiresIn = data.get("expires_in") instanceof Number
                    ? ((Number) data.get("expires_in")).doubleValue() : 3600;
            long lead = Math.max((long) expiresIn - 60, 30);
            this.tokenExpiry = Instant.now().plusSeconds(lead);
            return data;
        } catch (IOException | InterruptedException e) {
            throw new CRMException("Token request failed: " + e.getMessage());
        }
    }

    private void ensureToken() throws CRMException {
        if (token != null && Instant.now().isBefore(tokenExpiry)) {
            return;
        }
        if (clientId == null || clientSecret == null) {
            if (token != null) {
                return;
            }
            throw new CRMException("No access token and no client credentials configured");
        }
        fetchToken();
    }

    private HttpRequest.Builder baseRequest(String url) {
        return HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Accept", "application/json")
                .header("User-Agent", "hitechcloud-crm-java/" + VERSION)
                .header("Authorization", "Bearer " + token);
    }

    private Map<String, Object> send(HttpRequest.Builder builder, boolean retryAuth) throws CRMException {
        ensureToken();
        for (int attempt = 0; attempt <= maxRetries; attempt++) {
            HttpRequest request = builder.setHeader("Authorization", "Bearer " + token).build();
            HttpResponse<String> resp;
            try {
                resp = client.send(request, HttpResponse.BodyHandlers.ofString());
            } catch (IOException | InterruptedException e) {
                if (attempt < maxRetries) {
                    sleep((long) Math.pow(2, attempt) * 1000);
                    continue;
                }
                throw new CRMException("Request failed: " + e.getMessage());
            }
            int status = resp.statusCode();

            if (status == 401 && retryAuth && clientId != null) {
                fetchToken();
                retryAuth = false;
                attempt--;
                continue;
            }
            if (status == 429) {
                int ra = retryAfter(resp);
                if (attempt < maxRetries) {
                    sleep(ra * 1000L);
                    continue;
                }
                throw mapError(status, decode(resp.body()), ra);
            }
            if (status >= 500 && attempt < maxRetries) {
                sleep((long) Math.pow(2, attempt) * 1000);
                continue;
            }
            Map<String, Object> body = decode(resp.body());
            if (status >= 400) {
                throw mapError(status, body, retryAfter(resp));
            }
            return body;
        }
        throw new CRMException("Request failed after retries");
    }

    public Map<String, Object> get(String path, Map<String, String> params) throws CRMException {
        String url = baseUrl + path;
        if (params != null && !params.isEmpty()) {
            StringBuilder sb = new StringBuilder(url).append('?');
            boolean first = true;
            for (Map.Entry<String, String> e : params.entrySet()) {
                if (!first) {
                    sb.append('&');
                }
                sb.append(enc(e.getKey())).append('=').append(enc(e.getValue()));
                first = false;
            }
            url = sb.toString();
        }
        return send(baseRequest(url).GET(), true);
    }

    public Map<String, Object> post(String path, Object body) throws CRMException {
        return send(baseRequest(baseUrl + path)
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(gson.toJson(body))), true);
    }

    public Map<String, Object> patch(String path, Object body) throws CRMException {
        return send(baseRequest(baseUrl + path)
                .header("Content-Type", "application/json")
                .method("PATCH", HttpRequest.BodyPublishers.ofString(gson.toJson(body))), true);
    }

    public Map<String, Object> delete(String path) throws CRMException {
        return send(baseRequest(baseUrl + path).DELETE(), true);
    }

    /** Upload a file via multipart/form-data with extra text fields. */
    public Map<String, Object> postFile(String path, String fileField, Path file,
                                        Map<String, String> fields) throws CRMException {
        String boundary = "----crmsdk" + System.nanoTime();
        try {
            byte[] body = buildMultipart(boundary, fileField, file, fields);
            return send(baseRequest(baseUrl + path)
                    .header("Content-Type", "multipart/form-data; boundary=" + boundary)
                    .POST(HttpRequest.BodyPublishers.ofByteArray(body)), true);
        } catch (IOException e) {
            throw new CRMException("File upload failed: " + e.getMessage());
        }
    }

    private byte[] buildMultipart(String boundary, String fileField, Path file,
                                  Map<String, String> fields) throws IOException {
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        String dash = "--";
        String crlf = "\r\n";
        for (Map.Entry<String, String> e : fields.entrySet()) {
            out.write((dash + boundary + crlf).getBytes(StandardCharsets.UTF_8));
            out.write(("Content-Disposition: form-data; name=\"" + e.getKey() + "\"" + crlf + crlf)
                    .getBytes(StandardCharsets.UTF_8));
            out.write((e.getValue() + crlf).getBytes(StandardCharsets.UTF_8));
        }
        out.write((dash + boundary + crlf).getBytes(StandardCharsets.UTF_8));
        out.write(("Content-Disposition: form-data; name=\"" + fileField + "\"; filename=\""
                + file.getFileName() + "\"" + crlf).getBytes(StandardCharsets.UTF_8));
        out.write(("Content-Type: application/octet-stream" + crlf + crlf).getBytes(StandardCharsets.UTF_8));
        out.write(Files.readAllBytes(file));
        out.write(crlf.getBytes(StandardCharsets.UTF_8));
        out.write((dash + boundary + dash + crlf).getBytes(StandardCharsets.UTF_8));
        return out.toByteArray();
    }

    private Map<String, Object> decode(String raw) {
        if (raw == null || raw.isEmpty()) {
            return new java.util.HashMap<>();
        }
        try {
            Map<String, Object> m = gson.fromJson(raw, MAP_TYPE);
            return m == null ? new java.util.HashMap<>() : m;
        } catch (RuntimeException e) {
            Map<String, Object> m = new java.util.HashMap<>();
            m.put("message", raw.length() > 200 ? raw.substring(0, 200) : raw);
            return m;
        }
    }

    private int retryAfter(HttpResponse<?> resp) {
        return resp.headers().firstValue("Retry-After").map(v -> {
            try {
                return Integer.parseInt(v);
            } catch (NumberFormatException e) {
                return 60;
            }
        }).orElse(60);
    }

    private CRMException mapError(int status, Map<String, Object> body, int retryAfter) {
        String message = body.get("message") instanceof String ? (String) body.get("message") : "HTTP " + status;
        String code = body.get("code") instanceof String ? (String) body.get("code") : null;
        @SuppressWarnings("unchecked")
        Map<String, Object> errors = body.get("errors") instanceof Map ? (Map<String, Object>) body.get("errors") : null;
        switch (status) {
            case 400:
            case 422:
                return new ValidationException(message, status, code, errors);
            case 401:
                return new AuthenticationException(message, status, code, errors);
            case 403:
                return new AuthorizationException(message, status, code, errors);
            case 404:
                return new NotFoundException(message, status, code, errors);
            case 409:
                return new ConflictException(message, status, code, errors);
            case 429:
                return new RateLimitException(message, code, errors, retryAfter);
            default:
                if (status >= 500) {
                    return new ServerException(message, status, code, errors);
                }
                return new CRMException(message, status, code, errors);
        }
    }

    private static String enc(String s) {
        return URLEncoder.encode(s, StandardCharsets.UTF_8);
    }

    private static void sleep(long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
