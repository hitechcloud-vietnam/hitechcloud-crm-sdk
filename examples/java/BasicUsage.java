// HiTechCloud CRM — Java example
//
// Build with the vn.hitechcloud:crm-sdk dependency, then:
//   CRM_CLIENT_ID=... CRM_CLIENT_SECRET=... java BasicUsage.java   (Java 11+ single-file)

import vn.hitechcloud.crm.CRMClient;
import vn.hitechcloud.crm.CRMException;
import vn.hitechcloud.crm.NotFoundException;
import vn.hitechcloud.crm.RateLimitException;

import java.util.List;
import java.util.Map;

public class BasicUsage {
    public static void main(String[] args) throws CRMException {
        CRMClient crm = new CRMClient(
                System.getenv("CRM_CLIENT_ID"),
                System.getenv("CRM_CLIENT_SECRET"),
                "contacts:read contacts:write deals:read deals:write",
                null,
                CRMClient.SANDBOX_URL,
                30,
                3);

        // Create a contact
        Map<String, Object> created = crm.contacts().create(Map.of(
                "first_name", "Nguyen",
                "last_name", "Van A",
                "email", "vana@example.com",
                "phone", "0901234567",
                "lifecycle_stage", "lead"));
        @SuppressWarnings("unchecked")
        Map<String, Object> data = (Map<String, Object>) created.get("data");
        String contactId = (String) data.get("id");
        System.out.println("Created contact: " + contactId);

        // Update + fetch
        crm.contacts().update(contactId, Map.of("lifecycle_stage", "customer"));
        System.out.println("Contact: " + crm.contacts().get(contactId).get("data"));

        // List with filter
        Map<String, Object> customers = crm.contacts().list(Map.of("lifecycle_stage", "customer", "per_page", "50"));
        System.out.println("Customers meta: " + customers.get("meta"));

        // Create a deal
        Map<String, Object> deal = crm.deals().create(Map.of(
                "title", "Goi Cloud Server",
                "pipeline_id", "pl_sales",
                "stage_id", "stg_qualified",
                "amount", 24000000,
                "contact_id", contactId));
        System.out.println("Created deal: " + deal.get("data"));

        // Register a webhook
        crm.webhooks().register("https://your-app.vn/hooks/crm",
                List.of("contact.created", "deal.won"), "whsec_6b3c15aa");

        // Error handling
        try {
            crm.contacts().get("con_missing");
        } catch (NotFoundException e) {
            System.out.println("Contact not found (as expected)");
        } catch (RateLimitException e) {
            System.out.println("Rate limited; retry after " + e.getRetryAfter());
        }
    }
}
