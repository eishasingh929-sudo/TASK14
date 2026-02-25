require('dotenv').config();

const config = {
    PORT: process.env.PORT || 3000,
    TARGET_URL: process.env.TARGET_URL || 'http://localhost:8080/admit', // Default local mock
    MAX_BODY_SIZE: '1mb',
    NODE_ENV: process.env.NODE_ENV || 'development'
};

module.exports = config;
