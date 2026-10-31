<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Resources;

use HiTechCloud\CRM\HttpClient;

/**
 * Files: multipart upload, metadata and binary download URL.
 */
class Files extends Resource
{
    public function __construct(HttpClient $http)
    {
        parent::__construct($http, 'files');
    }

    /**
     * POST /v1/files — upload a file and attach it to a resource.
     *
     * @return array<string, mixed>
     */
    public function upload(string $filePath, string $resourceType, string $resourceId): array
    {
        $multipart = [
            [
                'name' => 'file',
                'contents' => fopen($filePath, 'r'),
                'filename' => basename($filePath),
            ],
            ['name' => 'resource_type', 'contents' => $resourceType],
            ['name' => 'resource_id', 'contents' => $resourceId],
        ];
        return $this->http->postMultipart('/v1/files', $multipart);
    }

    public function downloadUrl(string $id): string
    {
        return $this->http->baseUrl() . '/v1/files/' . rawurlencode($id) . '/download';
    }

    /**
     * @param array<string, mixed> $data
     * @return array<string, mixed>
     */
    public function create(array $data): array
    {
        throw new \BadMethodCallException('Use Files::upload() to create files');
    }
}
