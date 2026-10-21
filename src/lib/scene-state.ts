// Mutable state shared between GSAP (DOM side) and the R3F render loop.
// Written by ScrollTrigger/tweens, read every frame. Never put this in React state.
export const heroState = {
  /** 0 → 1: the reveal (rises out of the dark, light comes up). */
  reveal: 0,
  /** 0 → 1: scroll progress through the hero. */
  scroll: 0,
};
