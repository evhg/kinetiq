"use client";

import { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment, Lightformer } from "@react-three/drei";
import type { Group } from "three";
import { MathUtils } from "three";
import { gsap } from "@/lib/gsap";
import { heroState } from "@/lib/scene-state";
import { RacketModel } from "./RacketModel";

function Rig() {
  const group = useRef<Group>(null);

  useFrame((state, delta) => {
    const g = group.current;
    if (!g) return;
    // Frame counter for the check harness (verifies rendering stops off-screen).
    (window as Window & { __heroFrames?: number }).__heroFrames = ((window as Window & { __heroFrames?: number }).__heroFrames ?? 0) + 1;
    const { reveal, scroll } = heroState;
    const t = state.clock.elapsedTime;
    const fine = typeof window !== "undefined" && window.matchMedia("(pointer: fine)").matches;
    const px = fine ? state.pointer.x : 0;
    const py = fine ? state.pointer.y : 0;

    const targetY = (1 - reveal) * -2.4 + Math.sin(t * 0.6) * 0.18 * (1 - scroll) + scroll * 1.6;
    const targetRotY = (1 - reveal) * -2.2 + Math.sin(t * 0.35) * 0.22 + scroll * (Math.PI / 2 + 0.25) + px * 0.25;
    const targetRotX = (1 - reveal) * 0.6 - 0.12 - py * 0.12 + scroll * 0.15;
    const k = 1 - Math.exp(-delta * 6);
    g.position.y = MathUtils.lerp(g.position.y, targetY + 0.7, k);
    g.rotation.y = MathUtils.lerp(g.rotation.y, targetRotY, k);
    g.rotation.x = MathUtils.lerp(g.rotation.x, targetRotX, k);
    g.rotation.z = MathUtils.lerp(g.rotation.z, -0.18 * (1 - scroll), k);
    state.scene.environmentIntensity = 0.15 + reveal * 0.95;

    // Fit the 4.6-unit racket: portrait screens need the camera further back.
    const aspect = state.size.width / state.size.height;
    const z = aspect < 0.6 ? 12.5 : 10.5;
    state.camera.position.z = MathUtils.lerp(state.camera.position.z, z, 0.2);
  });

  return (
    <group ref={group} position={[0, -1.7, 0]}>
      <RacketModel />
    </group>
  );
}

/**
 * Loaded lazily (ssr: false). Renders only while on screen and while the tab
 * is visible. Calls onReady after the first rendered frame so the SVG still
 * underneath can step aside without a blank flash.
 */
export default function HeroScene({ onReady }: { onReady: () => void }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [onScreen, setOnScreen] = useState(true);
  const [tabVisible, setTabVisible] = useState(true);
  const [maxDpr, setMaxDpr] = useState(2);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time client measurement
    setMaxDpr(window.matchMedia("(max-width: 767px)").matches ? 1.5 : 2);
    const io = new IntersectionObserver(([entry]) => setOnScreen(entry.isIntersecting), { rootMargin: "120px" });
    if (wrapRef.current) io.observe(wrapRef.current);
    const onVis = () => setTabVisible(document.visibilityState === "visible");
    document.addEventListener("visibilitychange", onVis);
    // The signature reveal: out of the dark, into the light.
    heroState.reveal = 0;
    const tween = gsap.to(heroState, { reveal: 1, duration: 2.6, ease: "expo.out", delay: 0.15 });
    return () => {
      tween.kill();
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  return (
    <div ref={wrapRef} className="hero-canvas">
      <Canvas
        dpr={[1, maxDpr]}
        frameloop={onScreen && tabVisible ? "always" : "never"}
        camera={{ position: [0, 0, 10], fov: 30 }}
        gl={{ antialias: true, powerPreference: "high-performance", alpha: true }}
        onCreated={() => requestAnimationFrame(() => requestAnimationFrame(onReady))}
        aria-hidden="true"
      >
        <Environment resolution={64} frames={1}>
          <Lightformer form="rect" intensity={4} position={[0, 4, 3]} scale={[10, 1.2, 1]} />
          {/* Broad soft panel behind the camera: the sheen across the carbon face. */}
          <Lightformer form="rect" intensity={1.6} position={[0, 0.5, 9]} scale={[9, 6, 1]} />
          <Lightformer form="rect" intensity={2} position={[-5, 0, 2]} rotation-y={Math.PI / 2} scale={[8, 0.6, 1]} />
          <Lightformer form="rect" intensity={1.4} position={[5, -1, 1]} rotation-y={-Math.PI / 2} scale={[8, 0.4, 1]} />
          <Lightformer form="ring" intensity={1.2} position={[0, 0, -6]} scale={4} />
        </Environment>
        <ambientLight intensity={0.15} />
        <directionalLight position={[-2, 3, 5]} intensity={1.2} />
        <spotLight position={[3, 6, 6]} angle={0.4} penumbra={1} intensity={60} />
        <Rig />
      </Canvas>
    </div>
  );
}
