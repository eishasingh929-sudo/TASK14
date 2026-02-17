/**
 * Deterministic rule engine for UniGuru admission.
 * @param {Object} body - Incoming request body
 * @returns {Object} - Decision result { allowed, reason, timestamp }
 */
function runAdmissionRules(body) {
    const timestamp = new Date().toISOString();

    // 1. Check if body is a valid object
    if (!body || typeof body !== 'object' || Array.isArray(body)) {
        return {
            allowed: false,
            reason: 'Invalid JSON body: Expected a JSON object.',
            timestamp
        };
    }

    const { message, session_id, source } = body;

    // 2. Required fields
    if (message === undefined || session_id === undefined || source === undefined) {
        return {
            allowed: false,
            reason: 'Missing required fields: message, session_id, and source are required.',
            timestamp
        };
    }

    // 3. Message type and empty check
    if (typeof message !== 'string' || message.trim().length === 0) {
        return {
            allowed: false,
            reason: 'Invalid message: Message must be a non-empty string.',
            timestamp
        };
    }

    // 4. Message length check
    if (message.length > 1000) {
        return {
            allowed: false,
            reason: 'Message too long: Maximum allowed length is 1000 characters.',
            timestamp
        };
    }

    // 5. Unsafe tokens check
    const unsafeTokens = [
        'system prompt',
        'ignore instructions',
        'bypass',
        'override',
        '<script>',
        '</script>'
    ];

    const lowercaseMessage = message.toLowerCase();
    for (const token of unsafeTokens) {
        if (lowercaseMessage.includes(token)) {
            return {
                allowed: false,
                reason: `Unsafe content detected: Message contains forbidden token '${token}'.`,
                timestamp
            };
        }
    }

    // 6. Valid request
    return {
        allowed: true,
        reason: 'Admission successful',
        timestamp
    };
}

module.exports = { runAdmissionRules };
