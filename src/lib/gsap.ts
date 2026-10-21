"use client";

import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { useGSAP } from "@gsap/react";

// Register once, at module level, before any useGSAP call.
gsap.registerPlugin(ScrollTrigger, DrawSVGPlugin, useGSAP);

export { gsap, ScrollTrigger, useGSAP };
