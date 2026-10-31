package vn.hitechcloud.crm;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CRMClientTest {
    private CRMClient client() {
        return new CRMClient(null, null, null, "crm_at_test", CRMClient.SANDBOX_URL, 30, 3);
    }

    @Test
    void exposesResources() {
        CRMClient crm = client();
        assertEquals("contacts", crm.contacts().path());
        assertEquals("custom-fields", crm.customFields().path());
        assertEquals("lead-sources", crm.leadSources().path());
        assertNotNull(crm.files());
        assertNotNull(crm.webhooks());
        assertNotNull(crm.imports());
        assertNotNull(crm.exports());
    }

    @Test
    void bulkGuard() {
        CRMClient crm = client();
        assertThrows(IllegalArgumentException.class,
                () -> crm.companies().bulk(java.util.List.of(java.util.Map.of("op", "create", "data", java.util.Map.of()))));
    }

    @Test
    void webhookSignatureRoundtrip() {
        String secret = "whsec_6b3c15aa";
        String body = "{\"event\":\"deal.won\",\"id\":\"evt_1\"}";
        String sig = Webhook.computeSignature(body, secret);
        assertTrue(Webhook.verifySignature(body, sig, secret));
        assertFalse(Webhook.verifySignature(body, "deadbeef", secret));
        assertFalse(Webhook.verifySignature(body, "", secret));
    }
}
