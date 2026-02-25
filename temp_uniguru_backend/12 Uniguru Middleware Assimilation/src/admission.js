const { validateRequest, generateTraceId } = require('./ruleEngine');
const { logDecision } = require('./utils/logger');
const { forwardRequest } = require('./forward/forwardRequest');
// Note provided logger also requires traceId.

/**
 * Main admission handler.
 * Validates request and forwards if allowed.
 */
async function handleAdmission(req, res) {
    // 1. Get Payload Size
    const contentLength = req.get('content-length') || 0;
    const payloadSize = parseInt(contentLength);

    // 2. Run Pure Rule Engine
    const validationResult = validateRequest(req.body, payloadSize);

    const { allowed, reason, timestamp, trace_id } = validationResult;

    // 3. Log Decision
    logDecision(trace_id, validationResult);

    // 4. Handle Rejection
    if (!allowed) {
        return res.status(400).json(validationResult);
    }

    // 5. Forward Request if Allowed
    try {
        const upstreamResponse = await forwardRequest(req.body);

        // Return upstream response directly
        // Assuming upstream returns JSON
        return res.status(200).json(upstreamResponse);

    } catch (error) {
        // Log forwarding failure? Requirement says "Log decision... If rejected -> return decision JSON... If allowed -> forward".
        // It doesn't explicitly say log success/failure of forwarding in the *same* log function, but implied robustness.
        // I already logged the "Allowed" decision.

        // Return 502 for upstream error
        return res.status(502).json({
            allowed: true,
            forwarded: false,
            error: 'Upstream service unavailable or error',
            details: error.message,
            trace_id,
            timestamp
        });
    }
}

module.exports = { handleAdmission };
