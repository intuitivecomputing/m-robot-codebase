import express from "express";
import http from "http";
import { Server as SocketIOServer } from "socket.io";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";

import { getCapabilities, translateLegacyExpression, validateFaceCommand } from "./src/protocol.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const server = http.createServer(app);

app.use(express.json({ limit: "16kb" }));
app.use(cors());
app.use("/sdk", express.static(path.join(__dirname, "src"), { extensions: ["js"] }));
const io = new SocketIOServer(server, {
  cors: { origin: "*", methods: ["GET", "POST"] },
});

io.on("connection", (socket) => {
  console.log(`Client connected: ${socket.id}`);
  socket.on("disconnect", () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

app.get("/", (_req, res) => {
  res.sendFile(path.join(__dirname, "face.html"));
});

app.get("/face.html", (_req, res) => {
  res.sendFile(path.join(__dirname, "face.html"));
});

app.get("/face-testing.html", (_req, res) => {
  res.sendFile(path.join(__dirname, "face-testing.html"));
});

app.get("/face.css", (_req, res) => {
  res.sendFile(path.join(__dirname, "face.css"));
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.get("/api/capabilities", (_req, res) => {
  res.json(getCapabilities());
});

app.post("/face", (req, res) => {
  try {
    const command = validateFaceCommand(req.body);
    io.emit("face-state", command);
    res.json({ status: "ok", command });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.post("/express", (req, res) => {
  try {
    const command = translateLegacyExpression(req.body?.expression);
    io.emit("face-state", command);
    io.emit("change-expression", req.body.expression);
    res.json({ status: "ok", command });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

const PORT = Number(process.env.PORT || 3001);
server.listen(PORT, () => {
  console.log(`Face server running on http://localhost:${PORT}`);
});
