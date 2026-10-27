import { FaceEngine, Spring, expressions, validateFaceCommand } from "../src/index.js";

let passed = 0;
let failed = 0;
let section = "";

function describe(name, fn) {
  section = name;
  console.log(`\n  ${name}`);
  fn();
}

function it(name, fn) {
  try {
    fn();
    console.log(`    \x1b[32m✓\x1b[0m ${name}`);
    passed += 1;
  } catch (error) {
    console.error(`    \x1b[31m✗\x1b[0m ${name}`);
    console.error(`      \x1b[33m${error.message}\x1b[0m`);
    failed += 1;
  }
}

function expect(actual) {
  return {
    toBe(expected) {
      if (actual !== expected) {
        throw new Error(`Expected ${expected}, got ${actual}`);
      }
    },
    toBeCloseTo(expected, tolerance = 0.05) {
      if (Math.abs(actual - expected) > tolerance) {
        throw new Error(`Expected ~${expected} (±${tolerance}), got ${actual}`);
      }
    },
    toBeGreaterThan(expected) {
      if (!(actual > expected)) {
        throw new Error(`Expected > ${expected}, got ${actual}`);
      }
    },
    toThrow(message) {
      let threw = false;
      try {
        actual();
      } catch (error) {
        threw = true;
        if (message && !String(error.message).includes(message)) {
          throw new Error(`Expected error containing "${message}", got "${error.message}"`);
        }
      }
      if (!threw) {
        throw new Error("Expected function to throw");
      }
    },
  };
}

function step(engineOrSpring, frames, dt = 1 / 60) {
  for (let index = 0; index < frames; index += 1) {
    engineOrSpring.update(dt);
  }
}

console.log("\nFace SDK Tests");
console.log("─".repeat(50));

describe("Spring", () => {
  it("converges toward its target", () => {
    const spring = new Spring({ stiffness: 120, damping: 18, initial: 0 });
    spring.setTarget(1);
    step(spring, 60);
    expect(spring.value).toBeCloseTo(1, 0.08);
  });

  it("preserves velocity when interrupted", () => {
    const spring = new Spring({ stiffness: 120, damping: 18, initial: 0 });
    spring.setTarget(1);
    step(spring, 15);
    const velocity = spring.velocity;
    spring.setTarget(0.5);
    expect(spring.velocity).toBeCloseTo(velocity, 0.001);
  });
});

describe("FaceEngine", () => {
  it("starts asleep", () => {
    const engine = new FaceEngine();
    const snapshot = engine.snapshot();
    expect(snapshot.eyeLSy).toBeCloseTo(0, 0.001);
    expect(snapshot.faceR).toBeCloseTo(26, 0.001);
    engine.destroy();
  });

  it("applies expression poses", () => {
    const engine = new FaceEngine();
    engine.setExpression("happy", "high");
    step(engine, 120);
    const snapshot = engine.snapshot();
    expect(snapshot.eyeLSx).toBeGreaterThan(1.1);
    expect(snapshot.eyeLR).toBeCloseTo(expressions.happy.high.eyeLR, 1);
    engine.destroy();
  });

  it("composes reactive deltas on top of expression targets", () => {
    const engine = new FaceEngine();
    engine.setExpression("neutral", "high");
    engine.setReactive({ mouthSy: 0.4, eyeTx: -0.3 });
    step(engine, 120);
    const snapshot = engine.snapshot();
    expect(snapshot.mouthSy).toBeCloseTo(1.4, 0.05);
    expect(snapshot.eyeLTx).toBeCloseTo(-0.3, 0.05);
    engine.destroy();
  });

  it("activates behaviors from moods", () => {
    const engine = new FaceEngine();
    engine.setMood("curious");
    const behavior = engine.getBehaviorState();
    expect(behavior.breathing).toBe(true);
    engine.destroy();
  });

  it("tracks sequences and can stop them", () => {
    const engine = new FaceEngine();
    engine.runSequence("nervous");
    expect(engine.currentSequence).toBe("nervous");
    engine.stopSequence();
    expect(engine.currentSequence).toBe(null);
    engine.destroy();
  });
});

describe("Protocol validation", () => {
  it("accepts valid mood commands", () => {
    const command = validateFaceCommand({ mood: "happy" });
    expect(command.mood).toBe("happy");
  });

  it("rejects unknown keys", () => {
    expect(() => validateFaceCommand({ nope: true })).toThrow('Unknown command field');
  });

  it("rejects unknown expressions", () => {
    expect(() => validateFaceCommand({ emotion: "pirouette" })).toThrow('Unknown expression');
  });

  it("rejects invalid reactive keys", () => {
    expect(() => validateFaceCommand({ reactive: { jaw: 1 } })).toThrow('Unknown reactive key');
  });
});

console.log("─".repeat(50));
console.log(`  ${passed + failed} tests: ${failed === 0 ? "\x1b[32m" : "\x1b[31m"}${passed} passed${failed === 0 ? "\x1b[0m" : `, ${failed} failed\x1b[0m`}`);

if (failed > 0) {
  process.exit(1);
}
