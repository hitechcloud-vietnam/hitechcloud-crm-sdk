<?php

declare(strict_types=1);

namespace HiTechCloud\CRM\Resources;

use HiTechCloud\CRM\HttpClient;

/**
 * Generic CRUD resource bound to a collection path (e.g. "contacts").
 */
class Resource
{
    /** @var array<int, string> */
    private const BULK = ['contacts', 'deals'];

    protected HttpClient $http;
    protected string $path;

    public function __construct(HttpClient $http, string $path)
    {
        $this->http = $http;
        $this->path = $path;
    }

    /**
     * GET /v1/{path} — list records with pagination and filters.
     *
     * @param array<string, mixed> $params
     * @return array<string, mixed>
     */
    public function list(array $params = []): array
    {
        return $this->http->get("/v1/{$this->path}", $params);
    }

    /**
     * GET /v1/{path}/{id} — fetch a single record.
     *
     * @return array<string, mixed>
     */
    public function get(string $id): array
    {
        return $this->http->get("/v1/{$this->path}/" . rawurlencode($id));
    }

    /**
     * POST /v1/{path} — create a record.
     *
     * @param array<string, mixed> $data
     * @return array<string, mixed>
     */
    public function create(array $data): array
    {
        return $this->http->post("/v1/{$this->path}", $data);
    }

    /**
     * PATCH /v1/{path}/{id} — partially update a record.
     *
     * @param array<string, mixed> $data
     * @return array<string, mixed>
     */
    public function update(string $id, array $data): array
    {
        return $this->http->patch("/v1/{$this->path}/" . rawurlencode($id), $data);
    }

    /**
     * DELETE /v1/{path}/{id} — delete a record.
     *
     * @return array<string, mixed>
     */
    public function delete(string $id): array
    {
        return $this->http->delete("/v1/{$this->path}/" . rawurlencode($id));
    }

    /**
     * POST /v1/{path}/bulk — up to 100 create/update/delete operations.
     *
     * @param array<int, array<string, mixed>> $operations
     * @return array<string, mixed>
     */
    public function bulk(array $operations): array
    {
        if (!in_array($this->path, self::BULK, true)) {
            throw new \InvalidArgumentException("Bulk operations are not supported for {$this->path}");
        }
        return $this->http->post("/v1/{$this->path}/bulk", ['operations' => $operations]);
    }
}
