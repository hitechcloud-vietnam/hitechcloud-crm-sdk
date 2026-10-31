<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Resources;

use HiTechCloud\CRM\HttpClient;

/**
 * Asynchronous CSV export jobs.
 */
class Exports
{
    private HttpClient $http;

    public function __construct(HttpClient $http)
    {
        $this->http = $http;
    }

    /**
     * POST /v1/exports — start a CSV export job (entity: contact|deal|activity).
     *
     * @param array<string, mixed> $filter
     * @return array<string, mixed>
     */
    public function create(string $entity, array $filter = []): array
    {
        $body = ['entity' => $entity];
        if ($filter) {
            $body['filter'] = $filter;
        }
        return $this->http->post('/v1/exports', $body);
    }

    /** @return array<string, mixed> */
    public function get(string $id): array
    {
        return $this->http->get('/v1/exports/' . rawurlencode($id));
    }
}
