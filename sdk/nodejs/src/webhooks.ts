/** Webhook signature verification (X-CRM-Signature, HMAC-SHA256). */

import { createHmac, timingSafeEqual } from "crypto";

/** Compute the expected hex HMAC-SHA256 signature for a raw body. */
export function computeSignature(rawBody: string | Buffer, secret: string): string {
  return createHmac("sha256", secret).update(rawBody).digest("hex");
}

/**
 * Verify an `X-CRM-Signature` header against the raw request body.
 *
 * @param rawBody   the exact raw request body (string or Buffer) received.
 * @param signature the value of the `X-CRM-Signature` header.
 * @param secret    the webhook secret registered with the endpoint.
 */
export function verifyWebhookSignature(
  rawBody: string | Buffer,
  signature: string | undefined | null,
  secret: string
): boolean {
  if (!signature) return false;
  const expected = computeSignature(rawBody, secret);
  const a = Buffer.from(expected);
  const b = Buffer.from(signature.trim());
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}
