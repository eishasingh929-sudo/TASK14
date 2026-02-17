const { v4: uuidv4 } = require('uuid');

const generateTraceId = () => uuidv4();

module.exports = { generateTraceId };
