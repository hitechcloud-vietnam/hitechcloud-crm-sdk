"""HiTechCloud CRM — Python example.

Run:
    pip install hitechcloud-crm
    export CRM_CLIENT_ID=... CRM_CLIENT_SECRET=...
    python basic_usage.py
"""

import os

from hitechcloud_crm import CRMClient, NotFoundError, RateLimitError


def main() -> None:
    crm = CRMClient(
        client_id=os.environ["CRM_CLIENT_ID"],
        client_secret=os.environ["CRM_CLIENT_SECRET"],
        scope="contacts:read contacts:write deals:read deals:write",
        sandbox=True,
    )

    # Create a contact
    created = crm.contacts.create(
        first_name="Nguyen",
        last_name="Van A",
        email="vana@example.com",
        phone="0901234567",
        lifecycle_stage="lead",
    )
    contact_id = created["data"]["id"]
    print("Created contact:", contact_id)

    # Update + fetch
    crm.contacts.update(contact_id, lifecycle_stage="customer", tags=["vip"])
    print("Contact:", crm.contacts.get(contact_id)["data"])

    # List with filter + pagination
    customers = crm.contacts.list(lifecycle_stage="customer", per_page=50)
    print("Customers on page 1:", len(customers["data"]))

    # Create a deal
    deal = crm.deals.create(
        title="Goi Cloud Server",
        pipeline_id="pl_sales",
        stage_id="stg_qualified",
        amount=24000000,
        contact_id=contact_id,
    )
    print("Created deal:", deal["data"]["id"])

    # Register a webhook
    crm.webhooks.register(
        "https://your-app.vn/hooks/crm",
        events=["contact.created", "deal.won"],
        secret="whsec_6b3c15aa",
    )

    # Error handling
    try:
        crm.contacts.get("con_missing")
    except NotFoundError:
        print("Contact not found (as expected)")
    except RateLimitError as exc:
        print("Rate limited; retry after", exc.retry_after)


if __name__ == "__main__":
    main()
