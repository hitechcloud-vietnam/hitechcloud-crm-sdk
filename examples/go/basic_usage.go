// HiTechCloud CRM — Go example
//
// Run:
//   go mod init example && go get github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go
//   CRM_CLIENT_ID=... CRM_CLIENT_SECRET=... go run basic_usage.go
package main

import (
	"errors"
	"fmt"
	"log"
	"os"

	crm "github.com/hitechcloud-vietnam/hitechcloud-crm-sdk/go"
)

func main() {
	client, err := crm.NewClient(
		crm.WithClientCredentials(
			os.Getenv("CRM_CLIENT_ID"),
			os.Getenv("CRM_CLIENT_SECRET"),
			"contacts:read contacts:write deals:read deals:write",
		),
		crm.WithSandbox(),
	)
	if err != nil {
		log.Fatal(err)
	}

	// Create a contact
	created, err := client.Contacts.Create(map[string]interface{}{
		"first_name":      "Nguyen",
		"last_name":       "Van A",
		"email":           "vana@example.com",
		"phone":           "0901234567",
		"lifecycle_stage": "lead",
	})
	if err != nil {
		log.Fatal(err)
	}
	data := created["data"].(map[string]interface{})
	contactID := data["id"].(string)
	fmt.Println("Created contact:", contactID)

	// Update + fetch
	if _, err := client.Contacts.Update(contactID, map[string]interface{}{"lifecycle_stage": "customer"}); err != nil {
		log.Fatal(err)
	}

	// List with filter
	customers, err := client.Contacts.List(map[string]string{"lifecycle_stage": "customer", "per_page": "50"})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Customers payload: %v\n", customers["meta"])

	// Create a deal
	deal, err := client.Deals.Create(map[string]interface{}{
		"title":       "Goi Cloud Server",
		"pipeline_id": "pl_sales",
		"stage_id":    "stg_qualified",
		"amount":      24000000,
		"contact_id":  contactID,
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Created deal:", deal["data"].(map[string]interface{})["id"])

	// Register a webhook
	if _, err := client.Webhooks.Register(
		"https://your-app.vn/hooks/crm",
		[]string{"contact.created", "deal.won"},
		"whsec_6b3c15aa",
	); err != nil {
		log.Fatal(err)
	}

	// Error handling
	_, err = client.Contacts.Get("con_missing")
	var nf *crm.NotFoundError
	var rl *crm.RateLimitError
	switch {
	case errors.As(err, &nf):
		fmt.Println("Contact not found (as expected)")
	case errors.As(err, &rl):
		fmt.Println("Rate limited; retry after", rl.RetryAfter)
	}
}
