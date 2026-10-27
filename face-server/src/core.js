const EXPR_SPRING = { stiffness: 120, damping: 18 };
const COLOR_SPRING = { stiffness: 70, damping: 15 };
const EYE_SPRING = { stiffness: 280, damping: 26 };

export class Spring {
  constructor({ stiffness = 170, damping = 26, mass = 1, initial = 0 } = {}) {
    this.stiffness = stiffness;
    this.damping = damping;
    this.mass = mass;
    this.value = initial;
    this.target = initial;
    this.velocity = 0;
  }

  setTarget(target) {
    this.target = target;
  }

  setImmediate(value) {
    this.value = value;
    this.target = value;
    this.velocity = 0;
  }

  update(dt) {
    const force = this.stiffness * (this.target - this.value) - this.damping * this.velocity;
    this.velocity += (force / this.mass) * dt;
    this.value += this.velocity * dt;
    return this.value;
  }
}

export const NEUTRAL = {
  eyeLSx: 1, eyeLSy: 1, eyeLTx: 0, eyeLTy: 0, eyeLRot: 0, eyeLBr: 50,
  eyeLR: 0, eyeLG: 0, eyeLB: 0,
  eyeRSx: 1, eyeRSy: 1, eyeRTx: 0, eyeRTy: 0, eyeRRot: 0, eyeRBr: 50,
  eyeRR: 0, eyeRG: 0, eyeRB: 0,
  lidULTy: 0, lidULRot: 0,
  lidLLTy: 0, lidLLRot: 0,
  lidURTy: 0, lidURRot: 0,
  lidLRTy: 0, lidLRRot: 0,
  mouthSx: 1, mouthSy: 1, mouthTx: 0, mouthTy: 0,
  mouthBrTop: 0, mouthBrBot: 70,
  mouthR: 255, mouthG: 192, mouthB: 203,
  faceR: 245, faceG: 245, faceB: 245,
};

export const ASLEEP = {
  ...NEUTRAL,
  eyeLSx: 0.8, eyeLSy: 0,
  eyeRSx: 0.8, eyeRSy: 0,
  lidULTy: 100, lidURTy: 100,
  lidLLTy: -100, lidLRTy: -100,
  mouthSx: 0.5, mouthSy: 0.3,
  mouthBrTop: 50, mouthBrBot: 50,
  mouthR: 42, mouthG: 42, mouthB: 42,
  faceR: 26, faceG: 26, faceB: 26,
};

export const expressions = {
  neutral: { low: NEUTRAL, high: NEUTRAL },
  happy: {
    low: {
      eyeLSx: 1.1, eyeLSy: 1.1, eyeLTy: -5, eyeLR: 79, eyeLG: 195, eyeLB: 247,
      eyeRSx: 1.1, eyeRSy: 1.1, eyeRTy: -5, eyeRR: 79, eyeRG: 195, eyeRB: 247,
      lidULTy: -20, lidULRot: 10, lidURTy: -20, lidURRot: -10,
      lidLLTy: -10, lidLRTy: -10,
      mouthSx: 1.5, mouthSy: 1.2,
    },
    high: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLR: 79, eyeLG: 195, eyeLB: 247,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRR: 79, eyeRG: 195, eyeRB: 247,
      lidULTy: -50, lidURTy: -50,
      lidLLTy: -50, lidLLRot: 15, lidLRTy: -50, lidLRRot: -15,
      mouthSx: 1.2, mouthSy: 1.1, mouthR: 255, mouthG: 182, mouthB: 193,
    },
  },
  sad: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.9, eyeLTy: 5, eyeLR: 106, eyeLG: 142, eyeLB: 174,
      eyeRSx: 0.9, eyeRSy: 0.9, eyeRTy: 5, eyeRR: 106, eyeRG: 142, eyeRB: 174,
      lidULTy: 20, lidULRot: -10, lidURTy: 20, lidURRot: 10,
      mouthSx: 0.9, mouthSy: 0.7, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 169, mouthG: 176, mouthB: 179,
    },
    high: {
      eyeLSx: 0.6, eyeLSy: 0.6, eyeLTy: 10, eyeLR: 30, eyeLG: 58, eyeLB: 95,
      eyeRSx: 0.6, eyeRSy: 0.6, eyeRTy: 10, eyeRR: 30, eyeRG: 58, eyeRB: 95,
      lidULTy: 40, lidULRot: -15, lidURTy: 40, lidURRot: 15,
      mouthSx: 0.8, mouthSy: 0.5, mouthBrTop: 0, mouthBrBot: 0,
      mouthR: 112, mouthG: 128, mouthB: 144,
    },
  },
  angry: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.9, eyeLTx: -2, eyeLR: 255, eyeLG: 69, eyeLB: 0,
      eyeRSx: 0.9, eyeRSy: 0.9, eyeRTx: -2, eyeRR: 255, eyeRG: 69, eyeRB: 0,
      lidULTy: 20, lidULRot: 10, lidURTy: 20, lidURRot: -10,
      lidLLTy: 5, lidLRTy: 5,
      mouthSx: 1.1, mouthSy: 0.9, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 205, mouthG: 92, mouthB: 92,
    },
    high: {
      eyeLSx: 1.1, eyeLSy: 1.1, eyeLTx: -5, eyeLR: 255, eyeLG: 0, eyeLB: 0,
      eyeRSx: 1.1, eyeRSy: 1.1, eyeRTx: -5, eyeRR: 255, eyeRG: 0, eyeRB: 0,
      lidULTy: 35, lidULRot: 20, lidURTy: 35, lidURRot: -20,
      lidLLTy: 10, lidLLRot: 10, lidLRTy: 10, lidLRRot: 10,
      mouthSx: 1.2, mouthSy: 0.8, mouthBrTop: 0, mouthBrBot: 0,
      mouthR: 178, mouthG: 34, mouthB: 34,
    },
  },
  surprised: {
    low: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLTy: -10, eyeLR: 176, eyeLG: 196, eyeLB: 222,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRTy: -10, eyeRR: 176, eyeRG: 196, eyeRB: 222,
      lidULTy: -30, lidULRot: 10, lidURTy: -30, lidURRot: -10,
      lidLLTy: 10, lidLRTy: 10,
      mouthSx: 0.75, mouthSy: 1.875, mouthBrTop: 100, mouthBrBot: 100,
      mouthR: 211, mouthG: 211, mouthB: 211,
    },
    high: {
      eyeLSx: 1.5, eyeLSy: 1.5, eyeLR: 135, eyeLG: 206, eyeLB: 235,
      eyeRSx: 1.5, eyeRSy: 1.5, eyeRR: 135, eyeRG: 206, eyeRB: 235,
      lidULTy: -50, lidURTy: -50,
      lidLLTy: 50, lidLLRot: 15, lidLRTy: 50, lidLRRot: -15,
      mouthSx: 1.0, mouthSy: 2.5, mouthBrTop: 100, mouthBrBot: 100,
      mouthR: 70, mouthG: 130, mouthB: 180,
    },
  },
  stressed: {
    low: {
      eyeLSx: 1.2, eyeLSy: 0.8, eyeLTy: -3, eyeLBr: 0,
      eyeLR: 226, eyeLG: 133, eyeLB: 41,
      eyeRSx: 1.2, eyeRSy: 0.8, eyeRTy: -3, eyeRBr: 0,
      eyeRR: 226, eyeRG: 133, eyeRB: 41,
      lidULTy: 20, lidULRot: 5, lidURTy: 20, lidURRot: -5,
      lidLLRot: 5, lidLRRot: 5,
      mouthSx: 1.2, mouthSy: 0.9, mouthBrTop: 0, mouthBrBot: 0,
      mouthR: 205, mouthG: 92, mouthB: 92,
    },
    high: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLTy: -5, eyeLBr: 30,
      eyeLR: 255, eyeLG: 165, eyeLB: 0,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRTy: -5, eyeRBr: 30,
      eyeRR: 255, eyeRG: 165, eyeRB: 0,
      lidULTy: 40, lidULRot: 5, lidURTy: 40, lidURRot: -5,
      lidLLTy: -10, lidLRTy: -10,
      mouthSx: 1.2, mouthSy: 0.8, mouthBrTop: 20, mouthBrBot: 20,
      mouthR: 139, mouthG: 0, mouthB: 0,
    },
  },
  calm: {
    low: {
      eyeLR: 141, eyeLG: 240, eyeLB: 130,
      eyeRR: 141, eyeRG: 240, eyeRB: 130,
      lidLLTy: -15, lidLRTy: -15,
      mouthSx: 0.8, mouthSy: 0.8,
    },
    high: {
      eyeLSx: 1.1, eyeLSy: 1.1, eyeLR: 141, eyeLG: 240, eyeLB: 130,
      eyeRSx: 1.1, eyeRSy: 1.1, eyeRR: 141, eyeRG: 240, eyeRB: 130,
      lidULTy: 10, lidULRot: -10, lidURTy: 10, lidURRot: 10,
      lidLLTy: -20, lidLRTy: -20,
    },
  },
  confused: {
    low: {
      eyeLSx: 1.3, eyeLSy: 1.3, eyeLTy: -5, eyeLBr: 55,
      eyeRSx: 0.8, eyeRSy: 0.8, eyeRTy: 5,
      lidULTy: 10, lidURTy: 10, lidURRot: 5,
      lidLLTy: -15, lidLLRot: -15,
      mouthSx: 1.1, mouthBrTop: 50, mouthBrBot: 50,
      mouthR: 255, mouthG: 218, mouthB: 185,
    },
    high: {
      eyeLSx: 0.6, eyeLSy: 0.6, eyeLTy: 5, eyeLBr: 0, eyeLRot: -10,
      eyeLR: 33, eyeLG: 1, eyeLB: 49,
      eyeRSx: 1.3, eyeRSy: 1.3, eyeRTy: -5, eyeRBr: 60,
      eyeRR: 33, eyeRG: 1, eyeRB: 49,
      lidULTy: 10, lidURTy: 10, lidURRot: 15,
      lidLLTy: 5, lidLRTy: -10, lidLRRot: 15,
      mouthSx: 1.2, mouthBrTop: 50, mouthBrBot: 50,
      mouthR: 244, mouthG: 164, mouthB: 96,
    },
  },
  concern: {
    low: {
      eyeLSy: 0.9, eyeLTy: 2, eyeLR: 245, eyeLG: 222, eyeLB: 179,
      eyeRSy: 0.9, eyeRTy: 2, eyeRR: 245, eyeRG: 222, eyeRB: 179,
      lidULTy: 15, lidULRot: -5, lidURTy: 15, lidURRot: 5,
      mouthSx: 0.9, mouthSy: 0.8, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 210, mouthG: 180, mouthB: 140,
    },
    high: {
      eyeLSx: 0.9, eyeLSy: 0.8, eyeLTy: 5, eyeLR: 222, eyeLG: 184, eyeLB: 135,
      eyeRSx: 0.9, eyeRSy: 0.8, eyeRTy: 5, eyeRR: 222, eyeRG: 184, eyeRB: 135,
      lidULTy: 25, lidULRot: -10, lidURTy: 25, lidURRot: 10,
      mouthSx: 0.8, mouthSy: 0.7, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 160, mouthG: 82, mouthB: 45,
    },
  },
  fear: {
    low: {
      eyeLSx: 1.1, eyeLSy: 1.3, eyeLTy: -5, eyeLR: 173, eyeLG: 216, eyeLB: 230,
      eyeRSx: 1.1, eyeRSy: 1.3, eyeRTy: -5, eyeRR: 173, eyeRG: 216, eyeRB: 230,
      lidULTy: -10, lidULRot: 5, lidURTy: -10, lidURRot: -5,
      lidLLTy: 10, lidLLRot: -5, lidLRTy: 10, lidLRRot: 5,
      mouthSx: 1.2, mouthSy: 0.8, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 240, mouthG: 128, mouthB: 128,
    },
    high: {
      eyeLSx: 1.2, eyeLSy: 1.5, eyeLTy: -10, eyeLR: 70, eyeLG: 130, eyeLB: 180,
      eyeRSx: 1.2, eyeRSy: 1.5, eyeRTy: -10, eyeRR: 70, eyeRG: 130, eyeRB: 180,
      lidULTy: -20, lidULRot: 10, lidURTy: -20, lidURRot: -10,
      lidLLTy: 20, lidLLRot: -10, lidLRTy: 20, lidLRRot: 10,
      mouthSx: 1.5, mouthSy: 0.5, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 178, mouthG: 34, mouthB: 34,
    },
  },
  disgust: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.8, eyeLTy: 5, eyeLR: 154, eyeLG: 205, eyeLB: 50,
      eyeRSx: 0.8, eyeRSy: 0.7, eyeRTy: 10, eyeRR: 154, eyeRG: 205, eyeRB: 50,
      lidULTy: 10, lidULRot: 10, lidURTy: 15, lidURRot: -10,
      mouthSx: 1.1, mouthSy: 0.8, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 210, mouthG: 180, mouthB: 140,
    },
    high: {
      eyeLTy: 10, eyeLR: 85, eyeLG: 107, eyeLB: 47,
      eyeRSx: 0.7, eyeRSy: 0.6, eyeRTy: 15, eyeRR: 85, eyeRG: 107, eyeRB: 47,
      lidULTy: 20, lidULRot: 15, lidURTy: 25, lidURRot: -15,
      lidLLTy: -20, lidLLRot: 15, lidLRTy: -25, lidLRRot: -15,
      mouthSx: 1.2, mouthSy: 1.4, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 139, mouthG: 69, mouthB: 19,
    },
  },
  shocked: {
    low: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLR: 135, eyeLG: 206, eyeLB: 235,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRR: 135, eyeRG: 206, eyeRB: 235,
      lidULTy: 25, lidURTy: 25,
      lidLLTy: -5, lidLLRot: 3, lidLRTy: -5, lidLRRot: -3,
      mouthSx: 0.6, mouthSy: 1.5, mouthBrTop: 50, mouthBrBot: 50,
      mouthR: 255, mouthG: 182, mouthB: 193,
    },
    high: {
      eyeLSx: 1.5, eyeLSy: 1.5, eyeLR: 0, eyeLG: 191, eyeLB: 255,
      eyeRSx: 1.5, eyeRSy: 1.5, eyeRR: 0, eyeRG: 191, eyeRB: 255,
      lidLLTy: -10, lidLLRot: -5, lidLRTy: -10, lidLRRot: 5,
      mouthSx: 2.0, mouthSy: 1.0, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 255, mouthG: 192, mouthB: 203,
    },
  },
  tired: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.9, eyeLBr: 25, eyeLR: 211, eyeLG: 211, eyeLB: 211,
      eyeRSx: 0.9, eyeRSy: 0.9, eyeRBr: 25, eyeRR: 211, eyeRG: 211, eyeRB: 211,
      lidULTy: 35, lidULRot: -10, lidURTy: 35, lidURRot: 10,
      lidLLTy: -5, lidLRTy: -5,
      mouthSx: 0.5, mouthSy: 1.0, mouthBrTop: 50, mouthBrBot: 0,
    },
    high: {
      eyeLSx: 0.5, eyeLSy: 0.5, eyeLR: 128, eyeLG: 128, eyeLB: 128,
      eyeRSx: 0.5, eyeRSy: 0.5, eyeRR: 128, eyeRG: 128, eyeRB: 128,
      lidULTy: 25, lidULRot: 10, lidURTy: 25, lidURRot: -10,
      lidLLTy: -25, lidLRTy: -25,
      mouthSx: 0.6, mouthSy: 1.0, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 216, mouthG: 191, mouthB: 216,
    },
  },
  interested: {
    low: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLBr: 30,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRBr: 30,
      lidULTy: 5, lidURTy: 5, lidLLTy: -5, lidLRTy: -5,
      mouthSx: 0.9, mouthSy: 0.9, mouthBrTop: 0, mouthBrBot: 50,
      mouthR: 255, mouthG: 182, mouthB: 193,
    },
    high: {
      eyeLSx: 1.5, eyeLSy: 1.5, eyeLBr: 0,
      eyeRSx: 1.5, eyeRSy: 1.5, eyeRBr: 0,
      lidULTy: 25, lidURTy: 25, lidLLTy: -10, lidLRTy: -10,
      mouthSx: 0.6, mouthSy: 1.0, mouthBrTop: 0, mouthBrBot: 50,
      mouthR: 255, mouthG: 99, mouthB: 80,
    },
  },
  sorrow: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.9, eyeLR: 176, eyeLG: 196, eyeLB: 222,
      eyeRSx: 0.9, eyeRSy: 0.9, eyeRR: 176, eyeRG: 196, eyeRB: 222,
      lidULTy: 15, lidURTy: 15, lidLLTy: -10, lidLRTy: -10,
      mouthSx: 0.4, mouthSy: 0.75, mouthTy: 5, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 221, mouthG: 182, mouthB: 193,
    },
    high: {
      eyeLSx: 0.5, eyeLSy: 0.5, eyeLR: 112, eyeLG: 128, eyeLB: 144,
      eyeRSx: 0.5, eyeRSy: 0.5, eyeRR: 112, eyeRG: 128, eyeRB: 144,
      lidULTy: 25, lidULRot: -15, lidURTy: 25, lidURRot: 15,
      lidLLTy: -10, lidLLRot: -5, lidLRTy: -10, lidLRRot: 5,
      mouthSx: 0.6, mouthSy: 1.0, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 211, mouthG: 163, mouthB: 163,
    },
  },
  excitement: {
    low: {
      eyeLSx: 1.2, eyeLSy: 1.2, eyeLBr: 20, eyeLR: 173, eyeLG: 216, eyeLB: 230,
      eyeRSx: 1.2, eyeRSy: 1.2, eyeRBr: 20, eyeRR: 173, eyeRG: 216, eyeRB: 230,
      lidULTy: 25, lidURTy: 25, lidLLTy: -10, lidLRTy: -10,
      mouthSx: 1.2, mouthSy: 1.2, mouthBrTop: 0, mouthBrBot: 50,
    },
    high: {
      eyeLSx: 2.0, eyeLSy: 2.0, eyeLTy: -10, eyeLBr: 10,
      eyeLR: 64, eyeLG: 224, eyeLB: 208,
      eyeRSx: 2.0, eyeRSy: 2.0, eyeRTy: -10, eyeRBr: 10,
      eyeRR: 64, eyeRG: 224, eyeRB: 208,
      lidULTy: 50, lidURTy: 50, lidLLTy: -50, lidLRTy: -50,
      mouthSx: 0.9, mouthSy: 1.0, mouthBrTop: 0, mouthBrBot: 50,
      mouthR: 255, mouthG: 127, mouthB: 80,
    },
  },
  anger: {
    low: {
      eyeLSx: 0.9, eyeLSy: 0.9, eyeLBr: 55, eyeLR: 205, eyeLG: 92, eyeLB: 92,
      eyeRSx: 0.9, eyeRSy: 0.9, eyeRBr: 55, eyeRR: 205, eyeRG: 92, eyeRB: 92,
      lidULTy: 25, lidULRot: 2, lidURTy: 25, lidURRot: -2,
      lidLLTy: -5, lidLLRot: -2, lidLRTy: -5, lidLRRot: 2,
      mouthBrTop: 50, mouthBrBot: 0, mouthR: 255, mouthG: 99, mouthB: 71,
    },
    high: {
      eyeLSx: 0.8, eyeLSy: 0.8, eyeLBr: 30, eyeLR: 139, eyeLG: 0, eyeLB: 0,
      eyeRSx: 0.8, eyeRSy: 0.8, eyeRBr: 30, eyeRR: 139, eyeRG: 0, eyeRB: 0,
      lidULTy: 15, lidULRot: 5, lidURTy: 15, lidURRot: -5,
      lidLLTy: -10, lidLLRot: -5, lidLRTy: -10, lidLRRot: 5,
      mouthSx: 1.2, mouthSy: 0.8, mouthBrTop: 50, mouthBrBot: 0,
      mouthR: 210, mouthG: 4, mouthB: 45,
    },
  },
  thinking: {
    low: {
      eyeLTy: -10,
      eyeRSx: 1.2, eyeRSy: 1.2,
      lidURTy: 10, lidURRot: -10, lidLRTy: -10, lidLRRot: -10,
      mouthSx: 0.5, mouthSy: 0.25, mouthBrTop: 0, mouthBrBot: 0,
    },
    high: {
      eyeLTy: -10,
      eyeRSx: 1.2, eyeRSy: 1.2,
      lidURTy: 10, lidURRot: -10, lidLRTy: -10, lidLRRot: -10,
      mouthSx: 0.5, mouthSy: 0.25, mouthBrTop: 0, mouthBrBot: 0,
    },
  },
  listening: {
    low: {
      eyeLSx: 1.1, eyeLSy: 1.1,
      eyeRSx: 1.1, eyeRSy: 1.1,
      lidLLTy: -10, lidLRTy: -10,
      mouthSx: 1.05, mouthBrTop: 50, mouthBrBot: 50,
    },
    high: {
      eyeLSx: 1.1, eyeLSy: 1.1,
      eyeRSx: 1.1, eyeRSy: 1.1,
      lidLLTy: -10, lidLRTy: -10,
      mouthSx: 1.05, mouthBrTop: 50, mouthBrBot: 50,
    },
  },
  mischievous: {
    low: {
      eyeLSy: 1.2, eyeLBr: 25, eyeLTx: 4,
      eyeRSy: 0.55, eyeRBr: 45, eyeRTx: 4,
      lidURTy: 42, lidLRTy: -22,
      mouthSx: 1.1, mouthSy: 0.8, mouthBrBot: 80, mouthTx: 4,
      eyeLR: 255, eyeLG: 195, eyeLB: 80,
      eyeRR: 255, eyeRG: 195, eyeRB: 80,
    },
    high: {
      eyeLSy: 1.3, eyeLBr: 18, eyeLTx: 6,
      eyeRSy: 0.4, eyeRBr: 52, eyeRTx: 6,
      lidURTy: 55, lidLRTy: -32, lidLRRot: -8,
      mouthSx: 1.15, mouthSy: 0.75, mouthBrBot: 88, mouthTx: 6,
      eyeLR: 255, eyeLG: 180, eyeLB: 0,
      eyeRR: 255, eyeRG: 180, eyeRB: 0,
      mouthR: 255, mouthG: 120, mouthB: 60,
    },
  },
  lovestruck: {
    low: {
      eyeLSy: 1.15, eyeLBr: 35,
      eyeLR: 255, eyeLG: 170, eyeLB: 195,
      eyeRSy: 1.15, eyeRBr: 35,
      eyeRR: 255, eyeRG: 170, eyeRB: 195,
      lidULTy: -20, lidURTy: -20, lidLLTy: -18, lidLRTy: -18,
      mouthSx: 1.1, mouthSy: 0.85, mouthBrTop: 0, mouthBrBot: 85,
      mouthR: 255, mouthG: 150, mouthB: 180,
      faceR: 255, faceG: 238, faceB: 248,
    },
    high: {
      eyeLSy: 1.28, eyeLBr: 22,
      eyeLR: 255, eyeLG: 100, eyeLB: 155,
      eyeRSy: 1.28, eyeRBr: 22,
      eyeRR: 255, eyeRG: 100, eyeRB: 155,
      lidULTy: -35, lidURTy: -35, lidLLTy: -28, lidLRTy: -28,
      mouthSx: 1.18, mouthSy: 0.80, mouthBrTop: 8, mouthBrBot: 92,
      mouthR: 255, mouthG: 105, mouthB: 155,
      faceR: 255, faceG: 228, faceB: 242,
    },
  },
  determined: {
    low: {
      eyeLSx: 1.12, eyeLSy: 0.88, eyeLBr: 30,
      eyeLR: 30, eyeLG: 90, eyeLB: 210,
      eyeRSx: 1.12, eyeRSy: 0.88, eyeRBr: 30,
      eyeRR: 30, eyeRG: 90, eyeRB: 210,
      lidULTy: 14, lidULRot: 6, lidURTy: 14, lidURRot: -6,
      mouthSx: 1.22, mouthSy: 0.58, mouthBrTop: 0, mouthBrBot: 0,
      mouthR: 60, mouthG: 95, mouthB: 200,
    },
    high: {
      eyeLSx: 1.18, eyeLSy: 0.92, eyeLBr: 20,
      eyeLR: 0, eyeLG: 55, eyeLB: 255,
      eyeRSx: 1.18, eyeRSy: 0.92, eyeRBr: 20,
      eyeRR: 0, eyeRG: 55, eyeRB: 255,
      lidULTy: 20, lidULRot: 10, lidURTy: 20, lidURRot: -10,
      mouthSx: 1.32, mouthSy: 0.52, mouthBrTop: 0, mouthBrBot: 0,
      mouthR: 40, mouthG: 70, mouthB: 230,
    },
  },
  awe: {
    low: {
      eyeLSx: 1.3, eyeLSy: 1.3, eyeLBr: 15,
      eyeLR: 180, eyeLG: 220, eyeLB: 255,
      eyeRSx: 1.3, eyeRSy: 1.3, eyeRBr: 15,
      eyeRR: 180, eyeRG: 220, eyeRB: 255,
      lidULTy: -40, lidURTy: -40, lidLLTy: 20, lidLRTy: 20,
      mouthSx: 0.8, mouthSy: 1.8, mouthBrTop: 80, mouthBrBot: 80,
      mouthR: 200, mouthG: 220, mouthB: 255,
      faceR: 235, faceG: 242, faceB: 255,
    },
    high: {
      eyeLSx: 1.6, eyeLSy: 1.6, eyeLBr: 8,
      eyeLR: 140, eyeLG: 190, eyeLB: 255,
      eyeRSx: 1.6, eyeRSy: 1.6, eyeRBr: 8,
      eyeRR: 140, eyeRG: 190, eyeRB: 255,
      lidULTy: -55, lidURTy: -55, lidLLTy: 35, lidLRTy: 35,
      mouthSx: 0.65, mouthSy: 2.4, mouthBrTop: 100, mouthBrBot: 100,
      mouthR: 160, mouthG: 200, mouthB: 255,
      faceR: 220, faceG: 235, faceB: 255,
    },
  },
};

export const moods = {
  happy: { expr: "happy", int: "high", blink: true, breathe: true },
  excited: { expr: "excitement", int: "high", blink: true, breathe: true },
  calm: { expr: "calm", int: "high", blink: true, breathe: true },
  delighted: { expr: "lovestruck", int: "low", blink: true, breathe: true },
  playful: { expr: "mischievous", int: "high", blink: true, breathe: true },
  attentive: { expr: "listening", int: "high", blink: true, breathe: true },
  curious: { expr: "interested", int: "high", blink: true, breathe: true },
  thinking: { expr: "thinking", int: "low", blink: false, breathe: true },
  focused: { expr: "determined", int: "high", blink: false, breathe: false },
  confused: { expr: "confused", int: "high", blink: true, breathe: true },
  concerned: { expr: "concern", int: "high", blink: true, breathe: true },
  sad: { expr: "sad", int: "high", blink: true, breathe: true },
  scared: { expr: "fear", int: "low", blink: false, breathe: true },
  angry: { expr: "angry", int: "high", blink: false, breathe: true },
  neutral: { expr: "neutral", int: "high", blink: true, breathe: true },
  tired: { expr: "tired", int: "high", blink: true, breathe: true },
};

export const sequences = {
  startle: (face) => {
    face.kick(["eyeLSy", "eyeRSy"], 7.0);
    face.kick(["eyeLSx", "eyeRSx"], 2.5);
    face.kick(["mouthSy"], 4.0);
    face.kick(["mouthBrTop"], 200);
    face.kick(["lidULTy", "lidURTy"], -40);
    face.kick(["lidLLTy", "lidLRTy"], 30);
    face.setExpression("fear", "high");
    face.after(700, () => face.setExpression("shocked", "low"));
    face.after(1700, () => face.setExpression("surprised", "low"));
    face.after(3200, () => face.setExpression("neutral", "high"));
  },
  laugh: (face) => {
    face.setExpression("happy", "high");
    const ha = () => {
      face.kick("mouthSy", 2.2);
      face.kick("mouthBrTop", 220);
      face.kick(["lidULTy", "lidURTy"], 90);
      face.kick(["eyeLTy", "eyeRTy"], Math.random() > 0.5 ? 2.8 : -2.0);
      face.after(260 + Math.random() * 180, ha);
    };
    ha();
    return () => face.setExpression("happy", "low");
  },
  sob: (face) => {
    face.setExpression("sorrow", "high");
    Object.assign(face._pose, { faceR: 218, faceG: 226, faceB: 240 });
    const squint = () => {
      face.kick(["lidULTy", "lidURTy"], 110);
      face.kick(["lidLLTy", "lidLRTy"], -50);
      face.kick(["eyeLSy", "eyeRSy"], -2.2);
      face.after(220, () => {
        face.kick(["lidULTy", "lidURTy"], -45);
        face.kick(["lidLLTy", "lidLRTy"], 20);
      });
      face.after(1000 + Math.random() * 1100, squint);
    };
    face.after(500, squint);
    return () => face.setExpression("sad", "low");
  },
  realization: (face) => {
    face.setExpression("thinking", "low");
    face.after(1800, () => {
      face.kick(["eyeLSy", "eyeRSy"], 6.5);
      face.kick(["eyeLSx", "eyeRSx"], 2.5);
      face.kick(["mouthSy"], 3.8);
      face.kick(["mouthBrTop"], 250);
      face.kick(["lidULTy", "lidURTy"], -50);
      face.kick(["lidLLTy", "lidLRTy"], 40);
      face.setExpression("surprised", "high");
    });
    face.after(3100, () => face.setExpression("happy", "high"));
    face.after(4600, () => face.setExpression("excitement", "high"));
    face.after(6200, () => face.setExpression("lovestruck", "low"));
    face.after(8000, () => face.setExpression("calm", "high"));
    face.after(10000, () => face.setExpression("neutral", "high"));
  },
  rage: (face) => {
    face.setExpression("concern", "low");
    face.after(800, () => face.setExpression("concern", "high"));
    face.after(1800, () => face.setExpression("stressed", "high"));
    face.after(3000, () => face.setExpression("angry", "high"));
    face.after(4200, () => {
      face.kick(["eyeLSy", "eyeRSy"], -4.5);
      face.kick(["eyeLSx", "eyeRSx"], -1.8);
      face.kick(["lidULTy", "lidURTy"], 45);
      face.kick(["lidLLTy", "lidLRTy"], -25);
      face.kick(["eyeLTx"], -10);
      face.kick(["eyeRTx"], 10);
      face.kick(["mouthSy"], 2.8);
      face.kick(["mouthBrTop"], 150);
      face.setExpression("anger", "high");
      Object.assign(face._pose, { faceR: 255, faceG: 120, faceB: 120 });
    });
    face.after(5800, () => face.setExpression("tired", "high"));
    face.after(8500, () => face.setExpression("neutral", "high"));
  },
  glitch: (face) => {
    const pool = ["surprised", "fear", "angry", "disgust", "shocked", "excitement", "confused", "sorrow", "stressed", "awe"];
    for (let index = 0; index < 16; index += 1) {
      face.after(index * 60, () => {
        face.setExpression(pool[index % pool.length], index % 2 === 0 ? "high" : "low");
        if (index % 2 === 1) {
          face.kick(["eyeLSy", "eyeRSy"], (Math.random() - 0.4) * 12);
          face.kick(["mouthSy"], Math.random() * 6);
          face.kick(["lidULTy", "lidURTy"], (Math.random() - 0.5) * 100);
        }
      });
    }
    face.after(1020, () => {
      for (const spring of Object.values(face.sp)) {
        spring.velocity = 0;
      }
      face.setExpression("shocked", "high");
    });
    face.after(2600, () => face.setExpression("neutral", "high"));
  },
  flirt: (face) => {
    face.setExpression("lovestruck", "low");
    Object.assign(face._pose, {
      eyeLSy: 1.3, eyeLBr: 20, eyeLTx: 6,
      eyeRSy: 0.48, eyeRBr: 50, eyeRTx: 6,
      lidURTy: 50, lidLRTy: -28,
      mouthSx: 1.12, mouthSy: 0.78, mouthBrBot: 90, mouthTx: 5,
    });
    face.after(2200, () => {
      face.kick("eyeRSy", -8.0);
      face.kick(["lidURTy", "lidLRTy"], 80);
    });
    face.after(3800, () => face.setExpression("mischievous", "low"));
    face.after(5800, () => face.setExpression("neutral", "high"));
  },
  awe: (face) => {
    face.setExpression("interested", "low");
    face.after(600, () => face.setExpression("interested", "high"));
    face.after(1800, () => {
      face.kick(["eyeLSy", "eyeRSy"], 3.0);
      face.kick(["lidULTy", "lidURTy"], -30);
      face.kick(["mouthSy"], 2.5);
      face.setExpression("awe", "low");
    });
    face.after(3400, () => face.setExpression("awe", "high"));
    face.after(6000, () => face.setExpression("calm", "high"));
    face.after(8000, () => face.setExpression("neutral", "high"));
  },
  heartbreak: (face) => {
    face.setExpression("lovestruck", "high");
    face.after(2000, () => {
      face.kick(["eyeLSy", "eyeRSy"], -4.0);
      face.kick(["lidULTy", "lidURTy"], 60);
      face.kick(["mouthSy"], -1.5);
      face.setExpression("shocked", "low");
    });
    face.after(2800, () => face.setExpression("sad", "high"));
    face.after(4500, () => face.setExpression("sorrow", "high"));
    face.after(7000, () => {
      face.setExpression("tired", "high");
      Object.assign(face._pose, { faceR: 218, faceG: 218, faceB: 228 });
    });
    face.after(10000, () => face.setExpression("neutral", "high"));
  },
  suspicious: (face) => {
    face.setExpression("neutral", "high");
    face.after(300, () => {
      Object.assign(face._pose, {
        eyeLSy: 0.35, eyeLBr: 55, eyeLTx: -4,
        lidULTy: 40, lidLLTy: -18, lidULRot: 12,
        eyeRSy: 1.1, eyeRBr: 45,
        eyeLR: 180, eyeLG: 130, eyeLB: 50,
        eyeRR: 180, eyeRG: 130, eyeRB: 50,
        mouthSx: 0.9, mouthSy: 0.6, mouthBrTop: 0, mouthBrBot: 20,
        mouthTx: -5,
      });
    });
    face.after(2000, () => Object.assign(face._pose, { eyeLTx: 8, eyeRTx: 8 }));
    face.after(3400, () => Object.assign(face._pose, { eyeLTx: -6, eyeRTx: -6 }));
    face.after(4800, () => face.setExpression("neutral", "high"));
  },
  pride: (face) => {
    face.setExpression("determined", "high");
    face.after(500, () => {
      face.setReactive({ eyeTy: -12, eyeSy: 0.15 });
      Object.assign(face._pose, { mouthTy: -8, mouthSx: 1.1 });
    });
    face.after(2500, () => face.kick(["eyeLSy", "eyeRSy"], 1.5));
    face.after(4000, () => {
      face.clearReactive();
      face.setExpression("calm", "high");
    });
    face.after(6000, () => face.setExpression("neutral", "high"));
  },
  nervous: (face) => {
    face.setExpression("fear", "low");
    Object.assign(face._pose, {
      eyeLSy: 0.85, eyeRSy: 0.85,
      mouthSx: 0.7, mouthSy: 0.5,
    });
    const jitter = () => {
      face.kick(["eyeLSy", "eyeRSy"], (Math.random() - 0.5) * 0.9);
      face.kick(["eyeLTx", "eyeRTx"], (Math.random() - 0.5) * 3.5);
      face.kick(["mouthSy"], Math.random() * 0.4);
      face.after(80 + Math.random() * 180, jitter);
    };
    jitter();
    return () => face.setExpression("neutral", "high");
  },
  demo: (face) => {
    let micIntervalId = null;
    face.setMood("attentive");
    face.after(2000, () => { face.setMood("happy"); face.startTalking(); });
    face.after(5500, () => face.stopTalking());
    face.after(6500, () => face.setMood("curious"));
    face.after(9000, () => face.setMood("thinking"));
    face.after(12000, () => {
      face.kick(["eyeLSy", "eyeRSy"], 5.0);
      face.kick(["mouthSy"], 3.0);
      face.setMood("excited");
    });
    face.after(14000, () => face.startTalking());
    face.after(18000, () => face.stopTalking());
    face.after(19500, () => face.setMood("concerned"));
    face.after(21000, () => face.setMood("thinking"));
    face.after(24000, () => { face.setMood("calm"); face.startTalking(); });
    face.after(26500, () => face.stopTalking());
    face.after(28000, () => {
      face.setMood("attentive");
      micIntervalId = face.every(60, () => {
        const level = 0.2 + 0.5 * Math.abs(Math.sin(Date.now() / 180)) + 0.2 * Math.random();
        face.setReactive({ mouthSy: level * 0.6 });
      });
    });
    face.after(35000, () => {
      if (micIntervalId) {
        clearInterval(micIntervalId);
      }
      face.clearReactive();
      face.setMood("happy");
    });
    face.after(38000, () => face.setMood("tired"));
    face.after(40000, () => face.goToSleep());
    return () => {
      if (micIntervalId) {
        clearInterval(micIntervalId);
      }
      face.clearReactive();
      face.stopTalking();
    };
  },
};

export const WAKEUP_SEQUENCE = [
  { time: 0, pose: { faceR: 26, faceG: 26, faceB: 26 } },
  { time: 500, pose: { faceR: 61, faceG: 61, faceB: 61 } },
  { time: 1200, pose: { faceR: 107, faceG: 107, faceB: 107 } },
  { time: 2000, pose: { faceR: 212, faceG: 212, faceB: 212 } },
  { time: 2500, pose: { faceR: 245, faceG: 245, faceB: 245, mouthR: 255, mouthG: 192, mouthB: 203 } },
  { time: 2000, pose: { eyeLSy: 0.15, eyeLSx: 0.9, eyeRSy: 0.15, eyeRSx: 0.9, lidULTy: 70, lidURTy: 70, lidLLTy: -70, lidLRTy: -70 } },
  { time: 3200, pose: { eyeLSy: 0.02, eyeRSy: 0.02, lidULTy: 95, lidURTy: 95 } },
  { time: 4200, pose: { eyeLSy: 0.5, eyeLSx: 0.95, eyeRSy: 0.5, eyeRSx: 0.95, lidULTy: 40, lidURTy: 40, lidLLTy: -40, lidLRTy: -40 } },
  { time: 5600, pose: { eyeLSy: 0.05, eyeRSy: 0.05, lidULTy: 90, lidURTy: 90 } },
  { time: 6200, pose: { eyeLSy: 0.5, eyeRSy: 0.5, lidULTy: 40, lidURTy: 40 } },
  { time: 7000, pose: { mouthSx: 1.3, mouthSy: 1.6, mouthBrTop: 40, mouthBrBot: 60 } },
  { time: 8800, pose: { mouthSx: 0.85, mouthSy: 0.7, mouthBrTop: 50, mouthBrBot: 50 } },
  { time: 9600, pose: { eyeLSy: 0.85, eyeRSy: 0.85, lidULTy: 10, lidURTy: 10, lidLLTy: -15, lidLRTy: -15 } },
  { time: 10800, pose: { eyeLSy: 1.0, eyeLSx: 1.0, eyeRSy: 1.0, eyeRSx: 1.0, lidULTy: 0, lidURTy: 0, lidLLTy: 0, lidLRTy: 0 } },
  { time: 11500, pose: { mouthSx: 1.0, mouthSy: 1.0, mouthBrTop: 0, mouthBrBot: 70 } },
];

export const SLEEP_SEQUENCE = [
  { time: 0, pose: { eyeLSy: 0.15, eyeRSy: 0.15, lidULTy: 75, lidURTy: 75 } },
  { time: 800, pose: { eyeLSy: 0.75, eyeRSy: 0.75, lidULTy: 25, lidURTy: 25, lidLLTy: -15, lidLRTy: -15 } },
  { time: 1800, pose: { eyeLSy: 0.05, eyeRSy: 0.05, lidULTy: 90, lidURTy: 90 } },
  { time: 2500, pose: { eyeLSy: 0.4, eyeRSy: 0.4, lidULTy: 55, lidURTy: 55 } },
  { time: 2700, pose: { mouthSx: 1.25, mouthSy: 1.5, mouthBrTop: 40, mouthBrBot: 60 } },
  { time: 4300, pose: { mouthSx: 0.7, mouthSy: 0.5, mouthBrTop: 50, mouthBrBot: 50 } },
  { time: 5600, pose: { eyeLSy: 0.2, eyeLSx: 0.9, eyeRSy: 0.2, eyeRSx: 0.9, lidULTy: 70, lidURTy: 70 } },
  { time: 7000, pose: { eyeLSy: 0, eyeLSx: 0.8, eyeRSy: 0, eyeRSx: 0.8, lidULTy: 100, lidURTy: 100, lidLLTy: -100, lidLRTy: -100 } },
  { time: 7500, pose: { mouthSx: 0.5, mouthSy: 0.3, mouthBrTop: 50, mouthBrBot: 50 } },
  { time: 8500, pose: { faceR: 168, faceG: 168, faceB: 168 } },
  { time: 10000, pose: { faceR: 61, faceG: 61, faceB: 61 } },
  { time: 11500, pose: { faceR: 26, faceG: 26, faceB: 26, mouthR: 42, mouthG: 42, mouthB: 42 } },
];

export class FaceEngine {
  constructor(opts = {}) {
    this.expressions = opts.expressions || expressions;
    this.moods = opts.moods || moods;
    this.sequences = opts.sequences || sequences;
    this._pose = { ...ASLEEP };
    this._reactive = {};
    this._breathing = false;
    this._breathPhase = 0;
    this._talking = false;
    this._talkPhase = 0;
    this._blinkTimer = null;
    this._blinkRecoveryTimer = null;
    this._blinkOverride = false;
    this._heartbeatTimer = null;
    this._heartbeatDubTimer = null;
    this._seqTimeouts = [];
    this._seqIntervals = [];
    this._seqCleanup = null;
    this.currentExpression = "neutral";
    this.currentIntensity = "high";
    this.currentMood = null;
    this.currentSequence = null;
    this.sp = {};
    this._initSprings();
  }

  _initSprings() {
    const create = (config, initial) => new Spring({ ...config, initial });
    const initial = ASLEEP;
    this.sp = {
      eyeLSx: create(EXPR_SPRING, initial.eyeLSx), eyeLSy: create(EYE_SPRING, initial.eyeLSy),
      eyeLTx: create(EXPR_SPRING, initial.eyeLTx), eyeLTy: create(EXPR_SPRING, initial.eyeLTy),
      eyeLRot: create(EXPR_SPRING, initial.eyeLRot), eyeLBr: create(EXPR_SPRING, initial.eyeLBr),
      eyeLR: create(COLOR_SPRING, initial.eyeLR), eyeLG: create(COLOR_SPRING, initial.eyeLG), eyeLB: create(COLOR_SPRING, initial.eyeLB),
      eyeRSx: create(EXPR_SPRING, initial.eyeRSx), eyeRSy: create(EYE_SPRING, initial.eyeRSy),
      eyeRTx: create(EXPR_SPRING, initial.eyeRTx), eyeRTy: create(EXPR_SPRING, initial.eyeRTy),
      eyeRRot: create(EXPR_SPRING, initial.eyeRRot), eyeRBr: create(EXPR_SPRING, initial.eyeRBr),
      eyeRR: create(COLOR_SPRING, initial.eyeRR), eyeRG: create(COLOR_SPRING, initial.eyeRG), eyeRB: create(COLOR_SPRING, initial.eyeRB),
      lidULTy: create(EXPR_SPRING, initial.lidULTy), lidULRot: create(EXPR_SPRING, initial.lidULRot),
      lidLLTy: create(EXPR_SPRING, initial.lidLLTy), lidLLRot: create(EXPR_SPRING, initial.lidLLRot),
      lidURTy: create(EXPR_SPRING, initial.lidURTy), lidURRot: create(EXPR_SPRING, initial.lidURRot),
      lidLRTy: create(EXPR_SPRING, initial.lidLRTy), lidLRRot: create(EXPR_SPRING, initial.lidLRRot),
      mouthSx: create(EXPR_SPRING, initial.mouthSx), mouthSy: create(EXPR_SPRING, initial.mouthSy),
      mouthTx: create(EXPR_SPRING, initial.mouthTx), mouthTy: create(EXPR_SPRING, initial.mouthTy),
      mouthBrTop: create(EXPR_SPRING, initial.mouthBrTop), mouthBrBot: create(EXPR_SPRING, initial.mouthBrBot),
      mouthR: create(COLOR_SPRING, initial.mouthR), mouthG: create(COLOR_SPRING, initial.mouthG), mouthB: create(COLOR_SPRING, initial.mouthB),
      faceR: create(COLOR_SPRING, initial.faceR), faceG: create(COLOR_SPRING, initial.faceG), faceB: create(COLOR_SPRING, initial.faceB),
    };
  }

  update(dt) {
    const safeDt = Number.isFinite(dt) && dt >= 0 ? Math.min(dt, 0.05) : 0.016;
    if (this._breathing) {
      this._breathPhase += safeDt;
    }
    if (this._talking) {
      this._talkPhase += safeDt;
    }

    const pose = this._pose;
    const reactive = this._reactive;
    const breathDelta = this._breathing ? 0.05 * Math.sin(this._breathPhase * Math.PI * 2 * 0.35) : 0;
    const talkSyDelta = this._talking ? 0.5 * Math.abs(Math.sin(this._talkPhase * Math.PI * 2 * 2.5)) : 0;
    const talkBrDelta = this._talking ? 40 * Math.abs(Math.sin(this._talkPhase * Math.PI * 2 * 2.5)) : 0;

    const eyeLSyTarget = (this._blinkOverride ? 0 : (pose.eyeLSy ?? NEUTRAL.eyeLSy)) + breathDelta + (reactive.eyeSy || 0);
    const eyeRSyTarget = (this._blinkOverride ? 0 : (pose.eyeRSy ?? NEUTRAL.eyeRSy)) + breathDelta + (reactive.eyeSy || 0);

    this.sp.eyeLSx.setTarget(pose.eyeLSx ?? NEUTRAL.eyeLSx);
    this.sp.eyeLSy.setTarget(eyeLSyTarget);
    this.sp.eyeLTx.setTarget((pose.eyeLTx ?? NEUTRAL.eyeLTx) + (reactive.eyeTx || 0));
    this.sp.eyeLTy.setTarget((pose.eyeLTy ?? NEUTRAL.eyeLTy) + (reactive.eyeTy || 0));
    this.sp.eyeLRot.setTarget(pose.eyeLRot ?? NEUTRAL.eyeLRot);
    this.sp.eyeLBr.setTarget(pose.eyeLBr ?? NEUTRAL.eyeLBr);
    this.sp.eyeLR.setTarget(pose.eyeLR ?? NEUTRAL.eyeLR);
    this.sp.eyeLG.setTarget(pose.eyeLG ?? NEUTRAL.eyeLG);
    this.sp.eyeLB.setTarget(pose.eyeLB ?? NEUTRAL.eyeLB);
    this.sp.eyeRSx.setTarget(pose.eyeRSx ?? NEUTRAL.eyeRSx);
    this.sp.eyeRSy.setTarget(eyeRSyTarget);
    this.sp.eyeRTx.setTarget((pose.eyeRTx ?? NEUTRAL.eyeRTx) + (reactive.eyeTx || 0));
    this.sp.eyeRTy.setTarget((pose.eyeRTy ?? NEUTRAL.eyeRTy) + (reactive.eyeTy || 0));
    this.sp.eyeRRot.setTarget(pose.eyeRRot ?? NEUTRAL.eyeRRot);
    this.sp.eyeRBr.setTarget(pose.eyeRBr ?? NEUTRAL.eyeRBr);
    this.sp.eyeRR.setTarget(pose.eyeRR ?? NEUTRAL.eyeRR);
    this.sp.eyeRG.setTarget(pose.eyeRG ?? NEUTRAL.eyeRG);
    this.sp.eyeRB.setTarget(pose.eyeRB ?? NEUTRAL.eyeRB);
    this.sp.lidULTy.setTarget(pose.lidULTy ?? NEUTRAL.lidULTy);
    this.sp.lidULRot.setTarget(pose.lidULRot ?? NEUTRAL.lidULRot);
    this.sp.lidLLTy.setTarget(pose.lidLLTy ?? NEUTRAL.lidLLTy);
    this.sp.lidLLRot.setTarget(pose.lidLLRot ?? NEUTRAL.lidLLRot);
    this.sp.lidURTy.setTarget(pose.lidURTy ?? NEUTRAL.lidURTy);
    this.sp.lidURRot.setTarget(pose.lidURRot ?? NEUTRAL.lidURRot);
    this.sp.lidLRTy.setTarget(pose.lidLRTy ?? NEUTRAL.lidLRTy);
    this.sp.lidLRRot.setTarget(pose.lidLRRot ?? NEUTRAL.lidLRRot);
    this.sp.mouthSx.setTarget(pose.mouthSx ?? NEUTRAL.mouthSx);
    this.sp.mouthSy.setTarget((pose.mouthSy ?? NEUTRAL.mouthSy) + talkSyDelta + (reactive.mouthSy || 0));
    this.sp.mouthTx.setTarget(pose.mouthTx ?? NEUTRAL.mouthTx);
    this.sp.mouthTy.setTarget(pose.mouthTy ?? NEUTRAL.mouthTy);
    this.sp.mouthBrTop.setTarget((pose.mouthBrTop ?? NEUTRAL.mouthBrTop) + talkBrDelta);
    this.sp.mouthBrBot.setTarget(pose.mouthBrBot ?? NEUTRAL.mouthBrBot);
    this.sp.mouthR.setTarget(pose.mouthR ?? NEUTRAL.mouthR);
    this.sp.mouthG.setTarget(pose.mouthG ?? NEUTRAL.mouthG);
    this.sp.mouthB.setTarget(pose.mouthB ?? NEUTRAL.mouthB);
    this.sp.faceR.setTarget(pose.faceR ?? NEUTRAL.faceR);
    this.sp.faceG.setTarget(pose.faceG ?? NEUTRAL.faceG);
    this.sp.faceB.setTarget(pose.faceB ?? NEUTRAL.faceB);

    for (const spring of Object.values(this.sp)) {
      spring.update(safeDt);
    }

    return this.snapshot();
  }

  snapshot() {
    const snapshot = {};
    for (const [key, spring] of Object.entries(this.sp)) {
      snapshot[key] = spring.value;
    }
    return snapshot;
  }

  setExpression(name, intensity = "high") {
    const expression = this.expressions[name];
    if (!expression) {
      throw new Error(`Unknown expression "${name}"`);
    }
    const pose = expression[intensity] || expression.high || expression.low;
    this._pose = { ...NEUTRAL, ...pose };
    this.currentExpression = name;
    this.currentIntensity = intensity;
    this.currentMood = null;
  }

  reset() {
    this.stopSequence();
    this.stopBlinking();
    this.stopBreathing();
    this.stopTalking();
    this.stopHeartbeat();
    this.clearReactive();
    this._pose = { ...NEUTRAL };
    this.currentExpression = "neutral";
    this.currentIntensity = "high";
    this.currentMood = null;
  }

  setMood(name) {
    const mood = this.moods[name];
    if (!mood) {
      throw new Error(`Unknown mood "${name}"`);
    }
    this.setExpression(mood.expr, mood.int);
    mood.blink ? this.startBlinking() : this.stopBlinking();
    mood.breathe ? this.startBreathing() : this.stopBreathing();
    this.currentMood = name;
  }

  setReactive(deltas) {
    this._reactive = { ...this._reactive, ...deltas };
  }

  clearReactive() {
    this._reactive = {};
  }

  startBreathing() {
    this._breathing = true;
  }

  stopBreathing() {
    this._breathing = false;
    this._breathPhase = 0;
  }

  startTalking() {
    this._talking = true;
    this._talkPhase = 0;
  }

  stopTalking() {
    this._talking = false;
  }

  startBlinking() {
    if (this._blinkTimer || this._blinkRecoveryTimer) {
      return;
    }
    this._scheduleNextBlink();
  }

  stopBlinking() {
    if (this._blinkTimer) {
      clearTimeout(this._blinkTimer);
      this._blinkTimer = null;
    }
    if (this._blinkRecoveryTimer) {
      clearTimeout(this._blinkRecoveryTimer);
      this._blinkRecoveryTimer = null;
    }
    this._blinkOverride = false;
  }

  _scheduleNextBlink() {
    const delay = 2000 + Math.random() * 4000;
    this._blinkTimer = setTimeout(() => this._doBlink(), delay);
  }

  _doBlink() {
    this._blinkTimer = null;
    this._blinkOverride = true;
    this._blinkRecoveryTimer = setTimeout(() => {
      this._blinkOverride = false;
      this._blinkRecoveryTimer = null;
      if (this._breathing || this.currentMood || this.currentExpression) {
        this._scheduleNextBlink();
      }
    }, 150);
  }

  blink() {
    this._doBlink();
  }

  startHeartbeat(bpm = 65) {
    if (this._heartbeatTimer || this._heartbeatDubTimer) {
      return;
    }
    const interval = 60000 / bpm;
    const beat = () => {
      this.kick(["eyeLSy", "eyeRSy"], 2.0);
      this._heartbeatDubTimer = setTimeout(() => {
        this.kick(["eyeLSy", "eyeRSy"], 1.0);
        this._heartbeatDubTimer = null;
      }, 190);
      this._heartbeatTimer = setTimeout(beat, interval);
    };
    beat();
  }

  stopHeartbeat() {
    if (this._heartbeatTimer) {
      clearTimeout(this._heartbeatTimer);
      this._heartbeatTimer = null;
    }
    if (this._heartbeatDubTimer) {
      clearTimeout(this._heartbeatDubTimer);
      this._heartbeatDubTimer = null;
    }
  }

  kick(keys, velocity) {
    for (const key of Array.isArray(keys) ? keys : [keys]) {
      if (this.sp[key]) {
        this.sp[key].velocity += velocity;
      }
    }
  }

  after(ms, fn) {
    const timerId = setTimeout(fn, ms);
    this._seqTimeouts.push(timerId);
    return timerId;
  }

  every(ms, fn) {
    const intervalId = setInterval(fn, ms);
    this._seqIntervals.push(intervalId);
    return intervalId;
  }

  runSequence(name) {
    const sequence = this.sequences[name];
    if (!sequence) {
      throw new Error(`Unknown sequence "${name}"`);
    }
    this.stopSequence();
    this.currentSequence = name;
    const cleanup = sequence(this);
    this._seqCleanup = typeof cleanup === "function" ? cleanup : null;
    return this._seqCleanup;
  }

  stopSequence() {
    for (const timerId of this._seqTimeouts) {
      clearTimeout(timerId);
    }
    for (const intervalId of this._seqIntervals) {
      clearInterval(intervalId);
    }
    this._seqTimeouts = [];
    this._seqIntervals = [];
    this.currentSequence = null;
    if (this._seqCleanup) {
      const cleanup = this._seqCleanup;
      this._seqCleanup = null;
      cleanup();
    }
  }

  _playKeyframes(steps, onComplete) {
    this.stopSequence();
    for (const { time, pose } of steps) {
      this.after(time, () => {
        this._pose = { ...this._pose, ...pose };
      });
    }
    if (onComplete) {
      const lastTime = steps[steps.length - 1].time;
      this.after(lastTime + 1200, onComplete);
    }
  }

  wakeUp() {
    this.stopHeartbeat();
    this.stopTalking();
    this._pose = { ...ASLEEP };
    this._playKeyframes(WAKEUP_SEQUENCE, () => {
      this._pose = { ...NEUTRAL };
      this.startBlinking();
      this.startBreathing();
      this.currentExpression = "neutral";
      this.currentIntensity = "high";
    });
  }

  goToSleep() {
    this.stopBlinking();
    this.stopBreathing();
    this.stopTalking();
    this.stopHeartbeat();
    this.clearReactive();
    this._pose = { ...NEUTRAL };
    this._playKeyframes(SLEEP_SEQUENCE);
  }

  getBehaviorState() {
    return {
      breathing: this._breathing,
      talking: this._talking,
      blinking: Boolean(this._blinkTimer || this._blinkRecoveryTimer || this._blinkOverride),
      heartbeat: Boolean(this._heartbeatTimer || this._heartbeatDubTimer),
    };
  }

  destroy() {
    this.stopSequence();
    this.stopBlinking();
    this.stopHeartbeat();
    this.stopBreathing();
    this.stopTalking();
    this.clearReactive();
  }
}

export const FACE_CONSTANTS = {
  EXPR_SPRING,
  COLOR_SPRING,
  EYE_SPRING,
};
