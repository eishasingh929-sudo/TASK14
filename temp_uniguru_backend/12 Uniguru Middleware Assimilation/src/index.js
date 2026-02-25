const app = require('./server');
const config = require('./config');
const logger = require('./logger');

const PORT = config.PORT || 3000;

app.listen(PORT, () => {
    logger.info('SERVER', `UniGuru Admission Middleware listening on port ${PORT}`, {
        target: config.TARGET_URL
    });
});
