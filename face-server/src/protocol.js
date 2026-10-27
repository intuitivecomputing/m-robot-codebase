import { expressions, moods, sequences } from "./core.js";

export const FACE_CONTROLS = [
  "wake",
  "sleep",
  "reset",
  "stop_sequence",
  "blink_start",
  "blink_stop",
  "breathe_start",
  "breathe_stop",
  "talk_start",
  "talk_stop",
  "heartbeat_start",
  "heartbeat_stop",
];

export const REACTIVE_KEYS = ["mouthSy", "eyeSy", "eyeTx", "eyeTy"];

export function getCapabilities() {
  return {
    expressions: Object.keys(expressions),
    moods: Object.keys(moods),
    sequences: Object.keys(sequences),
    controls: [...FACE_CONTROLS],
    reactive: [...REACTIVE_KEYS],
    intensities: ["low", "high"],
  };
}

function assertString(value, label) {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`${label} must be a non-empty string`);
  }
}

function assertKnown(name, allowed, label) {
  if (!allowed.includes(name)) {
    throw new Error(`Unknown ${label} "${name}"`);
  }
}

export function validateFaceCommand(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    throw new Error("Face command must be an object");
  }

  const allowedKeys = ["mood", "emotion", "intensity", "sequence", "control", "reactive"];
  for (const key of Object.keys(payload)) {
    if (!allowedKeys.includes(key)) {
      throw new Error(`Unknown command field "${key}"`);
    }
  }

  const command = {};

  if ("mood" in payload) {
    assertString(payload.mood, "mood");
    assertKnown(payload.mood, Object.keys(moods), "mood");
    command.mood = payload.mood;
  }

  if ("emotion" in payload) {
    assertString(payload.emotion, "emotion");
    assertKnown(payload.emotion, Object.keys(expressions), "expression");
    command.emotion = payload.emotion;
  }

  if ("intensity" in payload) {
    assertString(payload.intensity, "intensity");
    assertKnown(payload.intensity, ["low", "high"], "intensity");
    command.intensity = payload.intensity;
  }

  if ("sequence" in payload) {
    assertString(payload.sequence, "sequence");
    assertKnown(payload.sequence, Object.keys(sequences), "sequence");
    command.sequence = payload.sequence;
  }

  if ("control" in payload) {
    assertString(payload.control, "control");
    assertKnown(payload.control, FACE_CONTROLS, "control");
    command.control = payload.control;
  }

  if ("reactive" in payload) {
    if (!payload.reactive || typeof payload.reactive !== "object" || Array.isArray(payload.reactive)) {
      throw new Error("reactive must be an object");
    }
    const deltas = {};
    for (const [key, value] of Object.entries(payload.reactive)) {
      if (!REACTIVE_KEYS.includes(key)) {
        throw new Error(`Unknown reactive key "${key}"`);
      }
      if (typeof value !== "number" || !Number.isFinite(value)) {
        throw new Error(`Reactive value for "${key}" must be a finite number`);
      }
      deltas[key] = value;
    }
    command.reactive = deltas;
  }

  if (Object.keys(command).length === 0) {
    throw new Error("Face command must include at least one supported field");
  }

  if (command.intensity && !command.emotion) {
    throw new Error("intensity requires emotion");
  }

  return command;
}

export function applyFaceCommand(face, payload) {
  const command = validateFaceCommand(payload);

  if (command.mood) {
    face.setMood(command.mood);
  }
  if (command.sequence) {
    face.runSequence(command.sequence);
  }
  if (command.control) {
    const controls = {
      wake: () => face.wake?.() ?? face.wakeUp?.(),
      sleep: () => face.sleep?.() ?? face.goToSleep?.(),
      reset: () => face.reset(),
      stop_sequence: () => face.stopSequence(),
      blink_start: () => face.startBlinking(),
      blink_stop: () => face.stopBlinking(),
      breathe_start: () => face.startBreathing(),
      breathe_stop: () => face.stopBreathing(),
      talk_start: () => face.startTalking(),
      talk_stop: () => face.stopTalking(),
      heartbeat_start: () => face.startHeartbeat(),
      heartbeat_stop: () => face.stopHeartbeat(),
    };
    controls[command.control]();
  }
  if (command.emotion) {
    face.setExpression(command.emotion, command.intensity || "high");
  }
  if (command.reactive) {
    face.setReactive(command.reactive);
  }

  return command;
}

export function translateLegacyExpression(expression) {
  assertString(expression, "expression");
  const [name, intensity] = expression.split(":");
  const legacyControls = {
    breathing: { control: "breathe_start" },
    talking: { control: "talk_start" },
    blinking: { control: "blink_start" },
    stopBlinking: { control: "blink_stop" },
    stopTalking: { control: "talk_stop" },
    reset: { control: "reset" },
    wakeup: { control: "wake" },
    sleep: { control: "sleep" },
  };

  if (legacyControls[name]) {
    return legacyControls[name];
  }

  if (Object.keys(expressions).includes(name)) {
    return validateFaceCommand({ emotion: name, intensity: intensity || "high" });
  }

  throw new Error(`Unknown legacy expression "${expression}"`);
}
