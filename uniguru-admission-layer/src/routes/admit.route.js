const express = require('express');
const router = express.Router();
const { runAdmissionRules } = require('../engine/ruleEngine');
const { forwardToUniGuru } = require('../forwarder/uniguruClient');
const { generateTraceId } = require('../utils/trace');
const logger = require('../utils/logger');

router.post('/', async (req, res) => {
    const traceId = generateTraceId();
    const body = req.body;

    logger.info('Incoming request received', { trace_id: traceId, path: '/admit' });

    // 1. Run admission rules
    const decision = runAdmissionRules(body);
    logger.info('Admission decision made', { trace_id: traceId, allowed: decision.allowed, reason: decision.reason });

    if (!decision.allowed) {
        return res.status(400).json({
            ...decision,
            trace_id: traceId
        });
    }

    // 2. Forward to UniGuru
    try {
        const uniGuruResponse = await forwardToUniGuru(body, traceId);
        return res.status(200).json({
            data: uniGuruResponse,
            trace_id: traceId
        });
    } catch (error) {
        return res.status(error.status || 502).json({
            error: error.message,
            trace_id: traceId
        });
    }
});

module.exports = router;
