<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Resources;

use HiTechCloud\CRM\HttpClient;

/**
 * Asynchronous CSV import jobs.
 */
class Imports
{
    private HttpClient $http;

    public function __construct(HttpClient $http)
    {
        $this->http = $http;
    }

    /**
     * POST /v1/imports — start a CSV import job (entity: contact|company).
     *
     * @return array<string, mixed>
     */
    public function create(string $filePath, string $entity): array
    {
        $multipart = [
            [
                'name' => 'file',
                'contents' => fopen($filePath, 'r'),
                'filename' => basename($filePath),
            ],
            ['name' => 'entity', 'contents' => $entity],
        ];
        return $this->http->postMultipart('/v1/imports', $multipart);
    }

    /** @return array<string, mixed> */
    public function get(string $id): array
    {
        return $this->http->get('/v1/imports/' . rawurlencode($id));
    }
}
