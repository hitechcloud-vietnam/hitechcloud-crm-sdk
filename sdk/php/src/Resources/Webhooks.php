<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Resources;

use HiTechCloud\CRM\HttpClient;

/**
 * Webhook registration management.
 */
class Webhooks
{
    private HttpClient $http;

    public function __construct(HttpClient $http)
    {
        $this->http = $http;
    }

    /** @return array<string, mixed> */
    public function list(): array
    {
        return $this->http->get('/v1/webhooks');
    }

    /**
     * @param array<int, string> $events
     * @return array<string, mixed>
     */
    public function register(string $url, array $events, ?string $secret = null): array
    {
        $body = ['url' => $url, 'events' => $events];
        if ($secret !== null) {
            $body['secret'] = $secret;
        }
        return $this->http->post('/v1/webhooks', $body);
    }

    /** @return array<string, mixed> */
    public function delete(string $id): array
    {
        return $this->http->delete('/v1/webhooks/' . rawurlencode($id));
    }
}
