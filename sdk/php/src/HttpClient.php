<?php

declare(strict_types=1);

namespace HiTechCloud\CRM;

use GuzzleHttp\Client as GuzzleClient;
use GuzzleHttp\Exception\ConnectException;
use GuzzleHttp\Exception\RequestException;
use Psr\Http\Message\ResponseInterface;

/**
 * Low-level HTTP transport with OAuth2 client_credentials token management.
 */
class HttpClient
{
    public const VERSION = '1.0.0';
    private const TOKEN_PATH = '/v1/oauth/token';

    private GuzzleClient $client;
    private string $baseUrl;
    private int $maxRetries;
    private ?string $clientId;
    private ?string $clientSecret;
    private ?string $scope;
    private ?string $token;
    private float $tokenExpiry = 0.0;

    public function __construct(
        string $baseUrl,
        ?string $clientId = null,
        ?string $clientSecret = null,
        ?string $scope = null,
        ?string $token = null,
        int $timeout = 30,
        int $maxRetries = 3
    ) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->clientId = $clientId;
        $this->clientSecret = $clientSecret;
        $this->scope = $scope;
        $this->token = $token;
        $this->tokenExpiry = $token !== null ? INF : 0.0;
        $this->maxRetries = $maxRetries;
        $this->client = new GuzzleClient([
            'base_uri' => $this->baseUrl . '/',
            'timeout' => $timeout,
            'http_errors' => false,
            'headers' => [
                'Accept' => 'application/json',
                'User-Agent' => 'hitechcloud-crm-php/' . self::VERSION,
            ],
        ]);
    }

    public function baseUrl(): string
    {
        return $this->baseUrl;
    }

    public function setToken(string $token): void
    {
        $this->token = $token;
        $this->tokenExpiry = INF;
    }

    /**
     * @return array<string, mixed>
     */
    public function fetchToken(): array
    {
        if (!$this->clientId || !$this->clientSecret) {
            throw new CRMException('No client credentials configured');
        }
        $payload = [
            'grant_type' => 'client_credentials',
            'client_id' => $this->clientId,
            'client_secret' => $this->clientSecret,
        ];
        if ($this->scope) {
            $payload['scope'] = $this->scope;
        }
        $response = $this->client->request('POST', ltrim(self::TOKEN_PATH, '/'), ['json' => $payload]);
        $body = $this->decode($response);
        if ($response->getStatusCode() >= 400) {
            $this->raiseError($response, $body);
        }
        $data = $body['data'] ?? [];
        $this->token = $data['access_token'] ?? null;
        $expiresIn = (int) ($data['expires_in'] ?? 3600);
        $this->tokenExpiry = microtime(true) + max($expiresIn - 60, 30);
        return $data;
    }

    private function ensureToken(): void
    {
        if ($this->token !== null && microtime(true) < $this->tokenExpiry) {
            return;
        }
        if (!$this->clientId || !$this->clientSecret) {
            if ($this->token !== null) {
                return;
            }
            throw new CRMException('No access token and no client credentials configured');
        }
        $this->fetchToken();
    }

    /**
     * @param array<string, mixed> $options
     * @return array<string, mixed>
     */
    public function request(string $method, string $path, array $options = [], bool $retryAuth = true): array
    {
        $this->ensureToken();
        $uri = ltrim($path, '/');

        for ($attempt = 0; $attempt <= $this->maxRetries; $attempt++) {
            $options['headers'] = ($options['headers'] ?? []) + [
                'Authorization' => 'Bearer ' . $this->token,
            ];

            try {
                $response = $this->client->request($method, $uri, $options);
            } catch (ConnectException $e) {
                if ($attempt < $this->maxRetries) {
                    sleep(2 ** $attempt);
                    continue;
                }
                throw new CRMException('Request failed: ' . $e->getMessage());
            } catch (RequestException $e) {
                throw new CRMException('Request failed: ' . $e->getMessage());
            }

            $status = $response->getStatusCode();

            if ($status === 401 && $retryAuth && $this->clientId) {
                $this->fetchToken();
                $retryAuth = false;
                $attempt--;
                continue;
            }

            if ($status === 429) {
                $retryAfter = (int) ($response->getHeaderLine('Retry-After') ?: 60);
                if ($attempt < $this->maxRetries) {
                    sleep($retryAfter);
                    continue;
                }
                $body = $this->decode($response);
                throw new RateLimitException($body['message'] ?? 'Rate limit exceeded', $retryAfter, $body['code'] ?? null, $body['errors'] ?? []);
            }

            if ($status >= 500 && $attempt < $this->maxRetries) {
                sleep(2 ** $attempt);
                continue;
            }

            $body = $this->decode($response);
            if ($status >= 400) {
                $this->raiseError($response, $body);
            }
            return $body;
        }

        throw new CRMException('Request failed after retries');
    }

    /**
     * @return array<string, mixed>
     */
    private function decode(ResponseInterface $response): array
    {
        $raw = (string) $response->getBody();
        if ($raw === '') {
            return [];
        }
        $decoded = json_decode($raw, true);
        return is_array($decoded) ? $decoded : ['message' => substr($raw, 0, 200)];
    }

    /**
     * @param array<string, mixed> $body
     */
    private function raiseError(ResponseInterface $response, array $body): void
    {
        $status = $response->getStatusCode();
        $message = $body['message'] ?? "HTTP {$status}";
        $code = $body['code'] ?? null;
        $errors = $body['errors'] ?? [];

        switch ($status) {
            case 400:
            case 422:
                throw new ValidationException($message, $status, $code, $errors);
            case 401:
                throw new AuthenticationException($message, 401, $code, $errors);
            case 403:
                throw new AuthorizationException($message, 403, $code, $errors);
            case 404:
                throw new NotFoundException($message, 404, $code, $errors);
            case 409:
                throw new ConflictException($message, 409, $code, $errors);
            case 429:
                $retryAfter = (int) ($response->getHeaderLine('Retry-After') ?: 60);
                throw new RateLimitException($message, $retryAfter, $code, $errors);
            default:
                if ($status >= 500) {
                    throw new ServerException($message, $status, $code, $errors);
                }
                throw new CRMException($message, $status, $code, $errors);
        }
    }

    /**
     * @param array<string, mixed> $params
     * @return array<string, mixed>
     */
    public function get(string $path, array $params = []): array
    {
        return $this->request('GET', $path, $params ? ['query' => $params] : []);
    }

    /**
     * @param array<string, mixed> $data
     * @return array<string, mixed>
     */
    public function post(string $path, array $data = []): array
    {
        return $this->request('POST', $path, ['json' => $data]);
    }

    /**
     * @param array<int, array<string, mixed>> $multipart
     * @return array<string, mixed>
     */
    public function postMultipart(string $path, array $multipart): array
    {
        return $this->request('POST', $path, ['multipart' => $multipart]);
    }

    /**
     * @param array<string, mixed> $data
     * @return array<string, mixed>
     */
    public function patch(string $path, array $data = []): array
    {
        return $this->request('PATCH', $path, ['json' => $data]);
    }

    /**
     * @return array<string, mixed>
     */
    public function delete(string $path): array
    {
        return $this->request('DELETE', $path);
    }
}
