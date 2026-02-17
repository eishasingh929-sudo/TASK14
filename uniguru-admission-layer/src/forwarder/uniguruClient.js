const axios = require('axios');
const logger = require('../utils/logger');

const UNIGURU_URL = process.env.UNIGURU_URL || 'http://localhost:8080/chat';

/**
 * Forwards the allowed request to the legacy UniGuru server.
 * @param {Object} payload - The request body
 * @param {string} traceId - The trace ID for logging
 * @returns {Promise<Object>} - The response from UniGuru
 */
async function forwardToUniGuru(payload, traceId) {
    try {
        logger.info('Attempting to forward request to UniGuru', { trace_id: traceId, url: UNIGURU_URL });

        const response = await axios.post(UNIGURU_URL, payload, {
            timeout: 5000,
            headers: {
                'Content-Type': 'application/json',
                'X-Trace-Id': traceId
            }
        });

        logger.info('Successfully received response from UniGuru', { trace_id: traceId, status: response.status });
        return response.data;
    } catch (error) {
        logger.error('Failed to forward request to UniGuru', {
            trace_id: traceId,
            error: error.message,
            code: error.code
        });

        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            throw {
                status: error.response.status,
                message: 'UniGuru server returned an error',
                data: error.response.data
            };
        } else if (error.request) {
            // The request was made but no response was received
            throw {
                status: 502,
                message: 'No response from UniGuru server (Gateway Error)'
            };
        } else {
            // Something happened in setting up the request that triggered an Error
            throw {
                status: 500,
                message: error.message
            };
        }
    }
}

module.exports = { forwardToUniGuru };
