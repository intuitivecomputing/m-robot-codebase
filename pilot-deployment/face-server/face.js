/**
 * @fileoverview
 * Defines the FaceController class to manage and animate facial expressions on a webpage.
 * This file handles the animation of eyes and mouth based on real-time events received
 * through Socket.IO from the server.
 *
 * @requires anime: Anime.js library used for smooth animation effects.
 */

class FaceController {
  /**
   * Constructs an instance of the FaceController with specific DOM elements.
   * @param {Object} elements - DOM elements for the face, eyes, eyelids, and mouth.
   */
  constructor(elements = {}) {
    Object.assign(this, elements); // Merge elements into 'this'
  }

  /**
   * Animates a property of a target element.
   * @param {Array | Object} target - DOM elements to be animated.
   * @param {string} property - CSS property to animate.
   * @param {Array | number | string} value - End value(s) of the animation.
   * @param {number} duration - Duration of the animation in milliseconds.
   */
  animateProperty(target, property, value, duration = 1000) {
    anime({
      targets: target,
      [property]: value,
      duration: duration,
      easing: "easeInOutQuad",
    });
  }

  /**
   * Triggers a blink animation on the eyes.
   * @param {number} duration - Duration of the blink animation in milliseconds.
   */
  blink(duration = 150) {
    this.animateProperty(
      [this.leftEye, this.rightEye],
      "scaleY",
      [1, 0, 1],
      duration
    );
  }

  /**
   * Starts an infinite blinking loop for the eyes.
   */
  startBlinking() {
    this.blinkingTimeline = anime.timeline({
      easing: "easeInOutQuad",
      loop: true,
      duration: 1800,
    });

    this.blinkingTimeline.add(
      {
        targets: [this.leftEye, this.rightEye],
        scaleY: [1, 0, 1],
        duration: 500,
      },
      1700
    );
  }

  /**
   * Stops the blinking animation and resets the eyes to the original state.
   */
  stopBlinking() {
    if (this.blinkingTimeline) {
      this.blinkingTimeline.pause();
      this.blinkingTimeline = null;
      anime({
        targets: [this.leftEye, this.rightEye],
        scaleY: 1,
        duration: 500,
        easing: "easeOutQuad",
      });
    }
  }

  /**
   * Resets all facial features to their original state, stopping all ongoing animations.
   * Future work: Separate resetting of facial features and stopping of individual animations.
   */
  resetToOriginalState() {
    // calls for stopping talking, blinking and breathing actions, if any.
    //this.stopTalking();
    this.stopBlinking();
    this.stopBreathing();

    const timeline = anime.timeline({
      easing: "easeOutQuad",
      duration: 500,
    });

    timeline
      .add({
        targets: [this.leftEye, this.rightEye],
        backgroundColor: "#000000",
        scaleX: 1,
        scaleY: 1,
        skewX: 0,
        skewY: 0,
        skew: 0,
        scale: 1,
        translateX: "0%",
        translateY: "0%",
        borderRadius: "50%",
        duration: 500,
        easing: "easeOutQuad",
      }, 0)
      .add(
        {
          targets: [
            this.upperLeftEyelid,
            this.upperRightEyelid,
            this.lowerRightEyelid,
            this.lowerLeftEyelid,
          ],
          translateY: "0%",
          rotate: "0deg",
          duration: 500,
          easing: "easeInOutSine",
        },
        0
      )
      .add({
        targets: this.mouth,
        backgroundColor: "#ffc0cb",
        scaleX: 1,
        scaleY: 1,
        scale: 1,
        width: "20vmin",
        height: "8vmin",
        translateX: "0%",
        translateY: "0%",
        borderRadius: ["50% 50% 50% 50%", "0% 0% 70% 70%"],
        rotate: "0deg",
        duration: 500,
        easing: "easeOutQuad",
      }, 0)
      .add(
        {
          targets: [
            this.face,
            this.lowerLeftEyelid,
            this.lowerRightEyelid,
            this.upperLeftEyelid,
            this.upperRightEyelid,
          ],
          backgroundColor: "#f5f5f5",
        },
        0
      );
  }

  /**
   * Implementation of a listening/'interested' expression
   * Future work: Add random variations to range of scaling, etc for a more dynamic feeling
   */
  expressListening() {
    const timeline = anime.timeline({
      easing: "easeOutQuad",
      duration: 500,
    });

    timeline
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleX: 1.1,
        scaleY: 1.1,
        duration: 500,
        easing: "easeOutQuad",
      })
      .add(
        {
          targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
          translateY: "-10%",
          duration: 500,
          easing: "easeInOutSine",
        },
        0
      )
      .add({
        targets: this.mouth,
        borderRadius: "50% 50% 50% 50%",
        translateY: "0%",
        scaleX: 1.05,
        scaleY: 1,
        duration: 500,
        easing: "easeOutQuad",
      });
  }

  /**
   * Implementation of a talking animation
   *  Future work: Add random variations to range of scaling, etc for a more dynamic feeling
   */
  startTalking() {
    this.talkingTimeline = anime.timeline({
      easing: "easeInOutQuad",
      loop: true,
      duration: 200,
    });

    this.talkingTimeline
      .add({
        targets: this.mouth,
        scaleY: [1, 1.2],
        scaleX: [1, 1.1],
        duration: 200,
        easing: "easeInOutSine",
      })
      .add({
        targets: this.mouth,
        scaleY: 1,
        scaleX: 1,
        duration: 200,
        easing: "easeInOutSine",
      })
      .add({
        targets: this.mouth,
        scaleY: [1, 1.3],
        scaleX: [1, 1.15],
        duration: 300,
        easing: "easeInOutSine",
      })
      .add({
        targets: this.mouth,
        scaleY: 1,
        scaleX: 1,
        duration: 300,
        easing: "easeInOutSine",
      });
  }

  /**
   * Function to terminate the talking animation
   */
  stopTalking() {
    if (this.talkingTimeline) {
      this.talkingTimeline.pause();
      this.talkingTimeline = null;

      anime({
        targets: this.mouth,
        scaleY: 1,
        scaleX: 1,
        duration: 500,
        easing: "easeOutQuad",
      });
    }
  }

  /**
   * Implementation of a breathing animation
   *  Future work: Add random variations to range of scaling, etc for a more dynamic feeling
   */
  startBreathing() {
    this.breathingTimeline = anime.timeline({
      easing: "easeInOutQuad",
      loop: true,
    });

    this.breathingTimeline
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [1, 0.9, 1],
        duration: 1000,
      })
      .add({
        targets: this.face,
        scale: [0.99, 1.01],
        duration: 1500,
      })
      .add({
        targets: this.face,
        scale: [1.01, 0.99],
        duration: 1500,
      });
  }

  /**
   * Function to terminate the breathing animation
   */
  stopBreathing() {
    if (this.breathingTimeline) {
      this.breathingTimeline.pause();
      this.breathingTimeline = null;

      anime({
        targets: [this.leftEye, this.rightEye],
        scaleY: 1,
        duration: 500,
        easing: "easeOutQuad",
      });

      anime({
        targets: this.face,
        scale: 1,
        duration: 500,
        easing: "easeOutQuad",
      });
    }
  }

  /**
   * Implementation of a wake-up animation sequence.
   * The face starts completely dark (sleeping), slowly brightens,
   * eyes gradually open with sleepy blinks, then fully awaken.
   * This creates an immersive "coming to life" effect.
   */
  wakeUp() {
    // First, set initial "asleep" state - everything dark and eyes closed
    anime.set(this.face, { backgroundColor: "#1a1a1a" });
    anime.set([this.upperLeftEyelid, this.upperRightEyelid], { 
      backgroundColor: "#1a1a1a",
      translateY: "100%" 
    });
    anime.set([this.lowerLeftEyelid, this.lowerRightEyelid], { 
      backgroundColor: "#1a1a1a",
      translateY: "-100%" 
    });
    anime.set([this.leftEye, this.rightEye], { 
      scaleY: 0,
      scaleX: 0.8 
    });
    anime.set(this.mouth, { 
      backgroundColor: "#2a2a2a",
      scaleX: 0.5,
      scaleY: 0.3,
      borderRadius: "50%"
    });

    const timeline = anime.timeline({
      easing: "easeInOutSine",
    });

    // Phase 1: Slowly transition from darkness to light (dawn breaking)
    timeline
      .add({
        targets: this.face,
        backgroundColor: ["#1a1a1a", "#3d3d3d", "#6b6b6b", "#a8a8a8", "#d4d4d4", "#f5f5f5"],
        duration: 2500,
        easing: "easeInOutQuad",
      })
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid, this.lowerLeftEyelid, this.lowerRightEyelid],
        backgroundColor: ["#1a1a1a", "#6b6b6b", "#a8a8a8", "#f5f5f5"],
        duration: 2000,
        easing: "easeInOutQuad",
      }, 500)
      .add({
        targets: this.mouth,
        backgroundColor: ["#2a2a2a", "#8b6b6b", "#c9a0a0", "#ffc0cb"],
        scaleX: [0.5, 0.7],
        scaleY: [0.3, 0.5],
        duration: 1500,
        easing: "easeOutQuad",
      }, 1000)

      // Phase 2: Eyes start to crack open - first flutter
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0, 0.15],
        scaleX: [0.8, 0.9],
        duration: 1000,
        easing: "easeOutQuad",
      }, 2000)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["100%", "70%"],
        duration: 1000,
        easing: "easeOutQuad",
      }, 2000)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-100%", "-70%"],
        duration: 1000,
        easing: "easeOutQuad",
      }, 2000)

      // Phase 3: First sleepy blink - heavy, slow close (fighting to stay awake)
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.15, 0.02],
        duration: 800,
        easing: "easeInOutSine",
      }, 3200)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["70%", "95%"],
        duration: 800,
        easing: "easeInOutSine",
      }, 3200)

      // Phase 4: Open to halfway - slow, groggy opening
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.02, 0.5],
        scaleX: [0.9, 0.95],
        duration: 1200,
        easing: "easeOutQuad",
      }, 4200)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["95%", "40%"],
        duration: 1200,
        easing: "easeOutQuad",
      }, 4200)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-70%", "-40%"],
        duration: 1200,
        easing: "easeOutQuad",
      }, 4200)

      // Phase 5: Second sleepy blink - still heavy but slightly faster
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.5, 0.05, 0.5],
        duration: 600,
        easing: "easeInOutSine",
      }, 5600)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["40%", "90%", "40%"],
        duration: 600,
        easing: "easeInOutSine",
      }, 5600)

      // Phase 6: Third blink with a slight head tilt feeling (asymmetric) - getting more awake
      .add({
        targets: this.leftEye,
        scaleY: [0.5, 0.1, 0.6],
        duration: 450,
        easing: "easeInOutSine",
      }, 6400)
      .add({
        targets: this.rightEye,
        scaleY: [0.5, 0.08, 0.55],
        duration: 500,
        easing: "easeInOutSine",
      }, 6450)
      .add({
        targets: this.upperLeftEyelid,
        translateY: ["40%", "85%", "30%"],
        duration: 450,
        easing: "easeInOutSine",
      }, 6400)
      .add({
        targets: this.upperRightEyelid,
        translateY: ["40%", "88%", "35%"],
        duration: 500,
        easing: "easeInOutSine",
      }, 6450)

      // Phase 7: Yawn - slow build up, hold at peak, quick release
      .add({
        targets: this.mouth,
        scaleX: [0.7, 1.3],
        scaleY: [0.5, 1.6],
        borderRadius: ["50%", "40% 40% 60% 60%"],
        duration: 1800,
        easing: "easeOutQuad",
      }, 7000)
      // Hold at peak briefly then quick release
      .add({
        targets: this.mouth,
        scaleX: [1.3, 0.85],
        scaleY: [1.6, 0.7],
        borderRadius: ["40% 40% 60% 60%", "50%"],
        duration: 600,
        easing: "easeInQuad",
      }, 8800)

      // Phase 8: Eyes start opening wider - gradual, not bouncy
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.6, 0.85],
        scaleX: [0.95, 1],
        duration: 1000,
        easing: "easeOutQuad",
      }, 9600)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["30%", "10%"],
        duration: 1000,
        easing: "easeOutQuad",
      }, 9600)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-40%", "-15%"],
        duration: 1000,
        easing: "easeOutQuad",
      }, 9600)

      // Phase 9: Gentle stretch and fully open - satisfying but smooth
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.85, 1.08, 1],
        scaleX: [1, 1.05, 1],
        duration: 1200,
        easing: "easeOutQuad",
      }, 10800)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["10%", "-5%", "0%"],
        duration: 1200,
        easing: "easeOutQuad",
      }, 10800)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-15%", "3%", "0%"],
        duration: 1200,
        easing: "easeOutQuad",
      }, 10800)

      // Phase 10: Mouth settles into relaxed smile
      .add({
        targets: this.mouth,
        scaleX: [0.85, 1],
        scaleY: [0.7, 1],
        borderRadius: ["50%", "0% 0% 70% 70%"],
        width: "20vmin",
        height: "8vmin",
        duration: 1000,
        easing: "easeOutQuad",
      }, 11500)

      // Phase 11: Final content blink - slower, relaxed, awake
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [1, 0.1, 1],
        duration: 350,
        easing: "easeInOutSine",
      }, 12800)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["0%", "80%", "0%"],
        duration: 350,
        easing: "easeInOutSine",
      }, 12800);

    return timeline;
  }

  /**
   * Implementation of a go-to-sleep animation sequence.
   * The face starts fully awake, gets progressively drowsy with heavy blinks,
   * yawns, eyes slowly close, and the face fades to black (asleep).
   * This creates an immersive "falling asleep" effect.
   */
  goToSleep() {
    const timeline = anime.timeline({
      easing: "easeInOutSine",
    });

    // Phase 1: First drowsy blink - starting to feel tired
    timeline
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [1, 0.15, 0.9],
        duration: 500,
        easing: "easeInOutSine",
      }, 0)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["0%", "75%", "10%"],
        duration: 500,
        easing: "easeInOutSine",
      }, 0)

      // Phase 2: Eyes droop slightly - getting heavier
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.9, 0.75],
        duration: 800,
        easing: "easeInOutQuad",
      }, 800)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["10%", "25%"],
        duration: 800,
        easing: "easeInOutQuad",
      }, 800)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["0%", "-15%"],
        duration: 800,
        easing: "easeInOutQuad",
      }, 800)

      // Phase 3: Second heavy blink - fighting sleep
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.75, 0.05, 0.6],
        duration: 700,
        easing: "easeInOutSine",
      }, 1800)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["25%", "90%", "35%"],
        duration: 700,
        easing: "easeInOutSine",
      }, 1800)

      // Phase 4: Yawn begins - slow build up
      .add({
        targets: this.mouth,
        scaleX: [1, 1.25],
        scaleY: [1, 1.5],
        borderRadius: ["0% 0% 70% 70%", "40% 40% 60% 60%"],
        duration: 1600,
        easing: "easeOutQuad",
      }, 2700)

      // Phase 5: Yawn release - quicker decay
      .add({
        targets: this.mouth,
        scaleX: [1.25, 0.7],
        scaleY: [1.5, 0.5],
        borderRadius: ["40% 40% 60% 60%", "50%"],
        duration: 500,
        easing: "easeInQuad",
      }, 4300)

      // Phase 6: Third very heavy blink - barely staying awake
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.6, 0.03, 0.4],
        duration: 900,
        easing: "easeInOutSine",
      }, 4500)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["35%", "95%", "55%"],
        duration: 900,
        easing: "easeInOutSine",
      }, 4500)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-15%", "-30%"],
        duration: 900,
        easing: "easeInOutSine",
      }, 4500)

      // Phase 7: Eyes barely open - losing the battle
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.4, 0.2],
        scaleX: [1, 0.9],
        duration: 1200,
        easing: "easeInOutQuad",
      }, 5600)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["55%", "70%"],
        duration: 1200,
        easing: "easeInOutQuad",
      }, 5600)

      // Phase 8: Final slow close - drifting off
      .add({
        targets: [this.leftEye, this.rightEye],
        scaleY: [0.2, 0],
        scaleX: [0.9, 0.8],
        duration: 1800,
        easing: "easeInQuad",
      }, 7000)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid],
        translateY: ["70%", "100%"],
        duration: 1800,
        easing: "easeInQuad",
      }, 7000)
      .add({
        targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
        translateY: ["-30%", "-100%"],
        duration: 1800,
        easing: "easeInQuad",
      }, 7000)

      // Phase 9: Mouth relaxes into sleep
      .add({
        targets: this.mouth,
        scaleX: [0.7, 0.5],
        scaleY: [0.5, 0.3],
        borderRadius: "50%",
        duration: 1500,
        easing: "easeInOutQuad",
      }, 7500)

      // Phase 10: Face begins to dim - lights going out
      .add({
        targets: this.face,
        backgroundColor: ["#f5f5f5", "#d4d4d4", "#a8a8a8"],
        duration: 2500,
        easing: "easeInQuad",
      }, 8500)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid, this.lowerLeftEyelid, this.lowerRightEyelid],
        backgroundColor: ["#f5f5f5", "#d4d4d4", "#a8a8a8"],
        duration: 2500,
        easing: "easeInQuad",
      }, 8500)

      // Phase 11: Continue dimming to darkness
      .add({
        targets: this.face,
        backgroundColor: ["#a8a8a8", "#6b6b6b", "#3d3d3d", "#1a1a1a"],
        duration: 2500,
        easing: "easeInQuad",
      }, 10500)
      .add({
        targets: [this.upperLeftEyelid, this.upperRightEyelid, this.lowerLeftEyelid, this.lowerRightEyelid],
        backgroundColor: ["#a8a8a8", "#6b6b6b", "#3d3d3d", "#1a1a1a"],
        duration: 2500,
        easing: "easeInQuad",
      }, 10500)
      .add({
        targets: this.mouth,
        backgroundColor: ["#ffc0cb", "#c9a0a0", "#8b6b6b", "#2a2a2a"],
        duration: 2500,
        easing: "easeInQuad",
      }, 10500);

    return timeline;
  }

  /**
   * Intial implementation of a thinking expression
   * Future work: Needs a few iterations to accurately depict thinking
   */
  expressThinking() {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    timeline
      .add(
        {
          targets: this.leftEye,
          scaleX: 1,
          scaleY: 1,
          borderRadius: "50%",
          translateX: "0%",
          translateY: "-10%",
        },
        0
      )
      .add(
        {
          targets: this.rightEye,
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "50%",
          translateX: "0%",
          translateY: "0%",
        },
        0
      )
      .add(
        {
          targets: this.upperRightEyelid,
          translateY: "10%",
          rotate: "-10deg",
        },
        0
      )
      .add(
        {
          targets: this.lowerRightEyelid,
          translateY: "-10%",
          rotate: "-10deg",
        },
        0
      )
      .add(
        {
          targets: this.mouth,
          backgroundColor: "#FFC0CB",
          scaleX: 1,
          scaleY: 1,
          borderRadius: "0%",
          translateX: "0%",
          translateY: "0%",
          width: "10vmin",
          height: "2vmin",
        },
        0
      );
  }

  /**
   * Implementation of a happy expression
   * High-intensity and low-intensity versions for a joyful emotion.
   */
  expressHappy(intensity = "high") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.1,
          scaleY: 1.1,
          translateY: "-5%",
          backgroundColor: "#4FC3F7", // Bright blue
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "-20%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-10%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.5,
          scaleY: 1.2,
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.2,
          scaleY: 1.2,
          backgroundColor: "#4FC3F7", // Bright blue
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "-50%",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-50%",
            rotate: "15deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-50%",
            rotate: "-15deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 1.1,
          backgroundColor: "#FFB6C1", // Soft pink
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a sad expression
   * High-intensity and low-intensity versions for a sorrowful emotion.
   */
  expressSad(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 0.9,
          scaleY: 0.9,
          translateY: "5%",
          backgroundColor: "#6A8EAE", // Softer blue
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "20%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "20%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 0.9,
          scaleY: 0.7,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#A9B0B3", // Pale grayish-blue
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 0.6,
          scaleY: 0.6,
          translateY: "10%",
          backgroundColor: "#1E3A5F", // Deep blue
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "40%",
            rotate: "-15deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "40%",
            rotate: "15deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 0.8,
          scaleY: 0.5,
          borderRadius: "0%",
          backgroundColor: "#708090", // Muted grayish-blue
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of an angry expression
   * High-intensity and low-intensity versions for an angry emotion.
   */
  expressAngry(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "high") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.1,
          scaleY: 1.1,
          translateX: "-5%",
          backgroundColor: "#FF0000", // Bright red
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "35%",
            rotate: "20deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "35%",
            rotate: "-20deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "10%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 0.8,
          borderRadius: "0%",
          backgroundColor: "#B22222", // Deep red
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 0.9,
          scaleY: 0.9,
          translateX: "-2%",
          backgroundColor: "#FF4500", // Dark orange
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "20%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "20%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "5%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.1,
          scaleY: 0.9,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#CD5C5C", // Muted red
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a surprised expression
   * High-intensity and low-intensity versions for a surprised emotion.
   */
  expressSurprised(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.2,
          scaleY: 1.2,
          translateY: "-10%",
          backgroundColor: "#B0C4DE", // Light Steel Blue for low intensity surprise
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "-30%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "10%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          width: "15vmin",
          height: "15vmin",
          borderRadius: "100%", // Round mouth for low intensity
          backgroundColor: "#D3D3D3", // Light Gray for low intensity
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.5,
          scaleY: 1.5,
          backgroundColor: "#87CEEB", // Sky Blue for high intensity surprise
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "-50%",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "50%",
            rotate: "15deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "50%",
            rotate: "-15deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          width: "20vmin",
          height: "20vmin",
          borderRadius: "100%", // Round mouth for high intensity
          backgroundColor: "#4682B4", // Steel Blue for high intensity
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a stressed expression
   * High-intensity and low-intensity versions for a stressed emotion.
   */
  expressStressed(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.2,
          scaleY: 0.8,
          translateY: "-3%",
          backgroundColor: "rgba(226, 133, 41, 1)", // Muted orange for low intensity stress
          borderRadius: "0%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "20%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "20%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 0.9,
          borderRadius: "0",
          backgroundColor: "#CD5C5C", // Muted red for low intensity stress
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.2,
          scaleY: 1.2,
          translateY: "-5%",
          backgroundColor: "#FFA500", // Bright orange for high intensity stress
          borderRadius: "30%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "40%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "40%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-10%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 0.8,
          borderRadius: "20%",
          backgroundColor: "#8B0000", // Deep red for high intensity stress
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a calm expression
   * High-intensity and low-intensity versions for a calm emotion.
   */
  expressCalm(intensity = "high") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.0,
          scaleY: 1.0,
          backgroundColor: "rgba(141, 240, 130, 1)",
          borderRadius: "50%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-15%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 0.8,
          scaleY: 0.8,
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.1,
          scaleY: 1.1,
          backgroundColor: "rgba(141, 240, 130, 1)",
          borderRadius: "50%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "10%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "10%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-20%",
            duration: 1000,
          },
          0
        )
    }
  }

  /**
   * Implementation of a confusion expression
   * High-intensity and low-intensity versions for a puzzled emotion.
   */
  expressConfused(intensity = "high") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye],
          scaleX: 1.3,
          scaleY: 1.3,
          translateY: "-5%",
          borderRadius: "55%",
          duration: 1000,
        })
        .add({
          targets: [this.rightEye],
          scaleX: 0.8,
          scaleY: 0.8,
          translateY: "5%",
          borderRadius: "50%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid],
          translateY: "10%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperRightEyelid],
          translateY: "10%",
          rotate: "5deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerLeftEyelid],
          translateY: "-15%",
          rotate: "-15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          scaleX: 1.1,
          scaleY: 1.0,
          borderRadius: "50% 50% 50% 50%",
          backgroundColor: "#FFDAB9", // Light peach
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.rightEye],
          scaleX: 1.3,
          scaleY: 1.3,
          translateY: "-5%",
          backgroundColor: "rgba(33, 1, 49, 1)", // Pale yellow
          borderRadius: "60%",
          duration: 1000,
        })
        .add({
          targets: [this.leftEye],
          scaleX: 0.6,
          scaleY: 0.6,
          rotate: "-10deg",
          translateY: "5%",
          backgroundColor: "rgba(33, 1, 49, 1)", // Pale yellow
          borderRadius: "0%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperRightEyelid],
          translateY: "10%",
          rotate: "15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid],
          translateY: "10%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerRightEyelid],
          translateY: "-10%",
          rotate: "15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerLeftEyelid],
          translateY: "5%",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 1.0,
          borderRadius: "50% 50%",
          backgroundColor: "#F4A460", // Muted orange
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a concern expression
   * High-intensity and low-intensity versions for a worried emotion.
   */
  expressConcern(intensity = "high") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.0,
          scaleY: 0.9,
          translateY: "2%",
          backgroundColor: "#F5DEB3", // Wheat color for subtle concern
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "15%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "15%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 0.9,
          scaleY: 0.8,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#D2B48C", // Tan color for subtle concern
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 0.9,
          scaleY: 0.8,
          translateY: "5%",
          backgroundColor: "#DEB887", // Burlywood color for intense concern
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "25%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "25%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 0.8,
          scaleY: 0.7,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#A0522D", // Sienna color for intense concern
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a fear expression
   * High-intensity and low-intensity versions for a fearful emotion.
   */
  expressFear(intensity = "high") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.1,
          scaleY: 1.3,
          translateY: "-5%",
          backgroundColor: "#ADD8E6", // Light blue for subtle fear
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "-10%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "-10%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "10%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "10%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 0.8,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#F08080", // Light coral for subtle fear
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          scaleX: 1.2,
          scaleY: 1.5,
          translateY: "-10%",
          backgroundColor: "#4682B4", // Steel blue for intense fear
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "-20%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "-20%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "20%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "20%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          scaleX: 1.5,
          scaleY: 0.5,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#B22222", // Firebrick red for intense fear
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a disgust expression
   * High-intensity and low-intensity versions for a disgusted emotion.
   */
  expressDisgust(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye],
          scaleX: 0.9,
          scaleY: 0.8,
          translateY: "5%",
          backgroundColor: "#9ACD32", // Yellow-green for subtle disgust
          duration: 1000,
        })
        .add({
          targets: [this.rightEye],
          scaleX: 0.8,
          scaleY: 0.7,
          translateY: "10%",
          backgroundColor: "#9ACD32",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid],
          translateY: "10%",
          rotate: "10deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperRightEyelid],
          translateY: "15%",
          rotate: "-10deg",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          scaleX: 1.1,
          scaleY: 0.8,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#D2B48C", // Tan for subtle disgust
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye],
          translateY: "10%",
          backgroundColor: "#556B2F", // Dark olive green for intense disgust
          duration: 1000,
        })
        .add({
          targets: [this.rightEye],
          scaleX: 0.7,
          scaleY: 0.6,
          translateY: "15%",
          backgroundColor: "#556B2F",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid],
          translateY: "20%",
          rotate: "15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperRightEyelid],
          translateY: "25%",
          rotate: "-15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerLeftEyelid],
          translateY: "-20%",
          rotate: "15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerRightEyelid],
          translateY: "-25%",
          rotate: "-15deg",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          scaleX: 1.2,
          scaleY: 1.4,
          borderRadius: "50% 50% 0% 0%",
          backgroundColor: "#8B4513", // Saddle brown for intense disgust
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a shocked expression
   * High-intensity and low-intensity versions for a shocked emotion.
   */
  expressShocked(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#87CEEB",
          scaleX: 1.2,
          scaleY: 1.2,
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "25%",
            rotate: "0deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-5%",
            rotate: "3deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-5%",
            rotate: "-3deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FFB6C1",
          width: "12vmin",
          height: "12vmin",
          borderRadius: "50%",
          translateX: "0%",
          translateY: "0%",
          rotate: "0deg",
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#00BFFF",
          scaleX: 1.5,
          scaleY: 1.5,
          borderRadius: "50%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "0%",
            rotate: "0deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-10%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-10%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FFC0CB",
          scaleX: 2,
          scaleY: 1,
          borderRadius: "50% 50% 0% 0%",
          translateX: "0%",
          translateY: "0%",
          rotate: "0deg",
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a tired expression
   * High-intensity and low-intensity versions for a tired emotion.
   */
  expressTired(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#D3D3D3",
          scaleX: 0.9,
          scaleY: 0.9,
          borderRadius: "25%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "35%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "35%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-5%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FFC0CB",
          scaleX: 1,
          scaleY: 1,
          borderRadius: "50% 50% 0% 0%",
          width: "10vmin",
          height: "8vmin",
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#808080",
          scaleX: 0.5,
          scaleY: 0.5,
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "25%",
            rotate: "10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "25%",
            rotate: "-10deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-25%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#D8BFD8",
          scaleX: 1.1,
          scaleY: 1,
          borderRadius: "50% 50% 0% 0%",
          width: "12vmin",
          height: "8vmin",
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of an interested expression
   * High-intensity and low-intensity versions for an interested emotion.
   */
  expressInterested(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: this.leftEye,
          backgroundColor: "#000000",
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "30%",
          translateX: "0%",
          translateY: "0%",
          duration: 1000,
        })
        .add({
          targets: this.rightEye,
          backgroundColor: "#000000",
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "30%",
          translateX: "0%",
          translateY: "0%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid, this.upperRightEyelid],
          translateY: "5%",
          rotate: "0deg",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
          translateY: "-5%",
          rotate: "0deg",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          backgroundColor: "#FFB6C1",
          scaleX: 0.9,
          scaleY: 0.9,
          borderRadius: "0% 0% 50% 50%",
          translateX: "0%",
          translateY: "0%",
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#000000",
          scaleX: 1.5,
          scaleY: 1.5,
          borderRadius: "0%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "25%",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-10%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FF6347",
          scaleX: 1.2,
          scaleY: 1.2,
          width: "12vmin",
          height: "8vmin",
          borderRadius: "0% 0% 50% 50%",
          translateX: "0%",
          translateY: "0%",
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of a sorrow expression
   * High-intensity and low-intensity versions for a sorrow emotion.
   */
  expressSorrow(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#B0C4DE",
          scaleX: 0.9,
          scaleY: 0.9,
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "15%",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-10%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#DDB6C1",
          width: "8vmin",
          height: "6vmin",
          borderRadius: "50% 50% 0% 0%",
          translateY: "5%",
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#708090",
          scaleX: 0.5,
          scaleY: 0.5,
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "25%",
            rotate: "-15deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "25%",
            rotate: "15deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-10%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-10%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#D3A3A3",
          width: "12vmin",
          height: "8vmin",
          borderRadius: "50% 50% 0% 0%",
          scaleX: 1.2,
          scaleY: 1,
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of an excitement expression
   * High-intensity and low-intensity versions for an excitement emotion.
   */
  expressExcitement(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: this.leftEye,
          backgroundColor: "#ADD8E6",
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "20%",
          duration: 1000,
        })
        .add({
          targets: this.rightEye,
          backgroundColor: "#ADD8E6",
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "20%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.upperLeftEyelid, this.upperRightEyelid],
          translateY: "25%",
          duration: 1000,
        }, 0)
        .add({
          targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
          translateY: "-10%",
          duration: 1000,
        }, 0)
        .add({
          targets: this.mouth,
          backgroundColor: "#FFC0CB",
          scaleX: 1.2,
          scaleY: 1.2,
          borderRadius: "0% 0% 50% 50%",
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#40E0D0",
          scaleX: 2,
          scaleY: 2,
          borderRadius: "10%",
          translateY: "-10%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid, this.upperRightEyelid],
            translateY: "50%",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid, this.lowerRightEyelid],
            translateY: "-50%",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FF7F50",
          scaleX: 1.5,
          scaleY: 1,
          borderRadius: "0% 0% 50% 50%",
          width: "18vmin",
          duration: 1000,
        }, 0);
    }
  }

  /**
   * Implementation of an anger expression
   * High-intensity and low-intensity versions for an anger emotion.
   */
  expressAnger(intensity = "low") {
    const timeline = anime.timeline({
      easing: "easeInOutQuad",
      duration: 1000,
    });

    if (intensity === "low") {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#CD5C5C",
          scaleX: 0.9,
          scaleY: 0.9,
          borderRadius: "55%",
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "25%",
            rotate: "2deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "25%",
            rotate: "-2deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-5%",
            rotate: "-2deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-5%",
            rotate: "2deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#FF6347",
          borderRadius: "50% 50% 0% 0%",
          scaleX: 1,
          scaleY: 1,
          duration: 1000,
        }, 0);
    } else {
      timeline
        .add({
          targets: [this.leftEye, this.rightEye],
          backgroundColor: "#8B0000",
          scaleX: 0.8,
          scaleY: 0.8,
          borderRadius: "30%",
          translateX: ["-2%", "2%"],
          duration: 1000,
        })
        .add(
          {
            targets: [this.upperLeftEyelid],
            translateY: "15%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.upperRightEyelid],
            translateY: "15%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerLeftEyelid],
            translateY: "-10%",
            rotate: "-5deg",
            duration: 1000,
          },
          0
        )
        .add(
          {
            targets: [this.lowerRightEyelid],
            translateY: "-10%",
            rotate: "5deg",
            duration: 1000,
          },
          0
        )
        .add({
          targets: this.mouth,
          backgroundColor: "#D2042D",
          width: "12vmin",
          height: "4vmin",
          borderRadius: "50% 50% 0% 0%",
          translateX: "0%",
          translateY: "0%",
          scaleX: 1.2,
          scaleY: 0.8,
          duration: 1000,
        }, 0);
    }
  }
}

/**
 * Initialization of FaceController with specific element selectors.
 */
const face = new FaceController({
  leftEye: document.querySelector(".left.eye"),
  rightEye: document.querySelector(".right.eye"),
  mouth: document.querySelector(".mouth"),
  upperLeftEyelid: document.querySelector(".left .eyelid.upper"),
  upperRightEyelid: document.querySelector(".right .eyelid.upper"),
  lowerLeftEyelid: document.querySelector(".left .eyelid.lower"),
  lowerRightEyelid: document.querySelector(".right .eyelid.lower"),
  face: document.querySelector(".face"),
});

/**
 * Setup Socket.IO client to handle real-time communication with the server.
 * Listens for 'change-expression' and 'execute-expression' events to trigger facial animations.
 */
const socket = io("http://localhost:3001");

/**
 * Handles incoming Socket.IO events to change facial expressions based on server commands.
 * The 'change-expression' event listener switches between different expression commands,
 * activating corresponding animations in the FaceController class.
 *
 * Expected format of choice: "expression" (type: String)
 */
socket.on("change-expression", (choice) => {
  switch (choice) {
    case "breathing":
      // Starts the breathing animation to simulate inhaling and exhaling.
      face.startBreathing();
      break;
    case "listening":
      // Activates the listening expression to give the appearance of attentiveness.
      face.expressListening();
      break;
    /* Intensity-specific endpoints: use "expression:low" or "expression:high" */
    case "happy:low":
      face.expressHappy("low");
      break;
    case "happy:high":
      face.expressHappy("high");
      break;
    case "happy":
      // Triggers the happy expression (default intensity).
      face.expressHappy();
      break;
    case "sad:low":
      face.expressSad("low");
      break;
    case "sad:high":
      face.expressSad("high");
      break;
    case "sad":
      // Triggers the sad expression (default intensity).
      face.expressSad();
      break;
    case "angry:low":
      face.expressAngry("low");
      break;
    case "angry:high":
      face.expressAngry("high");
      break;
    case "angry":
      // Triggers the angry expression (default intensity).
      face.expressAngry();
      break;
    case "surprised:low":
      face.expressSurprised("low");
      break;
    case "surprised:high":
      face.expressSurprised("high");
      break;
    case "surprised":
      // Triggers the surprised expression (default intensity).
      face.expressSurprised();
      break;
    case "stressed:low":
      face.expressStressed("low");
      break;
    case "stressed:high":
      face.expressStressed("high");
      break;
    case "stressed":
      // Triggers the stressed expression (default intensity).
      face.expressStressed();
      break;
    case "calm:low":
      face.expressCalm("low");
      break;
    case "calm:high":
      face.expressCalm("high");
      break;
    case "calm":
      // Triggers the calm expression (default intensity).
      face.expressCalm();
      break;
    case "confused:low":
      face.expressConfused("low");
      break;
    case "confused:high":
      face.expressConfused("high");
      break;
    case "confused":
      // Triggers the confused expression (default intensity).
      face.expressConfused();
      break;
    case "concern:low":
      face.expressConcern("low");
      break;
    case "concern:high":
      face.expressConcern("high");
      break;
    case "concern":
      // Triggers the concern/worried expression (default intensity).
      face.expressConcern();
      break;
    case "fear:low":
      face.expressFear("low");
      break;
    case "fear:high":
      face.expressFear("high");
      break;
    case "fear":
      // Triggers the fear expression (default intensity).
      face.expressFear();
      break;
    case "disgust:low":
      face.expressDisgust("low");
      break;
    case "disgust:high":
      face.expressDisgust("high");
      break;
    case "disgust":
      // Triggers the disgust expression (default intensity).
      face.expressDisgust();
      break;
    case "shocked:low":
      face.expressShocked("low");
      break;
    case "shocked:high":
      face.expressShocked("high");
      break;
    case "shocked":
      face.expressShocked();
      break;
    case "tired:low":
      face.expressTired("low");
      break;
    case "tired:high":
      face.expressTired("high");
      break;
    case "tired":
      face.expressTired();
      break;
    case "interested:low":
      face.expressInterested("low");
      break;
    case "interested:high":
      face.expressInterested("high");
      break;
    case "interested":
      face.expressInterested();
      break;
    case "sorrow:low":
      face.expressSorrow("low");
      break;
    case "sorrow:high":
      face.expressSorrow("high");
      break;
    case "sorrow":
      face.expressSorrow();
      break;
    case "excitement:low":
      face.expressExcitement("low");
      break;
    case "excitement:high":
      face.expressExcitement("high");
      break;
    case "excitement":
      face.expressExcitement();
      break;
    case "anger:low":
      face.expressAnger("low");
      break;
    case "anger:high":
      face.expressAnger("high");
      break;
    case "anger":
      face.expressAnger();
      break;
    case "thinking":
      // Triggers the thinking animation to show a contemplative expression.
      face.expressThinking();
      break;
    case "talking":
      // Initiates talking animation, simulating mouth movements as if speaking.
      face.startTalking();
      break;
    case "blinking":
      // Engages a quick blink to add realism to the eye movements.
      face.startBlinking();
      break;
    case "stopBlinking":
      // Engages a quick blink to add realism to the eye movements.
      face.stopBlinking();
      break;
    case "stopTalking":
      // Resets all facial features to their default state, stopping any active animations.
      face.stopTalking();
      break;
    case "reset":
      // Resets all facial features to their default state, stopping any active animations.
      face.resetToOriginalState();
      break;
    case "wakeup":
      // Triggers the wake-up animation - face transitions from sleeping to fully awake.
      face.wakeUp();
      break;
    case "sleep":
      // Triggers the go-to-sleep animation - face drifts off and fades to black.
      face.goToSleep();
      break;
    default:
      // Logs an error if an unknown expression command is received.
      console.log("Unknown expression command received:", choice);
      break;
  }
});

/**
 * Handles the 'execute-expression' event, which allows for dynamic execution of custom animation scripts.
 * This method receives a piece of JavaScript code as a string, which it attempts to execute.
 * This feature enables on-the-fly customization of facial expressions not predefined in the FaceController.
 *
 * Expected format of data: {"program": "anime.timeline({ easing: 'easeInOutQuad' }).add({ targets: this.leftEye, translateX: '-25%', duration: 500 }).add({ targets: this.rightEye, translateX: '25%', duration: 500 })"}
 * (type: Dict/Object)
 */
socket.on("execute-expression", (data) => {
  const { program } = data;
  try {
    // Attempts to dynamically create and execute a new function based on the received code.
    // The 'face' object is passed to the new function to manipulate facial expressions directly.
    const func = new Function("elements", program);
    func.call(this, face);
  } catch (error) {
    // Logs an error if the execution of the received code fails.
    console.log("Error executing received code:", error);
  }
});
