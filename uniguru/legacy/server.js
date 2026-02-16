const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Simulated Legacy RAG Endpoint
app.post('/chat', (req, res) => {
    const { message } = req.body;
    console.log(`[LEGACY RAG] Processing message: ${message}`);
    
    // Simulate RAG Logic
    res.json({
        answer: `Legacy Generative response for: "${message}"`,
        source: "VectorDB_v1",
        confidence: 0.95
    });
});

const PORT = 8080;
app.listen(PORT, () => {
    console.log(`Legacy UniGuru RAG Service running on port ${PORT}`);
});
