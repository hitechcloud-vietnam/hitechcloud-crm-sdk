# HiTechCloud CRM SDK for PHP

Official PHP SDK for the [HiTechCloud CRM API](https://developers.hitechcloud.vn).
Requires PHP 8.0+ and Guzzle 7.

## Install

```bash
composer require hitechcloud-vietnam/crm-sdk
```

## Authentication

The client uses the OAuth2 `client_credentials` flow and manages the access
token for you:

```php
use HiTechCloud\CRM\Client;

$crm = new Client([
    'client_id' => 'YOUR_CLIENT_ID',
    'client_secret' => 'YOUR_CLIENT_SECRET',
    'scope' => 'contacts:read contacts:write deals:read deals:write',
    // 'sandbox' => true,
]);
```

You may also pass `'token' => 'crm_at_...'` to use a pre-issued token.

## Usage

```php
$customers = $crm->contacts()->list(['lifecycle_stage' => 'customer', 'per_page' => 100]);

$created = $crm->contacts()->create(['first_name' => 'Nguyen', 'email' => 'vana@example.com']);
$id = $created['data']['id'];
$crm->contacts()->update($id, ['lifecycle_stage' => 'customer']);
$crm->contacts()->get($id);
$crm->contacts()->delete($id);

$crm->deals()->create([
    'title' => 'Goi Cloud Server',
    'pipeline_id' => 'pl_sales',
    'stage_id' => 'stg_qualified',
    'amount' => 24000000,
]);

// Bulk (contacts, deals)
$crm->contacts()->bulk([
    ['op' => 'create', 'data' => ['first_name' => 'A', 'email' => 'a@example.com']],
    ['op' => 'delete', 'data' => ['id' => 'con_0011aabb']],
]);

// Files, import/export
$crm->files()->upload('hopdong.pdf', 'deal', 'deal_a19c330e');
$crm->imports()->create('contacts.csv', 'contact');
$crm->exports()->create('contact', ['lifecycle_stage' => 'customer']);

// Webhooks
$crm->webhooks()->register('https://your-app.vn/hooks/crm', ['contact.created', 'deal.won'], 'whsec_6b3c15aa');
```

## Verifying webhooks

```php
use HiTechCloud\CRM\Webhook;

$raw = file_get_contents('php://input');
$sig = $_SERVER['HTTP_X_CRM_SIGNATURE'] ?? '';
if (!Webhook::verifySignature($raw, $sig, 'whsec_6b3c15aa')) {
    http_response_code(400);
    exit;
}
```

## Error handling

```php
use HiTechCloud\CRM\NotFoundException;
use HiTechCloud\CRM\RateLimitException;

try {
    $crm->contacts()->get('con_missing');
} catch (NotFoundException $e) {
    // ...
} catch (RateLimitException $e) {
    echo "retry after {$e->retryAfter}s";
}
```

## License

MIT
