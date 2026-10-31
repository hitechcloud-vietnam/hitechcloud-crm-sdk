package vn.hitechcloud.crm;

import vn.hitechcloud.crm.resources.CrudResource;
import vn.hitechcloud.crm.resources.ExportsResource;
import vn.hitechcloud.crm.resources.FilesResource;
import vn.hitechcloud.crm.resources.ImportsResource;
import vn.hitechcloud.crm.resources.WebhooksResource;

import java.util.Map;

/**
 * HiTechCloud CRM client.
 *
 * <pre>
 * CRMClient crm = new CRMClient("CLIENT_ID", "CLIENT_SECRET", "contacts:read contacts:write");
 * Map&lt;String, Object&gt; customers = crm.contacts().list(Map.of("lifecycle_stage", "customer"));
 * </pre>
 */
public class CRMClient {
    public static final String PRODUCTION_URL = "https://crm-gateways.hitechcloud.vn";
    public static final String SANDBOX_URL = "https://crm-gateways-sandbox.hitechcloud.vn";
    public static final String VERSION = "1.0.0";

    private final HttpClient http;

    private final CrudResource contacts;
    private final CrudResource companies;
    private final CrudResource deals;
    private final CrudResource pipelines;
    private final CrudResource stages;
    private final CrudResource activities;
    private final CrudResource tasks;
    private final CrudResource calls;
    private final CrudResource emails;
    private final CrudResource meetings;
    private final CrudResource notes;
    private final CrudResource tags;
    private final CrudResource segments;
    private final CrudResource customFields;
    private final CrudResource leadSources;
    private final CrudResource products;
    private final CrudResource quotes;
    private final CrudResource users;
    private final CrudResource teams;

    private final FilesResource files;
    private final WebhooksResource webhooks;
    private final ImportsResource imports;
    private final ExportsResource exports;

    /** Build a client from OAuth2 client credentials against production. */
    public CRMClient(String clientId, String clientSecret, String scope) {
        this(clientId, clientSecret, scope, null, PRODUCTION_URL, 30, 3);
    }

    /** Build a client from a pre-issued access token. */
    public static CRMClient withToken(String token) {
        return new CRMClient(null, null, null, token, PRODUCTION_URL, 30, 3);
    }

    public CRMClient(String clientId, String clientSecret, String scope, String token,
                     String baseUrl, int timeout, int maxRetries) {
        this.http = new HttpClient(baseUrl, clientId, clientSecret, scope, token, timeout, maxRetries);
        this.contacts = new CrudResource(http, "contacts");
        this.companies = new CrudResource(http, "companies");
        this.deals = new CrudResource(http, "deals");
        this.pipelines = new CrudResource(http, "pipelines");
        this.stages = new CrudResource(http, "stages");
        this.activities = new CrudResource(http, "activities");
        this.tasks = new CrudResource(http, "tasks");
        this.calls = new CrudResource(http, "calls");
        this.emails = new CrudResource(http, "emails");
        this.meetings = new CrudResource(http, "meetings");
        this.notes = new CrudResource(http, "notes");
        this.tags = new CrudResource(http, "tags");
        this.segments = new CrudResource(http, "segments");
        this.customFields = new CrudResource(http, "custom-fields");
        this.leadSources = new CrudResource(http, "lead-sources");
        this.products = new CrudResource(http, "products");
        this.quotes = new CrudResource(http, "quotes");
        this.users = new CrudResource(http, "users");
        this.teams = new CrudResource(http, "teams");
        this.files = new FilesResource(http);
        this.webhooks = new WebhooksResource(http);
        this.imports = new ImportsResource(http);
        this.exports = new ExportsResource(http);
    }

    public CrudResource contacts() { return contacts; }
    public CrudResource companies() { return companies; }
    public CrudResource deals() { return deals; }
    public CrudResource pipelines() { return pipelines; }
    public CrudResource stages() { return stages; }
    public CrudResource activities() { return activities; }
    public CrudResource tasks() { return tasks; }
    public CrudResource calls() { return calls; }
    public CrudResource emails() { return emails; }
    public CrudResource meetings() { return meetings; }
    public CrudResource notes() { return notes; }
    public CrudResource tags() { return tags; }
    public CrudResource segments() { return segments; }
    public CrudResource customFields() { return customFields; }
    public CrudResource leadSources() { return leadSources; }
    public CrudResource products() { return products; }
    public CrudResource quotes() { return quotes; }
    public CrudResource users() { return users; }
    public CrudResource teams() { return teams; }

    public FilesResource files() { return files; }
    public WebhooksResource webhooks() { return webhooks; }
    public ImportsResource imports() { return imports; }
    public ExportsResource exports() { return exports; }

    /** Force an OAuth2 token exchange and return the token data. */
    public Map<String, Object> fetchToken() throws CRMException {
        return http.fetchToken();
    }

    public void setToken(String token) {
        http.setToken(token);
    }
}
