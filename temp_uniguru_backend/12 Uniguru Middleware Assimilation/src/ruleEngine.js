const crypto = require('crypto');

/**
 * Deterministic validation set.
 * Returns structured decision object.
 */

const SAFE_LIMIT_BYTES = 1024 * 1024; // 1MB explicitly
const SAFE_TOKENS_REGEX = /(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|EXEC|DECLARE)\b)|(<script>|<\/script>)|(javascript:)|(onerror=)|(onload=)/i;

/**
 * Generates a trace ID for request tracking.
 */
function generateTraceId() {
    return crypto.randomUUID();
}

/**
 * Validates the incoming request payload.
 * @param {object} body - Parsed JSON body
 * @param {number} payloadSize - Payload size in bytes
 * @returns {object} - { allowed: boolean, reason: string|null, timestamp: string, trace_id: string }
 */
function validateRequest(body, payloadSize) {
    const trace_id = generateTraceId();
    const timestamp = new Date().toISOString();

    // 1. Reject empty message
    if (!body || Object.keys(body).length === 0) {
        return {
            allowed: false,
            reason: "Empty message payload",
            timestamp,
            trace_id
        };
    }

    // 2. Reject malformed request (missing required 'message' property or not a valid object)
    if (!body.message || typeof body.message !== 'string') {
        return {
            allowed: false,
            reason: "Malformed request: missing 'message' string property",
            timestamp,
            trace_id
        };
    }

    // 3. Reject oversized payload
    // The test expects reject for 2MB.
    if (payloadSize > SAFE_LIMIT_BYTES) {
        return {
            allowed: false,
            reason: "Payload exceeds size limit (1MB)",
            timestamp,
            trace_id
        };
    }

    // Also check if body size is somehow large if content-length wasn't reliable (though express limit catches this usually)
    // But we must support `payloadSize` argument as per requirement.

    // 4. Reject obvious unsafe tokens
    const stringifiedBody = JSON.stringify(body);
    if (SAFE_TOKENS_REGEX.test(stringifiedBody)) {
        return {
            allowed: false,
            reason: "Unsafe tokens detected in payload", // Matches regex check in tests? verify later
            timestamp,
            trace_id
        };
    }

    return {
        allowed: true,
        reason: null,
        timestamp,
        trace_id
    };
}

module.exports = { validateRequest, generateTraceId };
