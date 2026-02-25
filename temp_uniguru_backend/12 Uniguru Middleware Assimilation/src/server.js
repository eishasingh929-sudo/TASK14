const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const bodyParser = require('body-parser');
const { handleAdmission } = require('./admission');
const logger = require('./logger');

const app = express();

// Security Headers
app.use(helmet());
app.use(cors());

// Parse JSON body with strict limit (middleware layer defense)
app.use(bodyParser.json({ limit: '1mb' }));

// Custom error handler for JSON parsing issues (e.g. malformed JSON)
app.use((err, req, res, next) => {
    if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
        const trace_id = require('crypto').randomUUID(); // trace ID for error
        logger.error(trace_id, 'Malformed JSON rejected', { ip: req.ip });
        return res.status(400).json({
            allowed: false,
            reason: "Malformed JSON payload",
            timestamp: new Date().toISOString(),
            trace_id
        });
    }

    if (err.type === 'entity.too.large' || err.status === 413) {
        const trace_id = require('crypto').randomUUID();
        logger.warn(trace_id, 'Payload too large rejected');
        return res.status(413).json({
            allowed: false,
            reason: "Payload exceeds size limit (1MB)",
            timestamp: new Date().toISOString(),
            trace_id
        });
    }

    next(err);
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'ok', service: 'uniguru-admission-layer' });
});

// Main Admission Endpoint
app.post('/admit', handleAdmission);

// Global Error Handler
app.use((err, req, res, next) => {
    logger.error('GLOBAL_ERROR', 'Unhandled exception', { error: err.message, stack: err.stack });
    res.status(500).json({
        allowed: false,
        reason: "Internal Server Error",
        timestamp: new Date().toISOString()
    });
});

module.exports = app;
