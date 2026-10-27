/**
 * @fileoverview
 * Setup and management of the Express server with Socket.IO for real-time interaction.
 * This file configures the HTTP and WebSocket server, handling routes to manage
 * facial expression changes through a web interface.
 *
 * @requires express: Framework for handling HTTP server functionalities.
 * @requires http: Module to create HTTP server.
 * @requires socket.io: Enables real-time, bidirectional communication.
 * @requires cors: Middleware to enable CORS (Cross-Origin Resource Sharing).
 */

const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const cors = require("cors");
const { spawn } = require("child_process");

// Initialize express application
const app = express();
const server = http.createServer(app);

// Middleware to parse JSON and enable CORS
app.use(express.json());
app.use(cors());

// Serve static files from current directory
app.use(express.static(__dirname));

/**
 * WebSocket configuration allowing connections from any origin and handling
 * GET and POST methods.
 */
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

/**
 * Handles WebSocket connections, logging when clients connect and disconnect.
 */
io.on("connection", (socket) => {
  console.log("New client connected");
  socket.on("disconnect", () => {
    console.log("Client disconnected");
  });
});

/**
 * Route to change facial expressions. Accepts expression data via POST request
 * and broadcasts it to all connected clients.
 *
 * @route POST /express
 * @param req - HTTP request object containing expression data.
 * @param res - HTTP response object for sending back status.
 */
app.post("/express", (req, res) => {
  const requestData = req.body;
  const expression = requestData.expression;
  console.log("sending: ", expression);
  io.emit("change-expression", expression);
  res.send({ status: "expression changed" });
});

/**
 * Route to execute a function received as a string. Evaluates and executes the function,
 * emitting results to clients. This route is used for dynamic expression adjustments.
 *
 * @route POST /exec-func
 * @param req - HTTP request object containing the function as a string.
 * @param res - HTTP response object for sending back execution status.
 */
app.post("/exec-func", async (req, res) => {
  const programData = req.body;
  console.log("executing: ", programData);
  io.emit("execute-expression", programData);
  res.send({ status: "completed" });
});

// Server listening on port 3001
const PORT = 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

function isLoopbackAddress(remoteAddress) {
  if (!remoteAddress) return false;
  return (
    remoteAddress === "127.0.0.1" ||
    remoteAddress === "::1" ||
    remoteAddress === "::ffff:127.0.0.1"
  );
}

function runCommand(command, args, { timeoutMs = 15_000 } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    const timeout = setTimeout(() => {
      child.kill("SIGKILL");
      reject(new Error(`${command} timed out after ${timeoutMs}ms`));
    }, timeoutMs);

    child.stdout.on("data", (chunk) => (stdout += chunk.toString()));
    child.stderr.on("data", (chunk) => (stderr += chunk.toString()));

    child.on("error", (err) => {
      clearTimeout(timeout);
      reject(err);
    });

    child.on("close", (code) => {
      clearTimeout(timeout);
      if (code === 0) return resolve({ stdout, stderr });
      reject(new Error(`${command} exited with code ${code}: ${stderr || stdout}`));
    });
  });
}

let shuttingDown = false;

async function requestHostPoweroff() {
  // This requires a sudoers rule that allows ONLY this command without a password.
  return runCommand("sudo", ["-n", "/usr/bin/systemctl", "start", "robot-poweroff.service"], {
    timeoutMs: 10_000,
  });
}

function checkShutdownAuth(req) {
  const requiredToken = process.env.SHUTDOWN_TOKEN;
  if (!requiredToken) return true;

  const provided =
    req.get("x-shutdown-token") ||
    (typeof req.query?.token === "string" ? req.query.token : "") ||
    "";

  return provided && provided === requiredToken;
}

async function shutdownHandler(req, res) {
  const remoteAddress = req.socket?.remoteAddress;
  if (!isLoopbackAddress(remoteAddress)) {
    return res.status(403).send({ error: "shutdown is only allowed from localhost" });
  }

  if (!checkShutdownAuth(req)) {
    return res.status(401).send({ error: "invalid shutdown token" });
  }

  if (shuttingDown) {
    return res.status(202).send({ status: "shutting down" });
  }
  shuttingDown = true;

  res.status(202).send({ status: "shutting down" });
  console.log("Shutdown requested...", { remoteAddress });

  // Let the response flush.
  setTimeout(async () => {
    try {
      await requestHostPoweroff();
    } catch (err) {
      shuttingDown = false;
      console.error(
        "Failed to start robot-poweroff.service (check sudoers/systemd install):",
        err.message
      );
    }
  }, 200);
}

/**
 * Production shutdown trigger.
 * This endpoint does NOT power off directly; it starts a root-owned systemd oneshot unit.
 *
 * Preferred: POST /shutdown (optional header: x-shutdown-token)
 * Back-compat: GET /shutdown (same behavior)
 */
app.post("/shutdown", shutdownHandler);
app.get("/shutdown", shutdownHandler);
