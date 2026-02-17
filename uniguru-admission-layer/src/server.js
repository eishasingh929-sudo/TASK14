const express = require('express');
const admitRouter = require('./routes/admit.route');
const logger = require('./utils/logger');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Health check endpoint
app.get('/', (req, res) => {
    res.json({ status: 'UP', service: 'uniguru-admission-layer' });
});

// Admission endpoint
app.use('/admit', admitRouter);

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled internal error', { error: err.message, stack: err.stack });
    res.status(500).json({ error: 'Internal Server Error' });
});

if (require.main === module) {
    app.listen(PORT, () => {
        logger.info(`Admission layer server running on http://localhost:${PORT}`);
    });
}

module.exports = app;
