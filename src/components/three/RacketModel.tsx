"use client";

import { useEffect, useMemo } from "react";
import {
  CanvasTexture,
  CylinderGeometry,
  ExtrudeGeometry,
  MeshPhysicalMaterial,
  MeshStandardMaterial,
  Path,
  RepeatWrapping,
  Shape,
  SRGBColorSpace,
} from "three";
import {
  HANDLE,
  HEAD_CURVES,
  HEAD_START,
  HOLE_RADIUS,
  HOLES,
  THICKNESS,
  THROAT_CURVES,
  THROAT_START,
} from "@/lib/racket-shape";

function carbonTexture() {
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d")!;
  const cell = size / 4;
  for (let y = 0; y < 4; y++) {
    for (let x = 0; x < 4; x++) {
      // 2x2 twill: tows alternate direction on a diagonal.
      const horizontal = (x + y) % 2 === 0;
      const g = horizontal
        ? ctx.createLinearGradient(0, y * cell, 0, (y + 1) * cell)
        : ctx.createLinearGradient(x * cell, 0, (x + 1) * cell, 0);
      g.addColorStop(0, "#151517");
      g.addColorStop(0.5, "#46464b");
      g.addColorStop(1, "#151517");
      ctx.fillStyle = g;
      ctx.fillRect(x * cell, y * cell, cell, cell);
    }
  }
  const tex = new CanvasTexture(canvas);
  tex.wrapS = tex.wrapT = RepeatWrapping;
  tex.repeat.set(5, 5);
  tex.colorSpace = SRGBColorSpace;
  tex.anisotropy = 8;
  return tex;
}

export function RacketModel() {
  const { head, handle, grip, faceMat, edgeMat, gripMat } = useMemo(() => {
    const shape = new Shape();
    shape.moveTo(...HEAD_START);
    for (const [a, b, c] of HEAD_CURVES) shape.bezierCurveTo(a[0], a[1], b[0], b[1], c[0], c[1]);
    const throat = new Path();
    throat.moveTo(...THROAT_START);
    for (const [a, b, c] of THROAT_CURVES) throat.bezierCurveTo(a[0], a[1], b[0], b[1], c[0], c[1]);
    shape.holes.push(throat);
    for (const [x, y] of HOLES) {
      const hole = new Path();
      hole.absarc(x, y, HOLE_RADIUS, 0, Math.PI * 2, true);
      shape.holes.push(hole);
    }
    const head = new ExtrudeGeometry(shape, {
      depth: THICKNESS - 0.08,
      bevelEnabled: true,
      bevelThickness: 0.04,
      bevelSize: 0.035,
      bevelSegments: 3,
      curveSegments: 24,
    });
    head.translate(0, 0, -(THICKNESS - 0.08) / 2);

    const handle = new CylinderGeometry(HANDLE.radius * 0.92, HANDLE.radius * 0.92, 0.25, 32);
    handle.translate(0, HANDLE.top - 0.05, 0);
    const grip = new CylinderGeometry(HANDLE.radius, HANDLE.radius * 1.06, HANDLE.length - 0.25, 32);
    grip.translate(0, HANDLE.top - 0.18 - (HANDLE.length - 0.25) / 2, 0);

    const faceMat = new MeshPhysicalMaterial({
      map: carbonTexture(),
      color: "#ffffff",
      roughness: 0.42,
      metalness: 0.25,
      clearcoat: 1,
      clearcoatRoughness: 0.06,
    });
    const edgeMat = new MeshPhysicalMaterial({ color: "#0c0c0d", roughness: 0.3, metalness: 0.4, clearcoat: 1, clearcoatRoughness: 0.1 });
    const gripMat = new MeshStandardMaterial({ color: "#121212", roughness: 0.9 });
    return { head, handle, grip, faceMat, edgeMat, gripMat };
  }, []);

  // Created imperatively, so we dispose them ourselves.
  useEffect(
    () => () => {
      head.dispose();
      handle.dispose();
      grip.dispose();
      faceMat.map?.dispose();
      faceMat.dispose();
      edgeMat.dispose();
      gripMat.dispose();
    },
    [head, handle, grip, faceMat, edgeMat, gripMat],
  );

  return (
    <group>
      <mesh geometry={head} material={[faceMat, edgeMat]} />
      <mesh geometry={handle} material={edgeMat} />
      <mesh geometry={grip} material={gripMat} />
    </group>
  );
}
