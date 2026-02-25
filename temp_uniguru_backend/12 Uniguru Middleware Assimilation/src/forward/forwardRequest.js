const axios = require("axios");

async function forwardRequest(body) {
    // Using http://localhost:5000/chat as requested
    try {
        const response = await axios.post(
            "http://localhost:5000/chat",
            body
        );
        return response.data;
    } catch (error) {
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            throw new Error(`Upstream error: ${error.response.status}`);
        } else if (error.request) {
            // The request was made but no response was received
            throw new Error('Upstream unreachable');
        } else {
            // Something happened in setting up the request that triggered an Error
            throw new Error(`Forwarding error: ${error.message}`);
        }
    }
}

module.exports = { forwardRequest };
