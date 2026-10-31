// HiTechCloud CRM — Node.js example (ESM)
//
// Run:
//   npm install @hitechcloud-vietnam/crm-sdk
//   CRM_CLIENT_ID=... CRM_CLIENT_SECRET=... node basic_usage.mjs

import { CRMClient, NotFoundError, RateLimitError } from "@hitechcloud-vietnam/crm-sdk";

async function main() {
  const crm = new CRMClient({
    clientId: process.env.CRM_CLIENT_ID,
    clientSecret: process.env.CRM_CLIENT_SECRET,
    scope: "contacts:read contacts:write deals:read deals:write",
    sandbox: true,
  });

  // Create a contact
  const created = await crm.contacts.create({
    first_name: "Nguyen",
    last_name: "Van A",
    email: "vana@example.com",
    phone: "0901234567",
    lifecycle_stage: "lead",
  });
  const contactId = created.data.id;
  console.log("Created contact:", contactId);

  // Update + fetch
  await crm.contacts.update(contactId, { lifecycle_stage: "customer", tags: ["vip"] });
  console.log("Contact:", (await crm.contacts.get(contactId)).data);

  // List with filter
  const customers = await crm.contacts.list({ lifecycle_stage: "customer", per_page: 50 });
  console.log("Customers on page 1:", customers.data.length);

  // Create a deal
  const deal = await crm.deals.create({
    title: "Goi Cloud Server",
    pipeline_id: "pl_sales",
    stage_id: "stg_qualified",
    amount: 24000000,
    contact_id: contactId,
  });
  console.log("Created deal:", deal.data.id);

  // Register a webhook
  await crm.webhooks.register(
    "https://your-app.vn/hooks/crm",
    ["contact.created", "deal.won"],
    "whsec_6b3c15aa"
  );

  // Error handling
  try {
    await crm.contacts.get("con_missing");
  } catch (e) {
    if (e instanceof NotFoundError) console.log("Contact not found (as expected)");
    else if (e instanceof RateLimitError) console.log("Rate limited; retry after", e.retryAfter);
    else throw e;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
