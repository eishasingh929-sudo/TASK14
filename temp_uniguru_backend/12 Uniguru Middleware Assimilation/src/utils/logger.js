const fs = require("fs");

function logDecision(traceId, decision) {
    const log = `[${new Date().toISOString()}] ${traceId} ${JSON.stringify(decision)}\n`;
    fs.appendFileSync("admission.log", log);
}

module.exports = { logDecision };
