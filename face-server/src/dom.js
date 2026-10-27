import { FaceEngine } from "./core.js";

function isElementLike(value) {
  return value && typeof value.querySelector === "function";
}

export function resolveFaceElements(rootOrElements) {
  if (isElementLike(rootOrElements)) {
    return {
      face: rootOrElements,
      leftEye: rootOrElements.querySelector(".left.eye"),
      rightEye: rootOrElements.querySelector(".right.eye"),
      mouth: rootOrElements.querySelector(".mouth"),
      upperLeftEyelid: rootOrElements.querySelector(".left .eyelid.upper"),
      upperRightEyelid: rootOrElements.querySelector(".right .eyelid.upper"),
      lowerLeftEyelid: rootOrElements.querySelector(".left .eyelid.lower"),
      lowerRightEyelid: rootOrElements.querySelector(".right .eyelid.lower"),
    };
  }
  return rootOrElements;
}

function assertElements(elements) {
  const required = [
    "face",
    "leftEye",
    "rightEye",
    "mouth",
    "upperLeftEyelid",
    "upperRightEyelid",
    "lowerLeftEyelid",
    "lowerRightEyelid",
  ];
  for (const key of required) {
    if (!elements?.[key]) {
      throw new Error(`Missing face element "${key}"`);
    }
  }
}

export function applySnapshotToDOM(elements, snapshot) {
  elements.leftEye.style.transform =
    `translateX(${snapshot.eyeLTx}%) translateY(${snapshot.eyeLTy}%) ` +
    `scaleX(${snapshot.eyeLSx}) scaleY(${snapshot.eyeLSy}) rotate(${snapshot.eyeLRot}deg)`;
  elements.leftEye.style.borderRadius = `${snapshot.eyeLBr}%`;
  elements.leftEye.style.backgroundColor = `rgb(${snapshot.eyeLR | 0},${snapshot.eyeLG | 0},${snapshot.eyeLB | 0})`;

  elements.rightEye.style.transform =
    `translateX(${snapshot.eyeRTx}%) translateY(${snapshot.eyeRTy}%) ` +
    `scaleX(${snapshot.eyeRSx}) scaleY(${snapshot.eyeRSy}) rotate(${snapshot.eyeRRot}deg)`;
  elements.rightEye.style.borderRadius = `${snapshot.eyeRBr}%`;
  elements.rightEye.style.backgroundColor = `rgb(${snapshot.eyeRR | 0},${snapshot.eyeRG | 0},${snapshot.eyeRB | 0})`;

  const faceColor = `rgb(${snapshot.faceR | 0},${snapshot.faceG | 0},${snapshot.faceB | 0})`;
  elements.face.style.backgroundColor = faceColor;
  elements.upperLeftEyelid.style.backgroundColor = faceColor;
  elements.upperRightEyelid.style.backgroundColor = faceColor;
  elements.lowerLeftEyelid.style.backgroundColor = faceColor;
  elements.lowerRightEyelid.style.backgroundColor = faceColor;
  elements.upperLeftEyelid.style.transform = `translateY(${snapshot.lidULTy}%) rotate(${snapshot.lidULRot}deg)`;
  elements.lowerLeftEyelid.style.transform = `translateY(${snapshot.lidLLTy}%) rotate(${snapshot.lidLLRot}deg)`;
  elements.upperRightEyelid.style.transform = `translateY(${snapshot.lidURTy}%) rotate(${snapshot.lidURRot}deg)`;
  elements.lowerRightEyelid.style.transform = `translateY(${snapshot.lidLRTy}%) rotate(${snapshot.lidLRRot}deg)`;

  elements.mouth.style.transform =
    `translateX(${snapshot.mouthTx}%) translateY(${snapshot.mouthTy}%) ` +
    `scaleX(${snapshot.mouthSx}) scaleY(${snapshot.mouthSy})`;
  elements.mouth.style.borderRadius =
    `${snapshot.mouthBrTop}% ${snapshot.mouthBrTop}% ${snapshot.mouthBrBot}% ${snapshot.mouthBrBot}%`;
  elements.mouth.style.backgroundColor = `rgb(${snapshot.mouthR | 0},${snapshot.mouthG | 0},${snapshot.mouthB | 0})`;
}

export class FaceRenderer {
  constructor(rootOrElements, opts = {}) {
    this.elements = resolveFaceElements(rootOrElements);
    assertElements(this.elements);
    this.engine = opts.engine || new FaceEngine(opts);
    this._frameId = null;
    this._running = false;
    this._lastTimestamp = null;
    this.render();
    if (opts.autoStart !== false) {
      this.start();
    }
  }

  start() {
    if (this._running) {
      return;
    }
    this._running = true;
    const tick = (timestamp) => {
      if (!this._running) {
        return;
      }
      const dt = this._lastTimestamp == null ? 0.016 : Math.min((timestamp - this._lastTimestamp) / 1000, 0.05);
      this._lastTimestamp = timestamp;
      this.engine.update(dt);
      this.render();
      this._frameId = window.requestAnimationFrame(tick);
    };
    this._frameId = window.requestAnimationFrame(tick);
  }

  stop() {
    this._running = false;
    this._lastTimestamp = null;
    if (this._frameId !== null) {
      window.cancelAnimationFrame(this._frameId);
      this._frameId = null;
    }
  }

  render() {
    applySnapshotToDOM(this.elements, this.engine.snapshot());
  }

  destroy() {
    this.stop();
    this.engine.destroy();
  }

  getBehaviorState() {
    return this.engine.getBehaviorState();
  }

  wake() { this.engine.wakeUp(); }
  sleep() { this.engine.goToSleep(); }
  wakeUp() { this.engine.wakeUp(); }
  goToSleep() { this.engine.goToSleep(); }
  reset() { this.engine.reset(); }
  setMood(name) { this.engine.setMood(name); }
  setExpression(name, intensity) { this.engine.setExpression(name, intensity); }
  setReactive(deltas) { this.engine.setReactive(deltas); }
  clearReactive() { this.engine.clearReactive(); }
  startBlinking() { this.engine.startBlinking(); }
  stopBlinking() { this.engine.stopBlinking(); }
  startBreathing() { this.engine.startBreathing(); }
  stopBreathing() { this.engine.stopBreathing(); }
  startTalking() { this.engine.startTalking(); }
  stopTalking() { this.engine.stopTalking(); }
  startHeartbeat(bpm) { this.engine.startHeartbeat(bpm); }
  stopHeartbeat() { this.engine.stopHeartbeat(); }
  runSequence(name) { return this.engine.runSequence(name); }
  stopSequence() { this.engine.stopSequence(); }
  blink() { this.engine.blink(); }
  kick(keys, velocity) { this.engine.kick(keys, velocity); }

  get sp() {
    return this.engine.sp;
  }
}

export function createFaceRenderer(rootOrElements, opts = {}) {
  return new FaceRenderer(rootOrElements, opts);
}
