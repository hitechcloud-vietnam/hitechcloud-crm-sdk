package vn.hitechcloud.crm;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** Webhook signature verification (X-CRM-Signature, HMAC-SHA256). */
public final class Webhook {
    private Webhook() {
    }

    /** Compute the expected hex HMAC-SHA256 signature for a raw body. */
    public static String computeSignature(byte[] rawBody, String secret) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            byte[] digest = mac.doFinal(rawBody);
            StringBuilder sb = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                sb.append(Character.forDigit((b >> 4) & 0xF, 16));
                sb.append(Character.forDigit(b & 0xF, 16));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new IllegalStateException("HMAC-SHA256 unavailable", e);
        }
    }

    public static String computeSignature(String rawBody, String secret) {
        return computeSignature(rawBody.getBytes(StandardCharsets.UTF_8), secret);
    }

    /**
     * Verify an X-CRM-Signature header against the raw request body using a
     * constant-time comparison.
     */
    public static boolean verifySignature(byte[] rawBody, String signature, String secret) {
        if (signature == null || signature.isEmpty()) {
            return false;
        }
        String expected = computeSignature(rawBody, secret);
        return MessageDigest.isEqual(
                expected.getBytes(StandardCharsets.UTF_8),
                signature.trim().getBytes(StandardCharsets.UTF_8));
    }

    public static boolean verifySignature(String rawBody, String signature, String secret) {
        return verifySignature(rawBody.getBytes(StandardCharsets.UTF_8), signature, secret);
    }
}
