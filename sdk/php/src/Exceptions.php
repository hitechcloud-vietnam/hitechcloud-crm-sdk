<?php

declare(strict_types=1);

namespace HiTechCloud\CRM;

/**
 * Base exception for the HiTechCloud CRM SDK.
 */
class CRMException extends \Exception
{
    public ?int $statusCode;
    public ?string $errorCode;
    /** @var array<string, mixed> */
    public array $errors;

    /**
     * @param array<string, mixed> $errors
     */
    public function __construct(string $message, ?int $statusCode = null, ?string $errorCode = null, array $errors = [])
    {
        parent::__construct($message);
        $this->statusCode = $statusCode;
        $this->errorCode = $errorCode;
        $this->errors = $errors;
    }
}

/** Raised when the access token is missing or invalid (401). */
class AuthenticationException extends CRMException
{
}

/** Raised when the token lacks the required scope (403). */
class AuthorizationException extends CRMException
{
}

/** Raised when a resource is not found (404). */
class NotFoundException extends CRMException
{
}

/** Raised on a duplicate resource conflict (409). */
class ConflictException extends CRMException
{
}

/** Raised when request validation fails (400/422). */
class ValidationException extends CRMException
{
}

/** Raised when the rate limit is exceeded (429). */
class RateLimitException extends CRMException
{
    public int $retryAfter;

    /**
     * @param array<string, mixed> $errors
     */
    public function __construct(string $message, int $retryAfter = 60, ?string $errorCode = null, array $errors = [])
    {
        parent::__construct($message, 429, $errorCode, $errors);
        $this->retryAfter = $retryAfter;
    }
}

/** Raised when the server returns a 5xx error. */
class ServerException extends CRMException
{
}
