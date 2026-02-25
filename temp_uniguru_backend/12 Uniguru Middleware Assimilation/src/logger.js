/**
 * Simple logger utility for UniGuru Admission Middleware.
 * Writes to console for local demo, can be extended to file/syslog.
 */
const logger = {
    info: (traceId, message, meta = {}) => {
        console.log(JSON.stringify({
            level: 'INFO',
            trace_id: traceId,
            timestamp: new Date().toISOString(),
            message,
            ...meta
        }));
    },
    warn: (traceId, message, meta = {}) => {
        console.log(JSON.stringify({
            level: 'WARN',
            trace_id: traceId,
            timestamp: new Date().toISOString(),
            message,
            ...meta
        }));
    },
    error: (traceId, message, meta = {}) => {
        console.error(JSON.stringify({
            level: 'ERROR',
            trace_id: traceId,
            timestamp: new Date().toISOString(),
            message,
            ...meta
        }));
    }
};

module.exports = logger;
