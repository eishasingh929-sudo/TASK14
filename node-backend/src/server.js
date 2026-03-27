import dotenv from "dotenv";

import app from "./app.js";

dotenv.config();

const PORT = Number(process.env.PORT || process.env.NODE_BACKEND_PORT || 3000);

app.listen(PORT, () => {
  console.log(`Node backend listening on ${PORT}`);
});
