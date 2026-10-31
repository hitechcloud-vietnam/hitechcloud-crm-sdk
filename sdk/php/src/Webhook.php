<?php

declare(strict_types=1);

namespace HiTechCloud\CRM;

/**
 * Webhook signature verification (X-CRM-Signature, HMAC-SHA256).
 */
class Webhook
{
    /**
     * Compute the expected hex HMAC-SHA256 signature for a raw body.
     */
    public static function computeSignature(string $rawBody, string $secret): string
    {
        return hash_hmac('sha256', $rawBody, $secret);
    }

    /**
     * Verify an X-CRM-Signature header against the raw request body
     * using a constant-time comparison.
     *
     * @param string $rawBody   the exact raw request body received.
     * @param string $signature the value of the X-CRM-Signature header.
     * @param string $secret    the webhook secret registered with the endpoint.
     */
    public static function verifySignature(string $rawBody, string $signature, string $secret): bool
    {
        if ($signature === '') {
            return false;
        }
        $expected = self::computeSignature($rawBody, $secret);
        return hash_equals($expected, trim($signature));
    }
}
