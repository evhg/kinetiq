"use client";

import { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import type { Mesh } from "three";

function SpinningKnot() {
  const ref = useRef<Mesh>(null);
  useFrame((_, delta) => {
    if (!ref.current) return;
    ref.current.rotation.x += delta * 0.25;
    ref.current.rotation.y += delta * 0.4;
  });
  return (
    <Float speed={1.4} rotationIntensity={0.3} floatIntensity={0.6}>
      <mesh ref={ref}>
        <torusKnotGeometry args={[1, 0.32, 160, 24]} />
        <meshStandardMaterial color="#d8d2c4" metalness={0.6} roughness={0.25} />
      </mesh>
    </Float>
  );
}

/**
 * Loaded lazily (ssr: false) by LazyScene. Renders only while on screen
 * and while the tab is visible. R3F disposes geometries and materials
 * declared in JSX when the Canvas unmounts.
 */
export default function SmokeScene() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [onScreen, setOnScreen] = useState(true);
  const [tabVisible, setTabVisible] = useState(true);
  const [maxDpr, setMaxDpr] = useState(2);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time client measurement
    setMaxDpr(window.matchMedia("(max-width: 767px)").matches ? 1.5 : 2);
    const io = new IntersectionObserver(([entry]) => setOnScreen(entry.isIntersecting), {
      rootMargin: "100px",
    });
    if (wrapRef.current) io.observe(wrapRef.current);
    const onVis = () => setTabVisible(document.visibilityState === "visible");
    document.addEventListener("visibilitychange", onVis);
    return () => {
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, []);

  return (
    <div ref={wrapRef} className="scene-canvas">
      <Canvas
        dpr={[1, maxDpr]}
        frameloop={onScreen && tabVisible ? "always" : "never"}
        camera={{ position: [0, 0, 5], fov: 40 }}
        gl={{ antialias: true, powerPreference: "high-performance" }}
        aria-hidden="true"
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[4, 5, 3]} intensity={2.2} />
        <directionalLight position={[-4, -2, -3]} intensity={0.6} color="#c0392b" />
        <SpinningKnot />
      </Canvas>
    </div>
  );
}
