const express = require("express");
const app = express();

app.use(express.json());

app.post("/chat", (req, res) => {
    res.json({
        status: "UniGuru received request",
        received: req.body
    });
});

app.listen(5000, () =>
    console.log("Fake UniGuru running on port 5000")
);
