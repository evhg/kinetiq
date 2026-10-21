import { MotionToggle } from "@/components/motion/MotionToggle";
import { PinnedSequence } from "@/components/PinnedSequence";
import { LazyScene } from "@/components/three/LazyScene";

// Pipeline smoke test. Replaced by the real site once the brief arrives.
export default function Home() {
  return (
    <>
      <header className="site-header">
        <span className="wordmark">KINETIQ</span>
        <MotionToggle />
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <h1 id="hero-title">Pipeline smoke test</h1>
            <p>
              Next.js, GSAP ScrollTrigger, Lenis and a lazy React Three Fiber scene, deployed from
              main to Vercel.
            </p>
          </div>
          <LazyScene
            fallbackSrc="/images/smoke-fallback.svg"
            fallbackAlt="A light grey knot shape, the still version of the 3D test scene"
          />
        </section>

        <PinnedSequence afterId="after-pin" />

        <section id="after-pin" className="after" tabIndex={-1} aria-labelledby="after-title">
          <h2 id="after-title">After the sequence</h2>
          <p>The Skip link lands here. Keyboard focus moves here too.</p>
        </section>
      </main>

      <footer className="site-footer">
        <p>Smoke test build. Not the KINETIQ website yet.</p>
      </footer>
    </>
  );
}
