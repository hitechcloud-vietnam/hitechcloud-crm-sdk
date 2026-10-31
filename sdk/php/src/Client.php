<?php

declare(strict_types=1);

namespace HiTechCloud\CRM;

use HiTechCloud\CRM\Resources\Resource;
use HiTechCloud\CRM\Resources\Files;
use HiTechCloud\CRM\Resources\Webhooks;
use HiTechCloud\CRM\Resources\Imports;
use HiTechCloud\CRM\Resources\Exports;

/**
 * HiTechCloud CRM client.
 *
 * Example:
 *   $crm = new \HiTechCloud\CRM\Client([
 *       'client_id' => 'YOUR_CLIENT_ID',
 *       'client_secret' => 'YOUR_CLIENT_SECRET',
 *       'scope' => 'contacts:read contacts:write',
 *   ]);
 *   $customers = $crm->contacts()->list(['lifecycle_stage' => 'customer']);
 */
class Client
{
    public const PRODUCTION_URL = 'https://crm-gateways.hitechcloud.vn';
    public const SANDBOX_URL = 'https://crm-gateways-sandbox.hitechcloud.vn';

    /** @var array<int, string> accessor => collection path */
    private const RESOURCES = [
        'contacts' => 'contacts',
        'companies' => 'companies',
        'deals' => 'deals',
        'pipelines' => 'pipelines',
        'stages' => 'stages',
        'activities' => 'activities',
        'tasks' => 'tasks',
        'calls' => 'calls',
        'emails' => 'emails',
        'meetings' => 'meetings',
        'notes' => 'notes',
        'tags' => 'tags',
        'segments' => 'segments',
        'customFields' => 'custom-fields',
        'leadSources' => 'lead-sources',
        'products' => 'products',
        'quotes' => 'quotes',
        'users' => 'users',
        'teams' => 'teams',
    ];

    private HttpClient $http;
    /** @var array<string, Resource> */
    private array $cache = [];
    private Files $files;
    private Webhooks $webhooks;
    private Imports $imports;
    private Exports $exports;

    /**
     * @param array<string, mixed> $config
     *   Keys: client_id, client_secret, scope, token, base_url, sandbox, timeout, max_retries
     */
    public function __construct(array $config = [])
    {
        $baseUrl = $config['base_url'] ?? self::PRODUCTION_URL;
        if (!empty($config['sandbox'])) {
            $baseUrl = self::SANDBOX_URL;
        }
        $this->http = new HttpClient(
            $baseUrl,
            $config['client_id'] ?? null,
            $config['client_secret'] ?? null,
            $config['scope'] ?? null,
            $config['token'] ?? null,
            (int) ($config['timeout'] ?? 30),
            (int) ($config['max_retries'] ?? 3)
        );
        $this->files = new Files($this->http);
        $this->webhooks = new Webhooks($this->http);
        $this->imports = new Imports($this->http);
        $this->exports = new Exports($this->http);
    }

    private function resource(string $accessor): Resource
    {
        if (!isset($this->cache[$accessor])) {
            $this->cache[$accessor] = new Resource($this->http, self::RESOURCES[$accessor]);
        }
        return $this->cache[$accessor];
    }

    public function contacts(): Resource
    {
        return $this->resource('contacts');
    }

    public function companies(): Resource
    {
        return $this->resource('companies');
    }

    public function deals(): Resource
    {
        return $this->resource('deals');
    }

    public function pipelines(): Resource
    {
        return $this->resource('pipelines');
    }

    public function stages(): Resource
    {
        return $this->resource('stages');
    }

    public function activities(): Resource
    {
        return $this->resource('activities');
    }

    public function tasks(): Resource
    {
        return $this->resource('tasks');
    }

    public function calls(): Resource
    {
        return $this->resource('calls');
    }

    public function emails(): Resource
    {
        return $this->resource('emails');
    }

    public function meetings(): Resource
    {
        return $this->resource('meetings');
    }

    public function notes(): Resource
    {
        return $this->resource('notes');
    }

    public function tags(): Resource
    {
        return $this->resource('tags');
    }

    public function segments(): Resource
    {
        return $this->resource('segments');
    }

    public function customFields(): Resource
    {
        return $this->resource('customFields');
    }

    public function leadSources(): Resource
    {
        return $this->resource('leadSources');
    }

    public function products(): Resource
    {
        return $this->resource('products');
    }

    public function quotes(): Resource
    {
        return $this->resource('quotes');
    }

    public function users(): Resource
    {
        return $this->resource('users');
    }

    public function teams(): Resource
    {
        return $this->resource('teams');
    }

    public function files(): Files
    {
        return $this->files;
    }

    public function webhooks(): Webhooks
    {
        return $this->webhooks;
    }

    public function imports(): Imports
    {
        return $this->imports;
    }

    public function exports(): Exports
    {
        return $this->exports;
    }

    /**
     * Force an OAuth2 token exchange and return the token data.
     *
     * @return array<string, mixed>
     */
    public function fetchToken(): array
    {
        return $this->http->fetchToken();
    }

    public function setToken(string $token): void
    {
        $this->http->setToken($token);
    }
}
